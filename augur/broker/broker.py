import requests
from multiprocessing import Process, Queue, Manager

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
        worker_manager = Manager()
        self.id = id
        self.location = location
        self.qualifications = qualifications
        if qualifications is not None:
            self.given = qualifications[0]['given'][0][0]
            self.models = qualifications[0]['models']
        self.user_queue = worker_manager.Queue()
        self.maintain_queue = worker_manager.Queue()
        self.status = "Idle"

    def as_dict(self):
        return {
            'id': self.id, 'location': self.location,
            'given': self.given, 'models': self.models, 'status': self.status,
            'user_queue': self.user_queue, 'maintain_queue': self.maintain_queue
        }

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
        manager = Manager()
        self.num_workers = 1
        self.connected_workers = manager.dict()
        self.created_jobs = []
        logging.info("Broker spawned and is ready to accept tasks.")
        
        self.listen_process = multiprocessing.Process(target=self.main, args=(self.connected_workers,))
        self.listen_process.daemon = True
        self.listen_process.start()
        
        

    def add_new_worker(self, worker, connected_workers):
        """ Method to add a new worker to the set of workers the broker is managing
        """
        logging.info("Adding worker to connected worker list.\n")
        worker_dict = Worker(worker['id'], location=worker['location'], qualifications=worker['qualifications']).as_dict()
        # self.connected_workers[worker_dict['id']] = self.manager.dict()
        connected_workers[worker_dict['id']] = worker_dict
        

    def create_job(self, job_received, connected_workers):
        """ Method to add a job to the brokers set of maintained jobs and find compatible workers for it
        Hits compatible workers' AUGWOP endpoints that adds the job to their queues
        """
        # self.created_jobs.append(Job(job_type=job['job_type'], models=job['models'], given=job["given"]))

        # job = Job(job_type=job_received['job_type'], models=job_received['models'], given=job_received["given"])
        # for job in self.created_jobs:
        given = list(job_received['given'].keys())[0]
        model = job_received['models'][0]
        logging.info("Checking for compatible workers for given: " + str(given) + " and model(s): " + str(model) + "")
        logging.info("Connected workers: " + str(connected_workers.copy()))
        logging.info("Connected workers keys: " + str(connected_workers.copy().keys()))
        logging.info("Connected workers values: " + str(connected_workers.copy().values()))


        compatible_workers = [worker for worker in connected_workers.copy().values() if worker.given == given and model in worker.models]
        logging.info("Found compatible workers: " + str(compatible_workers))
        if compatible_workers is not None:
            for worker in compatible_workers:

                if job_received['job_type'] == "UPDATE":
                    connected_workers[worker.id].user_queue.put(job_received)
                    connected_workers[worker.id].status = "Updating tasks"
                elif job_received['job_type'] == "MAINTAIN":
                    connected_workers[worker.id].maintain_queue.put(job_received)
                    connected_workers[worker.id].status = "Updating tasks"


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

    def get_status(self, worker_id):
        return self.connected_workers[worker_id].status

    def main(self, connected_workers):
        """Load balancer main loop."""

        # Prepare context and sockets
        context = zmq.Context.instance()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind("ipc://frontend.ipc")
        backend = context.socket(zmq.ROUTER)
        backend.bind("ipc://backend.ipc")

        # Initialize main loop state
        count = NBR_CLIENTS
        poller = zmq.Poller()

        # Only poll for requests from backend 
        poller.register(backend, zmq.POLLIN)

        try:
        
            while True:

                # Identify the worker and the client
                logging.info("Broker is waiting for a new message...\n")
                client_id = backend.recv().decode('ascii')
                logging.info("Broker recieved a new message.\n")
                logging.info("Message sender: " + str(client_id) + "\n")
                request = backend.recv_multipart()

                delimiter = request[0]
                client = request[1]

                # parse the message
                message = request[len(request) - 1].decode('ascii').split(" ")

                logging.info("Message: " + str(request) + "\n")

                action = message[0]
                try:
                    job_received = json.loads(message[1])
                    logging.info(job_received)

                    # If the client's message is UPDATE, it is a message to maintain a model 
                    #   from the housekeeper or update from frontend
                    if action == "UPDATE" or action == "MAINTAIN":
                        self.create_job(job_received, connected_workers)

                except Exception as e:
                    logging.info("Invalid or problematic task: " + str(message))
                    logging.info("Error encountered: " + str(e) + "\n")
                    job_received = None

        except KeyboardInterrupt:
            self.listen_process.terminate()
        except:
            raise
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

