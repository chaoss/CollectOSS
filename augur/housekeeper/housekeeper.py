import logging
import requests
from multiprocessing import Process, Queue
import time
# import schedule
import sqlalchemy as s
import pandas as pd
import os
import zmq

logging.basicConfig(filename='housekeeper.log')
# logging = logging.getlogging(name="housekeeper_logging")


UPDATE_DELAY = 5 #5 sec for testing # 86400 (1 day)

def client_git_url_task(identity, model, git_url):
    """Basic request-reply client using REQ socket."""
    socket = zmq.Context().socket(zmq.REQ)
    socket.identity = u"git-url-client-{}".format(identity).encode("ascii")
    socket.connect("ipc://backend.ipc")
    # socket.connect("tcp://localhost:5558")
    # Send request, get reply
    request = b'UPDATE {"models":[model],"given":{"git_url": git_url}}'
    logging.info("sent request: " + str(request))
    #logging.info(f'{socket.identity.decode("ascii")}: sending {request.decode("ascii")}')
    socket.send(request)
    # reply = socket.recv()
    # logging.info("Reply: " + str(reply))
    #logging.info("{}: {}".format(socket.identity.decode("ascii"), reply.decode("ascii")))

class Housekeeper:

    def __init__(self, user, password, host, port, dbname):

        DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
        )

        dbschema='augur_data'
        self.db = s.create_engine(DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})
        repoUrlSQL = s.sql.text("""
            SELECT repo_git FROM repo
        """)

        rs = pd.read_sql(repoUrlSQL, self.db, params={})

        all_repos = rs['repo_git'].values.tolist()

        # List repo subsections that may have special update requirements
        subsection_test = ['https://github.com/rails/exception_notification.git']
        all_sorted_by_issues = sort_issue_repos()

        # List of tasks that need periodic updates
        self.__updatable = [
            {
                'model': 'issues',
                'started': False,
                'delay': 15,
                'section': subsection_test
            }
        ]
        self.__processes = []

        self.__updater()

    @staticmethod
    def updater_process(model, delay, repos):
        """
        Controls a given plugin's update process

        :param name: name of object to be updated 
        :param delay: time needed to update
        :param shared: shared object that is to also be updated
        """
        logging.info('Spawned {} model updater process with PID {}'.format(model, os.getpid()))
        try:
            while True:
                logging.info('Updating {} model...'.format(model))
                
                # Send task to broker through 0mq
                client_git_url_task('housekeeper', model, repos[0])
                # job = {
                #     "job_type": "MAINTAIN", 
                #     "models": [model], 
                #     "given": {
                #         "git_url": repos[0]
                #     }
                # }

                # requests.post('http://localhost:5000/api/unstable/job', json=job)

                time.sleep(delay)
        except KeyboardInterrupt:
            os._exit(0)
        except:
            raise

    def __updater(self, updates=None):
        """
        Starts update processes
        """
        logging.info("Starting update processes...")
        if updates is None:
            updates = self.__updatable
        for update in updates:
            if update['started'] != True:
                up = Process(target=self.updater_process, args=(update['model'], update['delay'], update['section']), daemon=True)
                up.start()
                self.__processes.append(up)
                update['started'] = True

    def update_all(self):
        """
        Updates all plugins
        """
        for updatable in self.__updatable:
            # logging.info('Updating {} model...'.format(updatable['model']))
            updatable['update']()

    def schedule_updates(self):
        """
        Schedules updates
        """
        # don't use this, 
        logging.debug('Scheduling updates...')
        self.__updater()

    def join_updates(self):
        """
        Join to the update processes
        """
        for process in self.__processes:
            process.join()

    def shutdown_updates(self):
        """
        Ends all running update processes
        """
        for process in self.__processes:
            process.terminate()

    def sort_issue_repos(self):
        
    # def run(self):


    #     # schedule.every(30).days.at("10:30").do(job) #BADGING
    #     # schedule.every().day.at("10:30").do(job) #FACADE?
    #     # schedule.every(7).days.at("10:30").do(job) #ISSUES?

    #     #testing
    #     # schedule.every(2).seconds.do(self.update_model, model="issues")
    #     schedule.every(15).seconds.do(self.update_model, model="badges")

    #     while True:
    #         schedule.run_pending()
    #         time.sleep(1)

    # def update_model(self, model=None):
    #     print("updating model: " + model)

    #     for repo in self.care_about:

    #         job = {
    #             "job_type": "MAINTAIN", 
    #             "models": [model], 
    #             "given": {
    #                 "git_url": repo
    #             }
    #         }

    #         requests.post('http://localhost:5000/api/job', json=job)



