import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse

import pandas as pd
import requests
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base


LOG_FORMAT = '%(levelname)s:[%(name)s]: %(message)s'
logging.basicConfig(filename='worker.log', filemode='w', level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('ValueWorker')


class CollectorTask:
    """
    Worker's perception of a task in its queue.

    Holds a message type (EXIT, TASK, etc) so the worker knows how to process the queue entry
    and the github_url given that it will be collecting data for
    """
    def __init__(self, message_type='TASK', entry_info=None):
        self.type = message_type
        self.entry_info = entry_info


def dump_queue(queue):
    """
    Empties all pending items in a queue and returns them in a list.

    :param queue: The queue to be emptied.
    """
    result = []
    queue.put("STOP")
    for i in iter(queue.get, 'STOP'):
        result.append(i)
    # time.sleep(.1)
    return result

class ValueWorker:
    """
    Worker that sythesises Value related data from the git repostiories and stores it in our database.

    :param config: holds info like api keys, descriptions, and database connection strings
    :param task: most recent task the broker added to the worker's queue
    """
    def __init__(self, config, task=None):
        logger.info(f'Worker (PID: {os.getpid()}) initializing...')
        self._task = task
        self._child = None
        self._queue = Queue()
        self._maintain_queue = Queue()
        self.working_on = None
        self.config = config
        self.db = None
        self.table = None
        self.API_KEY = self.config['key']
        self.tool_source = 'Value Worker'
        self.tool_version = '0.0.1' # See __init__.py
        self.data_source = 'scc'
        self.results_counter = 0
        self.headers = {'Authorization': f'token {self.API_KEY}'}
        self.history_id = None
        self.finishing_task = False
        self.scc_bin = self.config['scc_bin']

        url = "https://api.github.com"
        response = requests.get(url=url, headers=self.headers)
        self.rate_limit = int(response.headers['X-RateLimit-Remaining'])

        specs = {
            "id": self.config['id'],
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["value"]
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'],
            self.config['port'], self.config['database']
        )

        #Database connections
        logger.info("Making database connections...")
        dbschema = 'augur_data'
        self.db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        metadata = MetaData()
        helper_metadata = MetaData()

        metadata.reflect(self.db, only=['repo_labor'])

        helper_metadata.reflect(self.helper_db, only=['worker_history', 'worker_job'])

        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)

        Base.prepare()
        HelperBase.prepare()

        self.repo_labor_table = Base.classes.repo_labor.__table__

        self.history_table = HelperBase.classes.worker_history.__table__
        self.job_table = HelperBase.classes.worker_job.__table__

        try:
            # Hello message
            requests.post('http://{}:{}/api/unstable/workers'.format(
                self.config['broker_host'],self.config['broker_port']), json=specs)
        except:
            logger.info("Broker's port is busy, worker will not be able to accept tasks, "
                "please restart Augur if you want this worker to attempt connection again.")

    def update_config(self, config):
        """ Method to update config and set a default """
        self.config = {
            "display_name": "",
            "description": "",
            "required": 1,
            "type": "string"
        }
        self.config.update(config)
        self.API_KEY = self.config['key']

    @property
    def task(self):
        """ Property that is returned when the worker's current task is referenced
        """
        return self._task

    @task.setter
    def task(self, value):
        """
        Entry point for the broker to add a task to the queue
        Adds this task to the queue, and calls method to process queue
        """
        git_url = value['given']['git_url']

        repo_url_SQL = s.sql.text("""
            SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
            """.format(git_url))
        rs = pd.read_sql(repo_url_SQL, self.db, params={})

        try:
            repo_id = int(rs.iloc[0]['repo_id'])
            if value['job_type'] == "UPDATE":
                self._queue.put(CollectorTask(message_type='TASK', entry_info={"task": value, "repo_id": repo_id}))
            elif value['job_type'] == "MAINTAIN":
                self._maintain_queue.put(CollectorTask(message_type='TASK', entry_info={"task": value, "repo_id": repo_id}))
            if 'focused_task' in value:
                if value['focused_task'] == 1:
                    self.finishing_task = True

        except Exception as e:
            logger.error(f"error: {e}, or that repo is not in our database: {value}")

        self._task = CollectorTask(message_type='TASK', entry_info={"task": value})
        self.run()

    def cancel(self):
        """ Delete/cancel current task
        """
        self._task = None

    def run(self):
        """ Kicks off the processing of the queue if it is not already being processed
        Gets run whenever a new task is added
        """
        logger.info("Running...")
        self._child = Process(target=self.collect, args=())
        self._child.start()

    def collect(self):
        """ Function to process each entry in the worker's task queue
        Determines what action to take based off the message type
        """
        repos = requests.get('http://{}:{}/api/unstable/dosocs/repos'.format(
                self.config['broker_host'],self.config['broker_port'])).json()

        for repo in repos:
            self.generate_value_data(repo['repo_id'], repo['path'])

        self.register_task_completion('value')

        # while True:
        #     time.sleep(2)
        #     logger.info(f'Maintain Queue Empty: {self._maintain_queue.empty()}')
        #     logger.info(f'Queue Empty: {self._queue.empty()}')
        #     if not self._queue.empty():
        #         message = self._queue.get()
        #         logger.info(f"Popped off message from Queue: {message.entry_info}")
        #         self.working_on = "UPDATE"
        #     elif not self._maintain_queue.empty():
        #         message = self._maintain_queue.get()
        #         logger.info(f"Popped off message from Maintain Queue: {message.entry_info}")
        #         self.working_on = "MAINTAIN"
        #     else:
        #         break

        #     if message.type == 'EXIT':
        #         break

        #     if message.type != 'TASK':
        #         raise ValueError(f'{message.type} is not a recognized task type')

        #     if message.type == 'TASK':
        #         try:
        #             repos = requests.get('http://{}:{}/api/unstable/dosocs/repos'.format(
        #                         self.config['broker_host'],self.config['broker_port'])).json()

        #             for repo in repos:
        #                 self.generate_value_data(repo['repo_id'], repo['path'])

        #             self.register_task_completion('value')

        #         except Exception:
        #             # logger.error("Worker ran into an error for task: {}\n".format(message.entry_info['task']))
        #             # logger.error("Error encountered: " + str(e) + "\n")
        #             # # traceback.format_exc()
        #             # logger.info("Notifying broker and logging task failure in database...\n")

        #             logger.exception(f'Worker ran into an error for task {message.entry_info}')
        #             self.register_task_failure(message.entry_info['repo_id'],
        #                                        message.entry_info['task']['given']['git_url'])

        #             # Add to history table
        #             task_history = {
        #                 "repo_id": message.entry_info['repo_id'],
        #                 "worker": self.config['id'],
        #                 "job_model": message.entry_info['task']['models'][0],
        #                 "oauth_id": self.config['zombie_id'],
        #                 "timestamp": datetime.datetime.now(),
        #                 "status": "Error",
        #                 "total_results": self.results_counter
        #             }

        #             if self.history_id:
        #                 self.helper_db.execute(self.history_table.update().where(self.history_table.c.history_id==self.history_id).values(task_history))
        #             else:
        #                 r = self.helper_db.execute(self.history_table.insert().values(task_history))
        #                 self.history_id = r.inserted_primary_key[0]

        #             logger.info(f"Recorded job error for: {message.entry_info['task']}")

        #             # Update job process table
        #             updated_job = {
        #                 "since_id_str": message.entry_info['repo_id'],
        #                 "last_count": self.results_counter,
        #                 "last_run": datetime.datetime.now(),
        #                 "analysis_state": 0
        #             }
        #             self.helper_db.execute(self.job_table.update().where(self.job_table.c.job_model==message.entry_info['task']['models'][0]).values(updated_job))
        #             logger.info("Updated job process for model: " + message.entry_info['task']['models'][0] + "\n")

        #             # Reset results counter for next task
        #             self.results_counter = 0
        #             pass

    def generate_value_data(self, repo_id, path):
        """Runs scc on repo and stores data in database

        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """
        logger.info('Running `scc`....')
        logger.info(f'Repo ID: {repo_id}, Path: {path}')

        output = subprocess.check_output([self.scc_bin, '-f', 'json', path])
        records = json.loads(output.decode('utf8'))

        for record in records:
            for file in record['Files']:
                repo_labor = {
                    'repo_id': repo_id,
                    'rl_analysis_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'programming_language': file['Language'],
                    'file_path': file['Location'],
                    'file_name': file['Filename'],
                    'total_lines': file['Lines'],
                    'code_lines': file['Code'],
                    'comment_lines': file['Comment'],
                    'blank_lines': file['Blank'],
                    'code_complexity': file['Complexity'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': 'scc',
                    'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                }

                result = self.db.execute(self.repo_labor_table.insert().values(repo_labor))
                logger.info(f"Added Repo Labor Data: {result.inserted_primary_key}")

    def register_task_completion(self, model):
        # Task to send back to broker
        task_completed = {
            'worker_id': self.config['id'],
            'job_type': self.working_on,
            'repo_id': '0',
            'git_url': 'None'
        }

        # Notify broker of completion
        logger.info(f"Telling broker we completed task: {task_completed}")
        logger.info(f"This task inserted {self.results_counter} tuples\n")

        try:
            requests.post('http://{}:{}/api/unstable/completed_task'.format(
                self.config['broker_host'],self.config['broker_port']), json=task_completed)
        except requests.exceptions.ConnectionError:
            logger.info("Broker is booting and cannot accept the worker's message currently")
        except Exception:
            logger.exception('An unknown error occured while informing broker about task failure')

        # Reset results counter for next task
        self.results_counter = 0

    def register_task_failure(self, repo_id, git_url):
        task_failed = {
            'worker_id': self.config['id'],
            'job_type': self.working_on,
            'repo_id': repo_id,
            'git_url': git_url
        }

        logger.error('Task failed')
        logger.error('Informing broker about Task Failure')
        logger.info(f'This task inserted {self.results_counter} tuples\n')

        try:
            requests.post('http://{}:{}/api/unstable/task_error'.format(
                self.config['broker_host'],self.config['broker_port']), json=task_failed)
        except requests.exceptions.ConnectionError:
            logger.error('Could not send task failure message to the broker')
        except Exception:
            logger.exception('An unknown error occured while informing broker about task failure')

        self.results_counter = 0
