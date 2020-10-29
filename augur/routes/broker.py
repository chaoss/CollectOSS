#SPDX-License-Identifier: MIT
"""
Creates routes for the broker
"""

import logging
import time
import subprocess
import requests
import json
from flask import request, Response

logger = logging.getLogger(__name__)

# TODO: not this...
def worker_start(worker_name=None):
    process = subprocess.Popen("cd workers/{} && {}_start".format(worker_name,worker_name), shell=True)

def send_task(worker_proxy):

    # Defining local variables for convenience/readability
    user_queue = worker_proxy['user_queue']
    maintain_queue = worker_proxy['maintain_queue']
    worker_id = worker_proxy['id']
    task_endpoint = worker_proxy['location'] + '/AUGWOP/task'

    # Check if worker is alive
    r = requests.get('{}/AUGWOP/heartbeat'.format(
        worker_proxy['location']))
    j = r.json()

    if 'status' not in j:
        logger.error("Worker: {}'s heartbeat did not return a response, setting worker status as 'Disconnected'\n".format(worker_id))
        worker_proxy['status'] = 'Disconnected'
        return

    if j['status'] != 'alive':
        logger.info("Worker: {} is busy, setting its status as so.\n".format(worker_id))
        return

    # Want to check user-created job requests first
    if len(user_queue) > 0:
        new_task = user_queue.pop(0)

    # If no user-created job requests, move on to regulated/maintained ones
    elif len(maintain_queue) > 0:
        new_task = maintain_queue.pop(0)

    else:
        logger.debug("Both queues are empty for worker {}\n".format(worker_id))
        worker_proxy['status'] = 'Idle'
        return

    logger.info("Worker {} is idle, preparing to send the {} task to {}\n".format(worker_id, new_task['display_name'], task_endpoint))
    try:
        requests.post(task_endpoint, json=new_task)
        worker_proxy['status'] = 'Working'
    except:
        logger.error("Sending Worker: {} a task did not return a response, setting worker status as 'Disconnected'\n".format(worker_id))
        worker_proxy['status'] = 'Disconnected'
        # If the worker died, then restart it
        worker_start(worker_id.split('.')[len(worker_id.split('.')) - 2])


def create_routes(server):

    @server.app.route('/{}/task'.format(server.api_version), methods=['POST'])
    def task():
        """ AUGWOP route that is hit when data needs to be added to the database
        Retrieves a json consisting of task specifications that the broker will use to assign a worker
        """
        task = request.json

        given = []
        for given_component in list(task['given'].keys()):
            given.append(given_component)
        model = task['models'][0]
        logger.info("Broker recieved a new user task ... checking for compatible workers for given: " + str(given) + " and model(s): " + str(model) + "\n")

        logger.debug("Broker's list of all workers: {}\n".format(server.broker._getvalue().keys()))

        worker_found = False
        compatible_workers = {}

        # For every worker the broker is aware of that can fill the task's given and model
        for worker_id in [id for id in list(server.broker._getvalue().keys()) if model in server.broker[id]['models'] and given in server.broker[id]['given']]:
            if type(server.broker[worker_id]._getvalue()) != dict:
                continue

            logger.debug("Considering compatible worker: {}\n".format(worker_id))

            # Group workers by type (all gh workers grouped together etc)
            worker_type = worker_id.split('.')[len(worker_id.split('.'))-2]
            compatible_workers[worker_type] = compatible_workers[worker_type] if worker_type in compatible_workers else {'task_load': len(server.broker[worker_id]['user_queue']) + len(server.broker[worker_id]['maintain_queue']), 'worker_id': worker_id}

            # Make worker that is prioritized the one with the smallest sum of task queues
            if (len(server.broker[worker_id]['user_queue']) + len(server.broker[worker_id]['maintain_queue'])) < min([compatible_workers[w]['task_load'] for w in compatible_workers.keys() if worker_type == w]):
                logger.debug("Worker id: {} has the smallest task load encountered so far: {}\n".format(worker_id, len(server.broker[worker_id]['user_queue']) + len(server.broker[worker_id]['maintain_queue'])))
                compatible_workers[worker_type]['task_load'] = len(server.broker[worker_id]['user_queue']) + len(server.broker[worker_id]['maintain_queue'])
                compatible_workers[worker_type]['worker_id'] = worker_id

        for worker_type in compatible_workers.keys():
            worker_id = compatible_workers[worker_type]['worker_id']
            worker = server.broker[worker_id]
            logger.info("Final compatible worker chosen: {} with smallest task load: {} found to work on task: {}\n".format(worker_id, len(server.broker[worker_id]['user_queue']) + len(server.broker[worker_id]['maintain_queue']), task))

            if task['job_type'] == "UPDATE":
                worker['user_queue'].append(task)
                logger.info("Added task for model: {}. New length of worker {}'s user queue: {}\n".format(model, worker_id, str(len(server.broker[worker_id]['user_queue']))))
            elif task['job_type'] == "MAINTAIN":
                worker['maintain_queue'].append(task)
                logger.info("Added task for model: {}. New length of worker {}'s maintain queue: {}\n".format(model, worker_id, str(len(server.broker[worker_id]['maintain_queue']))))

            if worker['status'] == 'Idle':
                send_task(worker)
            worker_found = True
        # Otherwise, let the frontend know that the request can't be served
        if not worker_found:
            logger.warning("Augur does not have knowledge of any workers that are capable of handing the request: {}\n".format(task))

        return Response(response=task,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/workers'.format(server.api_version), methods=['POST'])
    def worker():
        """ AUGWOP route responsible for interpreting HELLO messages
            and telling the broker to add this worker to the set it maintains
        """
        worker = request.json
        logger.info("Recieved HELLO message from worker {} listening on: https://localhost:{}\
                    ".format(worker['id'], worker['id'].split('.')[2]))
        if worker['id'] not in server.broker:
            server.broker[worker['id']] = server.manager.dict()
            server.broker[worker['id']]['id'] = worker['id']
            server.broker[worker['id']]['user_queue'] = server.manager.list()
            server.broker[worker['id']]['maintain_queue'] = server.manager.list()
            server.broker[worker['id']]['given'] = server.manager.list()
            server.broker[worker['id']]['models'] = server.manager.list()
            for given in worker['qualifications'][0]['given']:
                server.broker[worker['id']]['given'].append(given)
            for model in worker['qualifications'][0]['models']:
                server.broker[worker['id']]['models'].append(model)
            server.broker[worker['id']]['status'] = 'Idle'
            server.broker[worker['id']]['location'] = worker['location']
        else:
            logger.info("Worker: {} has been reconnected.\n".format(worker['id']))
            models = server.broker[worker['id']]['models']
            givens = server.broker[worker['id']]['given']
            user_queue = server.broker[worker['id']]['user_queue']
            maintain_queue = server.broker[worker['id']]['maintain_queue']

            time.sleep(10)
            server.broker[worker['id']]['status'] = 'Idle'
            send_task(server.broker[worker['id']])

        return Response(response=worker['id'],
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/completed_task'.format(server.api_version), methods=['POST'])
    def sync_queue():
        task = request.json
        worker = task['worker_id']
        logger.info("Message recieved that worker {} completed task: {}\n".format(worker,task))
        try:
            models = server.broker[worker]['models']
            givens = server.broker[worker]['given']
            user_queue = server.broker[worker]['user_queue']
            maintain_queue = server.broker[worker]['maintain_queue']

            if server.broker[worker]['status'] != 'Disconnected':
                send_task(server.broker[worker])
        except Exception as e:
            logger.error("Ran into error: {}\n".format(repr(e)))
            logger.error("A past instance of the {} worker finished a previous leftover task.\n".format(worker))

        return Response(response=task,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/workers/status'.format(server.api_version), methods=['GET'])
    def get_status():
        all_workers_status = []
        for worker in server.broker.items():
            status = {}
            worker_id = ".".join(worker[0].split('.')[1:])
            status[worker_id] = {}
            status[worker_id]['id'] = worker[1]['id']
            status[worker_id]['user_queue'] = [repo for repo in worker[1]['user_queue']]
            status[worker_id]['maintain_queue'] = [repo for repo in worker[1]['maintain_queue']]
            status[worker_id]['given'] = [given for given in worker[1]['given']]
            status[worker_id]['models'] = [model for model in worker[1]['models']]
            status[worker_id]['status'] = worker[1]['status']
            status[worker_id]['location'] = worker[1]['location']
            all_workers_status.append(status)

        return Response(response=json.dumps(all_workers_status),
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/workers/remove'.format(server.api_version), methods=['POST'])
    def remove_worker():
        worker = request.json
        logger.info("Recieved a message to disconnect worker: {}\n".format(worker))
        server.broker[worker['id']]['status'] = 'Disconnected'
        return Response(response=worker,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/task_error'.format(server.api_version), methods=['POST'])
    def task_error():
        task = request.json
        worker_id = task['worker_id']
        # logger.error("Recieved a message that {} ran into an error on task: {}\n".format(worker_id, task))
        if worker_id in server.broker:
            if server.broker[worker_id]['status'] != 'Disconnected':
                logger.error("{} ran into error while completing task: {}\n".format(worker_id, task))
                send_task(server.broker[worker_id])
        else:
            logger.error("A previous instance of {} ran into error while completing task: {}\n".format(worker_id, task))
        return Response(response=request.json,
                        status=200,
                        mimetype="application/json")