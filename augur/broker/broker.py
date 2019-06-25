import requests
from multiprocessing import Process, Queue

import json
import random
import sys
import time

import click
import zmq
import multiprocessing

import logging
logging.basicConfig(filename='broker.log', filemode='w', level=logging.INFO)

# from multichannel.worker_tasks import deep_github_worker_task, github_worker_task, facade_worker_task
# from multichannel.client_tasks import client_owner_repo_task, client_git_url_task
NBR_WORKERS = 1
NBR_CLIENTS = 1

class Worker():
    """Workers collect data from data sources, normalize the data into our schema, and update the database. 
    When workers connect, they advertise what kind of work they can accept using a specification as detailed above. 
    Workers with the same ID (i.e. of the same type) share a job queue. 
    When workers with different IDs can accept the same job, each of those workers will be assigned a copy of the job.
    Workers are language agnostic: so long as they can connect to the broker and to the database, they’re good to go.
    
    ID: what the broker will be able to reference a worker as
    location: the url of the server a worker is working on
    qualifications: consists of the given and model a worker is able to provide data about
    """
    def __init__(self, id, location=None, qualifications=None):
        self.id = id
        self.location = location
        self.qualifications = qualifications
        if qualifications is not None:
            self.given = qualifications[0]['given'][0][0]
            self.models = qualifications[0]['models']
        self.user_queue = Queue()
        self.maintain_queue = Queue()

class Job():
    """ Defines the instructions to give to a worker about the data needed to be inserted in our database
    
    job_type: type of action worker should take in reference to models and given
    models: references a sector of data that the worker is able to provide
    given: what the worker is given and is able to provide data about
    """
    def __init__(self, job_type, models, given):
        self.job_type = job_type
        self.models = models
        self.given = given

class Broker(object):
    """The broker is responsible for queuing and distributing requests to workers. 
    These requests come from the server and are for data that is to be used in the calculation of a metric. 

    A worker provides data from a singular data source: each worker that 
        provides data from the same data source is of the same “type.” 
    
    Each type of worker gets their own queue, and workers compete against other workers of 
        their own type (competing consumers) to fulfill jobs on that queue. 
    """
    
    def __init__(self):
        """ Initialize the broker's maintained sets of connected workers and created jobs
        """
        # self.NBR_CLIENTS = 1
        self.num_workers = 1
        self.connected_workers = {}
        self.created_jobs = []
        logging.info("Broker spawned and is ready to accept tasks.")
        process = multiprocessing.Process(target=self.main)
        process.daemon = True
        process.start()
        

    def add_new_worker(self, worker):
        """ Method to add a new worker to the set of workers the broker is managing
        """
        self.connected_workers[worker['id']] = (Worker(id=worker['id'], location=worker['location'], qualifications=worker['qualifications']))
        

    def create_job(self, job_received):
        """ Method to add a job to the brokers set of maintained jobs and find compatible workers for it
        Hits compatible workers' AUGWOP endpoints that adds the job to their queues
        """
        # self.created_jobs.append(Job(job_type=job['job_type'], models=job['models'], given=job["given"]))

        # job = Job(job_type=job_received['job_type'], models=job_received['models'], given=job_received["given"])
        # for job in self.created_jobs:
        given = list(job_received['given'].keys())[0]
        model = job_received['models'][0]
        # print(self.connected_workers)
        # print(model in self.connected_workers['com.augurlabs.core.github_worker'].models, model, worker.models)
        compatible_workers = [worker for worker in self.connected_workers.values() if worker.given == given and model in worker.models]

        if compatible_workers is not None:
            for worker in compatible_workers:

                if job_received['job_type'] == "UPDATE":
                    self.connected_workers[worker.id].user_queue.put(job_received)
                elif job_received['job_type'] == "MAINTAIN":
                    self.connected_workers[worker.id].maintain_queue.put(job_received)

                print(worker.id + "'s queue after adding the job: ")
                print(dump_queue(self.connected_workers[worker.id].queue))

                requests.post(worker.location + '/AUGWOP/task', json=job_received)
        # Otherwise, let the frontend know that the request can't be served
        else:
            logging.info(f"Augur does not have knowledge of any workers that are capable of handing the request: " + str(job_received) + ". \nPlease install a worker that can serve requests given `{given}`")
            # frontend.send_multipart([client, b"", b"NO-WORKERS"])

    def completed_job(self, job):
        if job['action'] == "UPDATE":
            completed_job = self.connected_workers[job['worker_id']].user_queue.get()
        elif job['action'] == "MAINTAIN":
            completed_job = self.connected_workers[job['worker_id']].maintain_queue.get()
        logging.info("Popped off broker's worker's queue the job: " + str(completed_job))

    def main(self):
        """Load balancer main loop."""

        # Prepare context and sockets
        context = zmq.Context.instance()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind("ipc://frontend.ipc")
        backend = context.socket(zmq.ROUTER)
        backend.bind("ipc://backend.ipc")
        # backend.bind("tcp://*:5558")
        print("hi")

        # Initialize main loop state
        count = NBR_CLIENTS
        # workers = []
        # jobs = {}
        # client_job_ids = {}
        poller = zmq.Poller()

        # Only poll for requests from backend 
        poller.register(backend, zmq.POLLIN)
        
        while True:
            # Identify which sockets have activity
            # sockets = dict(poller.poll(1000))
            # logging.info("about to start" + str(sockets))

            # if sockets:
            #     # If the backend is the one that has activity
            #     if backend in sockets:

            # Identify the worker and the client
            logging.info("Broker is waiting for a new message...\n")
            client_id = backend.recv().decode('ascii')
            logging.info("Broker recieved a new message.\n")
            logging.info("Message sender: " + str(client_id))
            request = backend.recv_multipart()
            logging.info("Message request: " + str(request))

            # worker, delimiter, client = request[:3]
            delimiter = request[0]
            client = request[1]
            # parse the message
            message = request[len(request) - 1].decode('ascii').split(" ")

            # delimiter = request[0].decode('ascii')#.split(" ")
            logging.info("Parsed message: " + str(message))
            action = message[0]
            logging.info("messsage:" + str(message[1]))
            print("printed", message, type(message[1]))
            try:
                job_received = json.loads(message[1])
            



                # logging.info("Client: " + str(client))

                # If there are no workers currently available
                # if not workers:
                    #listen on the frontend now that a worker is available (we just found one above)
                    # poller.register(frontend, zmq.POLLIN)


                # If the client's message is UPDATE, it is a message to maintain a model 
                #   from the housekeeper or update from frontend
                if action == "UPDATE" or action == "MAINTAIN":
                    # job_received['action'] = action
                    self.create_job(job_received)
                    # Send to the client that made the request the contents of the reply 
                    # backend.send_multipart([client, b"", reply])


                # # If the client's message is not READY and there are more than 3 parts to it, then that mean's a reply to a request
                # if client != b"READY" and len(request) > 3:
                #     # Identify the reply
                #     delimiter, reply = request[3:]

                #     if 'DONE' == reply.decode('ascii'):
                #         job_items = list(jobs.items())
                #         job_id = next(job[0] for job in job_items if worker.decode('ascii') in list(job[1].keys()))

                #         self.connected_workers[job['worker_id']].queue.get()

                #         if len([job for job in jobs[job_id].values()]) == len([job for job in jobs[job_id].values() if job == 'complete']):
                #             logging.info(f"Job {job_id} is finished")
                #             frontend.send_multipart([client_job_ids[job_id], b"", b"DONE"])
                #         else:
                #             logging.info(f"Job {job_id} is still in progress")

                    # # Send to the client that made the request the contents of the reply 
                    # frontend.send_multipart([client, b"", reply])

                    # # Note that one of the requests has been served
                    # count -= 1

                    # # If there are no more requests to be served, terminate
                    # if not count:
                    #     break



            # If there's activity on the frontend
            # if frontend in sockets:
            #     # Get next client request
            #     msg = frontend.recv_multipart()
            #     client = msg[0]
            #     delimiter = msg[1]
            #     request = msg[2]

            #     # Identify given from request
            #     given = list(json.loads((request.decode('ascii')).split(" ")[1])['given'])[0]

            #     # Find workers that can process that given
            #     compatible_workers = [worker for worker in workers if worker.given[1] == given]

            #     # If any exist, give each one a copy of the request
            #     if workers is not None:
            #         job_id = random.randint(0, 100)
            #         jobs[job_id] = {}
            #         client_job_ids[job_id] = client
            #         logging.info(f"Created job {job_id} for {client.decode('ascii')}")
            #         for worker in compatible_workers:
            #             # Send to the backend the worker to use, which client requested, and the message from the client
            #             #logging.info(f"{request.decode('ascii')} is being routed to {worker.ID.decode('ascii')}")
            #             backend.send_multipart([worker.ID, b"", client, b"", request])

            #             # Add the job to the list of current jobs
            #             jobs[job_id][worker.ID.decode('ascii')] = 'working'

            #     # Otherwise, let the frontend know that the request can't be served
            #     else:
            #         logging.warning(f"Augur does not have knowledge of any workers that are capable of handing the request {request.decode('ascii')}. \nPlease install a worker that can serve requests given `{given}`")
            #         frontend.send_multipart([client, b"", b"NO-WORKERS"])
            #     # else:
            #     #     logging.info("TIMEOUT")
            except Exception as e:
                logging.info(str(e))
                logging.info(str(message))
                job_received = None

        # Clean up
        backend.close()
        frontend.close()
        context.term()

def dump_queue(queue):
    """
    Empties all pending items in a queue and returns them in a list.
    """
    result = []
    queue.put("STOP")

    for i in iter(queue.get, 'STOP'):
        result.append(i)
    # time.sleep(.1)
    return result

