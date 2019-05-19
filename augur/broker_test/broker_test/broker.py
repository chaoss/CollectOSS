import logging
import requests
logging.basicConfig(filename='logs/server.log')
logger = logging.getLogger(name="broker_logger")

class Worker():
    """docstring for Worker"""
    def __init__(self, ID, location, qualifications):
        self.ID = ID
        self.location = location
        self.qualifications = qualifications
        self.given = qualifications[0]['given'][0][0]
        print("Worker given: " + self.given)

class Job():
    """docstring for Job"""
    def __init__(self, job_type, models, given):
        self.job_type = job_type
        self.models = models
        self.given = given

class Broker(object):
    """docstring for Broker"""
    def __init__(self):
        self.connected_workers = []
        self.created_jobs = []

    def add_new_worker(self, worker):
        self.connected_workers.append(Worker(ID=worker['id'], location=worker['location'], qualifications=worker['qualifications']))

    def create_job(self, job):
        self.created_jobs.append(Job(job_type=job['job_type'], models=job['models'], given=job["given"]))

        for job in self.created_jobs:
            job_given = list(job.given.keys())[0]
            compatible_workers = [worker for worker in self.connected_workers if worker.given == job_given]

            for worker in compatible_workers:
                task = {'task': job.given}
                requests.post(worker.location + '/AUGWOP/task', json=task)



