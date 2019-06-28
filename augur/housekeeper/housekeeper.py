import logging
import requests
from multiprocessing import Process, Queue
import time
# import schedule
import sqlalchemy as s
import pandas as pd
import os
import zmq
import json

logging.basicConfig(filename='housekeeper.log', filemode='w', level=logging.INFO)


UPDATE_DELAY = 5 #5 sec for testing # 86400 (1 day)

def client_git_url_task(identity, model, git_url):
    """Basic request-reply client using REQ socket."""
    socket = zmq.Context().socket(zmq.REQ)
    socket.identity = u"git-url-client-{}-{}".format(identity, os.getpid()).encode("ascii")
    socket.connect("ipc://backend.ipc")

    # Send request, get reply
    request = b'UPDATE {"models":["%s"],"given":{"git_url":"%s"}}' % (model.encode(), git_url.encode())
    logging.info("Sent request: " + str(request) + "\n")
    socket.send(request)

class Housekeeper:

    def __init__(self, user, password, host, port, dbname):

        DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
        )

        dbschema='augur_data'
        self.db = s.create_engine(DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        repoUrlSQL = s.sql.text("""
            SELECT repo_git FROM repo
        """)

        rs = pd.read_sql(repoUrlSQL, self.db, params={})

        all_repos = rs['repo_git'].values.tolist()

        # List repo subsections that may have special update requirements
        subsection_test = ['https://github.com/rails/exception_notification.git']
        all_repo_issues_sorted = self.sort_issue_repos()['repo_git'].values#.tolist()

        # List of jobs that need periodic updates
        self.__updatable = [
            {
                'model': 'issues',
                'started': False,
                'delay': 15000,
                'section': all_repo_issues_sorted,
                'tag': 'All stored repositories'
            }
        ]
        self.__processes = []

        self.__updater()
        

    @staticmethod
    def updater_process(model, delay, repos, tag):
        """
        Controls a given plugin's update process

        :param name: name of object to be updated 
        :param delay: time needed to update
        :param shared: shared object that is to also be updated
        """
        logging.info('Housekeeper spawned {} model updater process with PID {} for subsection {}'.format(
            model, os.getpid(), tag))
        try:
            while True:
                logging.info('Housekeeper preparing to send update request(s) for {} model for subsection {}...'.format(model, tag))
                
                # Send task to broker through 0mq
                for repo in repos:
                    client_git_url_task('housekeeper', model, repo)
                    time.sleep(15)

                time.sleep(delay)
        except KeyboardInterrupt:
            self.shutdown_updates()
            os.kill(os.getpid(), 9)
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
                update['started'] = True
                up = Process(target=self.updater_process, args=(update['model'], update['delay'], update['section'], update['tag']), daemon=True)
                up.start()
                self.__processes.append(up)
                update['started'] = True

    def update_all(self):
        """
        Updates all plugins
        """
        for updatable in self.__updatable:
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
        # Query all repos and last repo id
        repoUrlSQL = s.sql.text("""
            SELECT repo_git, repo_id FROM repo ORDER BY repo_id ASC
            """)

        rs = pd.read_sql(repoUrlSQL, self.db, params={})

        repoIdSQL = s.sql.text("""
            SELECT since_id_str FROM gh_worker_job
            """)

        df = pd.read_sql(repoIdSQL, self.helper_db, params={})
        last_id = int(df.iloc[0]['since_id_str'])
        before_repos = rs.loc[rs['repo_id'].astype(int) <= last_id]
        after_repos = rs.loc[rs['repo_id'].astype(int) > last_id]

        reorganized_repos = after_repos.append(before_repos)
        return reorganized_repos
        
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



