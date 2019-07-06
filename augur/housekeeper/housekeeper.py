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

    def __init__(self, broker, broker_port, user, password, host, port, dbname):

        self.broker_port = broker_port
        self.broker = broker
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
        example_subsection = [
                {
                    'repo_git': 'https://github.com/rails/exception_notification.git', 
                    'focused_task': '0' # OPTIONAL KEY, '1' if you want an in-depth 'crawl' of github's api for the repo, 
                                        #    will cause unnecessary api calls and will take longer
                }
            ]
        all_sorted_by_issues = self.sort_issue_repos()

        # List of tasks that need periodic updates
        self.__updatable = [
            {
                'model': 'issues',
                'started': False,
                'delay': 150000,
                'section': all_sorted_by_issues,
                'tag': 'All repositories'
            }
        ]
        self.__processes = []
        # logging.info("HK pid: {}".format(str(os.getpid())))
        self.__updater()

    @staticmethod
    def updater_process(broker_port, broker, model, started, delay, section, tag):
        """
        Controls a given plugin's update process
        :param name: name of object to be updated 
        :param delay: time needed to update
        :param shared: shared object that is to also be updated
        """
        logging.info('Housekeeper spawned {} model updater process for subsection {} with PID {}'.format(model, tag, os.getpid()))
        try:
            # Waiting for 1 alive worker
            while True:
                if broker is not None:
                    if len(broker._getvalue().keys()) > 1:
                        logging.info("Housekeeper recognized that the broker has at least one worker... beginning to distribute maintained tasks")
                        time.sleep(10)
                        while True:
                            logging.info('Housekeeper updating {} model for subsection: {}...'.format(model, tag))
                            
                            for repo in section:
                                task = {
                                    "job_type": "MAINTAIN", 
                                    "models": [model], 
                                    "given": {
                                        "git_url": repo['repo_git']
                                    }
                                }
                                if "focused_task" in repo:
                                    task["focused_task"] = repo['focused_task']
                                try:
                                    requests.post('http://localhost:{}/api/unstable/task'.format(
                                        broker_port), json=task, timeout=10)
                                except Exception as e:
                                    logging.info(str(e))

                                time.sleep(2.5)
                            logging.info("Housekeeper finished sending {} tasks to the broker for it to distribute to your worker(s)".format(str(len(section))))
                            time.sleep(delay)
                        break
                time.sleep(3)

                
        except KeyboardInterrupt:
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
                up = Process(target=self.updater_process, args=(self.broker_port, self.broker, update['model'], 
                    update['started'], update['delay'], update['section'], update['tag']), daemon=True)
                up.start()
                self.__processes.append(up)
                # logging.info("HK processes: {}".format(str(self.__processes[0].pid)))
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

        # Query all repos and last repo id
        repoUrlSQL = s.sql.text("""
                SELECT repo_git, repo_id FROM repo ORDER BY repo_id ASC
            """)

        rs = pd.read_sql(repoUrlSQL, self.db, params={})

        repoIdSQL = s.sql.text("""
                SELECT since_id_str FROM gh_worker_job
            """)

        job_df = pd.read_sql(repoIdSQL, self.helper_db, params={})

        last_id = int(job_df.iloc[0]['since_id_str'])

        jobHistorySQL = s.sql.text("""
                SELECT max(history_id) AS history_id, status FROM gh_worker_history
                GROUP BY status
                LIMIT 1
            """)

        history_df = pd.read_sql(jobHistorySQL, self.helper_db, params={})

        finishing_task = False
        if len(history_df.index) != 0:
            if history_df.iloc[0]['status'] == 'Stopped':
                self.history_id = int(history_df.iloc[0]['history_id'])
                finishing_task = True
                last_id += 1 #update to match history tuple val rather than just increment
            

        # Rearrange repos so the one after the last one that 
        #   was completed will be ran first
        before_repos = rs.loc[rs['repo_id'].astype(int) < last_id]
        after_repos = rs.loc[rs['repo_id'].astype(int) >= last_id]

        reorganized_repos = after_repos.append(before_repos)

        reorganized_repos['focused_task'] = 0
        reorganized_repos = reorganized_repos.to_dict('records')
        
        if finishing_task:
            reorganized_repos[0]['focused_task'] = 1

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
