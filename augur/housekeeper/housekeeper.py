import logging
import requests
from multiprocessing import Process, Queue
import time
import sqlalchemy as s
import pandas as pd
import os
import json
logging.basicConfig(filename='housekeeper.log')

class Housekeeper:

    def __init__(self, jobs, broker, broker_host, broker_port, user, password, host, port, dbname):

        self.broker_host = broker_host
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

        # List of tasks that need periodic updates
        self.__updatable = self.prep_jobs(jobs)

        self.__processes = []
        self.__updater()

    @staticmethod
    def updater_process(broker_host, broker_port, broker, model, given, delay, repos, repo_group_id=None):
        """
        Controls a given plugin's update process
        :param name: name of object to be updated 
        :param delay: time needed to update
        :param shared: shared object that is to also be updated
        """
        if repo_group_id:
            logging.info('Housekeeper spawned {} model updater process for subsection {} with PID {}'.format(model, repo_group_id, os.getpid()))
        else:
            logging.info('Housekeeper spawned {} model updater process for repo {} with PID {}'.format(model, repos[0]['repo_id'], os.getpid()))

        try:
            compatible_worker_found = False
            # Waiting for compatible worker
            while True:
                for worker in list(broker._getvalue().keys()):
                    # logging.info("{} {} {} {} {}".format(worker, model, broker[worker]['models'], given, broker[worker]['given']))
                    if model in broker[worker]['models'] and given in broker[worker]['given']:
                        compatible_worker_found = True
                if compatible_worker_found:
                    logging.info("Housekeeper recognized that the broker has a worker that " + 
                        "can handle the {} model... beginning to distribute maintained tasks".format(model))
                    time.sleep(4)
                    while True:
                        logging.info('Housekeeper updating {} model with given {}...'.format(
                            model, given[0]))
                        
                        if given[0] == 'git_url' or given[0] == 'github_url':
                            for repo in repos:
                                if given[0] == 'github_url' and 'github' not in repo['repo_git']:
                                    continue
                                given_key = 'git_url' if given[0] == 'git_url' else 'github_url'
                                task = {
                                    "job_type": "MAINTAIN", 
                                    "models": [model], 
                                    "display_name": "{} model for url: {}".format(model, repo['repo_git']),
                                    "given": {}
                                }
                                task['given'][given_key] = repo['repo_git']
                                if "focused_task" in repo:
                                    task["focused_task"] = repo['focused_task']
                                try:
                                    requests.post('http://{}:{}/api/unstable/task'.format(
                                        broker_host,broker_port), json=task, timeout=10)
                                except Exception as e:
                                    logging.info("Error encountered: {}".format(e))

                                time.sleep(0.5)
                        elif given[0] == 'repo_group':
                            task = {
                                    "job_type": "MAINTAIN", 
                                    "models": [model], 
                                    "display_name": "{} model for repo group id: {}".format(model, repo_group_id),
                                    "given": {
                                        "repo_group": repos
                                    }
                                }
                            try:
                                requests.post('http://{}:{}/api/unstable/task'.format(
                                    broker_host,broker_port), json=task, timeout=10)
                            except Exception as e:
                                logging.info("Error encountered: {}".format(e))

                        logging.info("Housekeeper finished sending {} tasks to the broker for it to distribute to your worker(s)".format(len(repos)))
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
            up = Process(target=self.updater_process, args=(self.broker_host,self.broker_port, self.broker, update['model'], 
                update['given'], update['delay'], update['repos'], update['repo_group_id']), daemon=True)
            up.start()
            self.__processes.append(up)

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

    def prep_jobs(self, jobs):

        for job in jobs:
            if 'repo_group_id' in job:
                if job['repo_group_id'] != 0:
                    # Query all repos and last repo id
                    repoUrlSQL = s.sql.text("""
                            SELECT repo_git, repo_id FROM repo WHERE repo_group_id = {} ORDER BY repo_id ASC
                        """.format(job['repo_group_id']))
                else:
                    repoUrlSQL = s.sql.text("""
                            SELECT repo_git, repo_id FROM repo ORDER BY repo_id ASC
                        """.format(job['repo_group_id']))
                rs = pd.read_sql(repoUrlSQL, self.db, params={})
                if len(rs) == 0:
                    logging.info("Trying to send tasks for repo group with id: {}, but the repo group does not contain any repos".format(job['repo_group_id']))
                    continue

                if 'starting_repo_id' in job:
                    last_id = job['starting_repo_id']
                else:
                    repoIdSQL = s.sql.text("""
                            SELECT since_id_str FROM worker_job
                            WHERE job_model = '{}'
                        """.format(job['model']))

                    job_df = pd.read_sql(repoIdSQL, self.helper_db, params={})

                    # If a last id is not recorded, start from beginning of repos 
                    #   (first id is not necessarily 0)
                    try:
                        last_id = int(job_df.iloc[0]['since_id_str'])
                    except:
                        last_id = 0

                jobHistorySQL = s.sql.text("""
                        SELECT max(history_id) AS history_id, status FROM worker_history
                        GROUP BY status
                        LIMIT 1
                    """)

                history_df = pd.read_sql(jobHistorySQL, self.helper_db, params={})

                finishing_task = False
                if len(history_df.index) != 0:
                    if history_df.iloc[0]['status'] == 'Stopped':
                        self.history_id = int(history_df.iloc[0]['history_id'])
                        finishing_task = True
                        # last_id += 1 #update to match history tuple val rather than just increment


                # Rearrange repos so the one after the last one that 
                #   was completed will be ran first
                before_repos = rs.loc[rs['repo_id'].astype(int) < last_id]
                after_repos = rs.loc[rs['repo_id'].astype(int) >= last_id]

                reorganized_repos = after_repos.append(before_repos)

                if 'all_focused' in job:
                    reorganized_repos['focused_task'] = job['all_focused']

                reorganized_repos = reorganized_repos.to_dict('records')
            
                if finishing_task:
                    reorganized_repos[0]['focused_task'] = 1
                
                job['repos'] = reorganized_repos

            elif 'repo_id' in job:
                job['repo_group_id'] = None
                repoUrlSQL = s.sql.text("""
                    SELECT repo_git, repo_id FROM repo WHERE repo_id = {}
                """.format(job['repo_id']))

                rs = pd.read_sql(repoUrlSQL, self.db, params={})

                if 'all_focused' in job:
                    rs['focused_task'] = job['all_focused']

                rs = rs.to_dict('records')

                job['repos'] = rs

        return jobs

