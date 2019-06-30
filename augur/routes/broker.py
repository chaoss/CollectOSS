#SPDX-License-Identifier: MIT
"""
Creates routes for the broker
"""
from flask import request, jsonify, Response
import logging
import json
import requests

def create_broker_routes(server):

    @server.app.route('/{}/task'.format(server.api_version), methods=['POST'])
    def task():
        """ AUGWOP route that is hit when data needs to be added to the database
        Retrieves a json consisting of task specifications that the broker will use to assign a worker
        """
        task = request.json

        given = list(task['given'].keys())[0]
        model = task['models'][0]
        if task['job_type'] != 'MAINTAIN':
            logging.info("Broker recieved a new user task ... checking for compatible workers for given: " + str(given) + " and model(s): " + str(model) + "")

        worker_found = False
        for worker in list(server.broker._getvalue().keys()):
            models = server.broker[worker]['models']
            givens = server.broker[worker]['given']
            user_queue = server.broker[worker]['user_queue']
            maintain_queue = server.broker[worker]['maintain_queue']

            if model in models and given in givens:
                if task['job_type'] == "UPDATE":
                    server.broker[worker]['user_queue'].append(task)
                    logging.info("New length of worker {}'s user queue: {}".format(worker, str(len(server.broker[worker]['user_queue']))))
                elif task['job_type'] == "MAINTAIN":
                    server.broker[worker]['maintain_queue'].append(task)
                    # logging.info("New length of worker {}'s maintain queue: {}".format(worker, str(len(server.broker[worker]['maintain_queue']))))

                if server.broker[worker]['status'] == 'Idle':
                    if len(user_queue) > 0:
                        new_task = user_queue.pop(0)
                        logging.info("Worker {} is idle, preparing to send the {} task to {}".format(worker, new_task['given']['git_url'], str(server.broker[worker]['location'])))
                        requests.post(server.broker[worker]['location'] + '/AUGWOP/task', json=new_task)
                        server.broker[worker]['status'] = 'Working'
                    elif len(maintain_queue) > 0:
                        new_task = maintain_queue.pop(0)
                        # logging.info("Worker {} is idle, preparing to send the {} task to {}".format(worker, new_task['given']['git_url'], str(server.broker[worker]['location'])))
                        requests.post(server.broker[worker]['location'] + '/AUGWOP/task', json=new_task)
                        server.broker[worker]['status'] = 'Working'
                    else:
                        logging.info("Both queues are empty for worker {} and it is idle".format(worker))
                worker_found = True
        # Otherwise, let the frontend know that the request can't be served
        if not worker_found:
            logging.info(f"Augur does not have knowledge of any workers that are capable of handing the request: " + str(task))

        return Response(response=task,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/workers'.format(server.api_version), methods=['POST'])
    def worker():
        """ AUGWOP route responsible for interpreting HELLO messages
            and telling the broker to add this worker to the set it maintains
        """
        worker = request.json
        logging.info("Recieved HELLO message from worker: " + worker['id'])
        server.broker[worker['id']] = server.manager.dict()
        server.broker[worker['id']]['user_queue'] = server.manager.list()
        server.broker[worker['id']]['maintain_queue'] = server.manager.list()
        server.broker[worker['id']]['given'] = server.manager.list()
        server.broker[worker['id']]['models'] = server.manager.list()
        server.broker[worker['id']]['given'].append(worker['qualifications'][0]['given'][0][0])
        server.broker[worker['id']]['models'].append(worker['qualifications'][0]['models'][0])
        server.broker[worker['id']]['status'] = 'Idle'
        server.broker[worker['id']]['location'] = worker['location']

        return Response(response=worker['id'],
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/completed_task'.format(server.api_version), methods=['POST'])
    def sync_queue():
        task = request.json
        worker = task['worker_id']
        logging.info("Message recieved that worker " + worker + " completed task: " + str(task))
        models = server.broker[worker]['models']
        givens = server.broker[worker]['given']
        user_queue = server.broker[worker]['user_queue']
        maintain_queue = server.broker[worker]['maintain_queue']

        try:
            new_task = user_queue.pop(0)
            logging.info("Worker {}'s user queue is not empty, preparing to send it the next 'user' task: {}".format(worker, new_task['given']['git_url']))
            logging.info("Remaining length of user queue: {}".format(str(len(user_queue))))
            requests.post(server.broker[worker]['location'] + '/AUGWOP/task', json=new_task)
        except:
            try:
                new_task = maintain_queue.pop(0)
                logging.info("Worker {}'s user queue is empty but the maintain queue is not, preparing to send it the next 'maintain' task: {}".format(worker, new_task['given']['git_url']))
                logging.info("Remaining length of maintain queue: {}".format(str(len(maintain_queue))))
                requests.post(server.broker[worker]['location'] + '/AUGWOP/task', json=new_task)
            except:
                logging.info("Both queues are empty for worker {}".format(worker))
                server.broker[worker]['status'] = 'Idle'

        return Response(response=task,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/workers/status'.format(server.api_version), methods=['GET'])
    def get_status():
        status = {}
        for worker in list(server.broker._getvalue().keys()):
            status[worker] = worker
            status[worker]['user_queue'] = server.broker[worker]['user_queue']._getvalue()
            status[worker]['maintain_queue'] = server.broker[worker]['maintain_queue']._getvalue()

        return Response(response=status,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/workers/remove'.format(server.api_version), methods=['POST'])
    def remove_worker():
        worker = request.json
        del server.broker[worker['id']]
        return Response(response=worker,
                        status=200,
                        mimetype="application/json")