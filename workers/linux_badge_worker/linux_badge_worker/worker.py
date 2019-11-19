from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests, logging, os
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
logging.basicConfig(filename='worker.log', level=logging.INFO, filemode='w')

import ipdb

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
    """ Worker that collects data from the Github API and stores it in our database
    task: most recent task the broker added to the worker's queue
    child: current process of the queue being ran
    queue: queue of tasks to be fulfilled
    config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config, task=None):
        self._task = task
        self._child = None
        self._queue = Queue()
        self.config = config
        logging.basicConfig(filename='worker_{}.log'.format(self.config['id'].split('.')[len(self.config['id'].split('.')) - 1]), filemode='w', level=logging.INFO)
        logging.info('Worker (PID: {}) initializing...'.format(str(os.getpid())))
        self.db = None
        self.table = None

        specs = {
            "id": "com.augurlabs.core.badge_worker",
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["badges"]
                }
            ],
            "config": [self.config]
        }

        """
        Connect to GHTorrent

        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
        """
        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['database']
        )
        logging.info(self.DB_STR)

        dbschema='augur_data' # Searches left-to-right
        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})


        # produce our own MetaData object
        metadata = MetaData()

        # we can reflect it ourselves from a database, using options
        # such as 'only' to limit what tables we look at...
        metadata.reflect(self.db, only=['repo_badging'])


        # we can then produce a set of mappings from this MetaData.
        Base = automap_base(metadata=metadata)

        # calling prepare() just sets up mapped classes and relationships.
        Base.prepare()

        # mapped classes are ready
        self.table = Base.classes.repo_badging.__table__

        self.run()

        requests.post('http://{}:{}/api/workers'.format(self.config['broker_host'],self.config['broker_port'], json=specs)) #hello message


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
        git_url = value['given']['git_url']

        """ Query all repos """
        repoUrlSQL = s.sql.text("""
            SELECT repo_id FROM repo WHERE repo_git = '{}'
            """.format(git_url))
        rs = pd.read_sql(repoUrlSQL, self.db, params={})
        try:
            self._queue.put(CollectorTask(message_type='TASK', entry_info={"git_url": git_url, "repo_id": rs.iloc[0]["repo_id"]}))

        # list_queue = dump_queue(self._queue)
        # logging.info("worker's queue after adding the job: " + list_queue)

        except:
            logging.info("that repo is not in our database")
        if self._queue.empty():
            if 'github.com' in git_url:
                self._task = value
                self.run()


    def cancel(self):
        """ Delete/cancel current task
        """
        self._task = None

    def collect(self, num):
        """ Data collection and storage method
        Query the github api for contributors and issues (not yet implemented)
        """
        git_url = str(num)
        extension = "/en/projects/" + str(git_url) + ".json"

        url = self.config['endpoint'] + extension
        print("******************")
        print(url)
        logging.info("Hitting endpoint: " + url + " ...\n")
        r = requests.get(url=url)
        data = r.json()
        if data != 0 and "404" not in str(r):
            #print(data)
            print("FOUND")
            # data[0]['repo_id'] = entry_info['repo_id']

            # ipdb.set_trace()
            self.db.execute(self.table.insert().values(data=data, tool_source="linux_badge_worker", tool_version="1.0", data_source="CII Badging API"))
            # logging.info("Inserted badging info for repo: " + str(entry_info['repo_id']) + "\n")
            """
            task_completed = entry_info
            task_completed['worker_id'] = self.config['id']

            logging.info("Telling broker we completed task: " + str(task_completed) + "\n\n")
            requests.post('http://localhost:5000/api/completed_task', json=entry_info['git_url'])
            """
        else:
            logging.info("Endpoint did not return any data.")
        #if num < 3500:
        #    self.collect(num + 1)

    def run(self):
        """ Kicks off the processing of the queue if it is not already being processed
        Gets run whenever a new task is added
        """
        # if not self._child:
        for i in range(1571, 3500):
            self.collect(i)
