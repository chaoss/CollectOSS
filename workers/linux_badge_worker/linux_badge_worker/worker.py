import os
from datetime import datetime
import logging
import requests
import json
from urllib.parse import quote
from multiprocessing import Process, Queue

from linux_badge_worker import __data_source__, __tool_source__, __tool_version__
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from workers.standard_methods import register_task_completion, register_task_failure, connect_to_broker, update_gh_rate_limit, record_model_process

class CollectorTask:
    """ Worker's perception of a task in its queue
    Holds a message type (EXIT, TASK, etc) so the worker knows how to process the queue entry
    and the github_url given that it will be collecting data for
    """
    def __init__(self, message_type='TASK', entry_info=None):
        self.type = message_type
        self.entry_info = entry_info

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

class BadgeWorker:
    """ Worker that collects repo badging data from CII
    config: database credentials, broker information, and ID
    """
    def __init__(self, config, task=None):
        logging.info('Worker (PID: {}) initializing...'.format(str(os.getpid())))
        self.config = config

        self.db = None
        self.repo_badging_table = None

        self._task = task
        self._queue = Queue()
        self._child = None

        self.history_id = None
        self.finishing_task = False
        self.working_on = None
        self.results_counter = 0

        self.specs = {
            "id": self.config['id'],
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["badges"]
                }
            ],
            "config": [self.config]
        }

        self._db_str = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'],
            self.config['password'],
            self.config['host'],
            self.config['port'],
            self.config['database']
        )

        dbschema = 'augur_data'
        self.db = s.create_engine(self._db_str, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(self._db_str, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})
        logging.info("Database connection established...")

        metadata = MetaData()
        helper_metadata = MetaData()

        metadata.reflect(self.db, only=['repo_badging'])
        helper_metadata.reflect(self.helper_db, only=['worker_history', 'worker_job', 'worker_oauth'])

        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)

        Base.prepare()
        HelperBase.prepare()

        self.history_table = HelperBase.classes.worker_history.__table__
        self.job_table = HelperBase.classes.worker_job.__table__
        self.repo_badging_table = Base.classes.repo_badging.__table__
        logging.info("ORM setup complete...")

        # Organize different api keys/oauths available
        self.oauths = []
        self.headers = None

        # Endpoint to hit solely to retrieve rate limit information from headers of the response
        url = "https://api.github.com/users/gabe-heim"

        # Make a list of api key in the config combined w keys stored in the database
        oauth_sql = s.sql.text("""
            SELECT * FROM worker_oauth WHERE access_token <> '{}'
        """.format(0))

        for oauth in [{'oauth_id': 0, 'access_token': 0}] + json.loads(pd.read_sql(oauth_sql, self.helper_db, params={}).to_json(orient="records")):
            self.headers = {'Authorization': 'token %s' % oauth['access_token']}
            logging.info("Getting rate limit info for oauth: {}".format(oauth))
            response = requests.get(url=url, headers=self.headers)
            self.oauths.append({
                'oauth_id': oauth['oauth_id'],
                'access_token': oauth['access_token'],
                'rate_limit': int(response.headers['X-RateLimit-Remaining']),
                'seconds_to_reset': (datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])) \
                                                                - datetime.now()).total_seconds()
            })
            logging.info("Found OAuth available for use: {}".format(self.oauths[-1]))

        if len(self.oauths) == 0:
            logging.info("No API keys detected, please include one in your config or in the worker_oauths table in the augur_operations schema of your database\n")

        # First key to be used will be the one specified in the config (first element in
        #   self.oauths array will always be the key in use)
        self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}

        # Send broker hello message
        connect_to_broker(self, logging.getLogger())
        logging.info("Connected to the broker...\n")

    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            "key": "",
            "display_name": "",
            "description": "",
            "required": 1,
            "type": "string"
        }
        self.config.update(config)
        self.API_KEY = self.config['github_api_key']

    @property
    def task(self):
        """ Property that is returned when the worker's current task is referenced
        """
        return self._task

    @task.setter
    def task(self, value):
        """ entry point for the broker to add a task to the queue
        Adds this task to the queue, and calls method to process queue
        """
        
        if value['job_type'] == "UPDATE" or value['job_type'] == "MAINTAIN":
            self._queue.put(value)

        if 'focused_task' in value:
            if value['focused_task'] == 1:
                logging.info("Focused task is ON\n")
                self.finishing_task = True
            else:
                self.finishing_task = False
                logging.info("Focused task is OFF\n")
        else:
            self.finishing_task = False
            logging.info("Focused task is OFF\n")
        
        self._task = value
        self.run()


    def cancel(self):
        """ Delete/cancel current task
        """
        self._task = None

    def badges_model(self, entry_info, repo_id):
        """ Data collection and storage method
        Query the CII API and store the result in the DB for the badges model
        """
        git_url = entry_info['given']['git_url']
        logging.info("Collecting data for {}".format(git_url))
        extension = "/projects.json?pq=" + (quote(git_url[0:-4]))

        url = self.config['endpoint'] + extension
        logging.info("Hitting CII endpoint: " + url + " ...")
        data = requests.get(url=url).json()

        if data != []:
            logging.info("Inserting badging data for " + git_url)
            self.db.execute(self.repo_badging_table.insert()\
                            .values(repo_id=repo_id,
                                    data=data,
                                    tool_source=__tool_source__,
                                    tool_version=__tool_version__,
                                    data_source=__data_source__))

            self.results_counter += 1
        else:
            logging.info("No CII data found for {}\n".format(git_url))

    def collect(self):
        """ Function to process each entry in the worker's task queue
        Determines what action to take based off the message type
        """
        while True:
            if not self._queue.empty():
                message = self._queue.get()
                self.working_on = message['job_type']
            else:
                break
            logging.info("Popped off message: {}\n".format(str(message)))

            if message['job_type'] == 'STOP':
                break

            if message['job_type'] != 'MAINTAIN' and message['job_type'] != 'UPDATE':
                raise ValueError('{} is not a recognized task type'.format(message['job_type']))
                pass

            """ Query all repos with repo url of given task """
            repoUrlSQL = s.sql.text("""
                SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
                """.format(message['given']['git_url']))
            repo_id = int(pd.read_sql(repoUrlSQL, self.db, params={}).iloc[0]['repo_id'])

            try:
                if message['models'][0] == 'badges':
                    self.badges_model(message, repo_id)
            except Exception as e:
                register_task_failure(self, logging, message, repo_id, e)
                pass

        register_task_completion(self, logging, message, repo_id, "badges")

    def run(self):
        """ Kicks off the processing of the queue if it is not already being processed
        Gets run whenever a new task is added
        """
        logging.info("Running...\n")
        self._child = Process(target=self.collect, args=())
        self._child.start()
