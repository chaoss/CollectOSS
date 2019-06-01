from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData

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

class InsightWorker:
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
        self.db = None
        self.table = None
        
        specs = {
            "id": "com.augurlabs.core.badge_worker",
            "location": "http://localhost:51235",
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

        dbschema='augur_data' # Searches left-to-right
        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        
        # produce our own MetaData object
        metadata = MetaData()

        # we can reflect it ourselves from a database, using options
        # such as 'only' to limit what tables we look at...
        metadata.reflect(self.db, only=[self.config['table']])

        # we can then produce a set of mappings from this MetaData.
        Base = automap_base(metadata=metadata)

        # calling prepare() just sets up mapped classes and relationships.
        Base.prepare()

        # mapped classes are ready
        self.table = Base.classes[self.config['table']].__table__


        # """ Query all repos """
        # repoUrlSQL = s.sql.text("""
        #     SELECT repo_git, repo_id FROM repo
        #     """)
        # rs = pd.read_sql(repoUrlSQL, self.db, params={})

        # #fill queue
        # for index, row in rs.iterrows():
        #     entry_info = {"git_url": row["repo_git"], "repo_id": row["repo_id"]}
        #     self._queue.put(CollectorTask(message_type='TASK', entry_info=entry_info))

        # self.run()

        requests.post('http://localhost:5000/api/workers', json=specs) #hello message
        

    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            'database_connection_string': 'psql://localhost:5432/augur',
            "key": "",
            "display_name": "",
            "description": "",
            "required": 1,
            "type": "string"
        }
        self.config.update(config)

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
        print("VALUE", value)
        git_url = value['given']['git_url']

        """ Query all repos """
        repoUrlSQL = s.sql.text("""
            SELECT repo_id FROM repo WHERE repo_git = '{}'
            """.format(git_url))
        rs = pd.read_sql(repoUrlSQL, self.db, params={})
        print(rs, repoUrlSQL)
        try:
            self._queue.put(CollectorTask(message_type='TASK', entry_info={"git_url": git_url, "repo_id": rs.iloc[0]["repo_id"]}))
        
        # list_queue = dump_queue(self._queue)
        # print("worker's queue after adding the job: " + list_queue)

        except:
            print("that repo is not in our database")
        if self._queue.empty(): 
            if 'github.com' in git_url:
                self._task = value
                self.run()


    def cancel(self):
        """ Delete/cancel current task
        """
        self._task = None

    def run(self):
        """ Kicks off the processing of the queue if it is not already being processed
        Gets run whenever a new task is added
        """
        if not self._child:
            self._child = Process(target=self.collect, args=())
            self._child.start()

    def collect(self):
        """ Function to process each entry in the worker's task queue
        Determines what action to take based off the message type
        """
        while True:
            if not self._queue.empty():
                message = self._queue.get()
            else:
                break

            if message.type == 'EXIT':
                break
            if message.type != 'TASK':
                raise ValueError(f'{message.type} is not a recognized task type')

            if message.type == 'TASK':
                self.query(message.entry_info)

    def query(self, entry_info):
        """ Data collection function
        Query the github api for contributors and issues (not yet implemented)
        """
        url = self.config['endpoint']

        r = requests.get(url=url)
        data = r.json()
        data[0]['repo_id'] = entry_info['repo_id']
        metrics = []
        for obj in data:
            metrics.append(obj['tag'])

        
        # self.db.execute(self.table.insert().values(data[0]))
        # requests.post('http://localhost:5000/api/completed_task', json=entry_info['git_url'])



