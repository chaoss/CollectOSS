import logging
import requests
from multiprocessing import Process, Queue
logging.basicConfig(filename='logs/server.log')
logger = logging.getLogger(name="broker_logger")

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
    def __init__(self, id, location, qualifications):
        self.id = id
        self.location = location
        self.qualifications = qualifications
        self.given = qualifications[0]['given'][0][0]
        self.models = qualifications[0]['models']
        print("Worker given: " + self.id)
        self.queue = Queue()

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
        self.connected_workers = {}
        self.created_jobs = []

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
        print(self.connected_workers)
        # print(model in self.connected_workers['com.augurlabs.core.github_worker'].models, model, worker.models)
        compatible_workers = [worker for worker in self.connected_workers.values() if worker.given == given and model in worker.models]

        for worker in compatible_workers:

            """ PRIORITY KEY:
                0 - user/endpoint created job ("UPDATE" job type)
                1 - a maintained job created by the housekeeper ("MAINTAIN" job type)
            """

            if job_received['job_type'] == "UPDATE":
                self.connected_workers[worker.id].queue.put(job_received)
            elif job_received['job_type'] == "MAINTAIN":
                self.connected_workers[worker.id].queue.put(job_received)

            print(worker.id + "'s queue after adding the job: ")
            print(dump_queue(self.connected_workers[worker.id].queue))

            requests.post(worker.location + '/AUGWOP/task', json=job_received)

    def completed_job(self, job):
        print("Job completed: ", completed_job, job)
        completed_job = self.connected_workers[job['worker_id']].queue.get()
        print("Job completed: ", completed_job, job)

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

