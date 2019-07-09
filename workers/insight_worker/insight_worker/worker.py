from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
import logging
logging.basicConfig(filename='worker.log', filemode='w', level=logging.INFO)

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
        self.tool_source = 'Insight Worker'
        self.tool_version = '0.0.1' # See __init__.py

        logging.info("Worker initializing...\n")
        
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

        self.metric_results_counter = 0
        self.insight_results_counter = 0

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
        metadata.reflect(self.db, only=['chaoss_metric_status'])#self.config['table']])

        # we can then produce a set of mappings from this MetaData.
        Base = automap_base(metadata=metadata)

        # calling prepare() just sets up mapped classes and relationships.
        Base.prepare()

        # mapped classes are ready
        # self.insight_table = Base.classes[self.config['table']].__table__
        self.metrics_table = Base.classes['chaoss_metric_status'].__table__


        """ Query all repos """
        repoUrlSQL = s.sql.text("""
            SELECT repo_git, repo_id FROM repo
            """)
        rs = pd.read_sql(repoUrlSQL, self.db, params={})

        #fill queue
        for index, row in rs.iterrows():
            entry_info = {"git_url": row["repo_git"], "repo_id": row["repo_id"]}
            self._queue.put(CollectorTask(message_type='TASK', entry_info=entry_info))

        self.run()

        requests.post('http://localhost:5000/api/workers', json=specs) #hello message
        

    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            'database_connection_string': 'psql://localhost:5432/augur',
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
            SELECT repo_id, repo_group_id FROM repo WHERE repo_git = '{}'
            """.format(git_url))
        rs = pd.read_sql(repoUrlSQL, self.db, params={})
        try:
            self._queue.put(CollectorTask(message_type='TASK', entry_info={"git_url": git_url, 
                "repo_id": rs.iloc[0]["repo_id"], "repo_group_id": rs.iloc[0]["repo_group_id"]}))
        
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
        logging.info("Running...\n")
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
        # Update table of endpoints before we query them all
        self.update_metrics()

        """ Query all endpoints """
        endpointSQL = s.sql.text("""
            SELECT * FROM chaoss_metric_status WHERE cm_source = 'augur_db'
            """)
        endpoints = pd.read_sql(endpointSQL, self.db, params={}).to_json()
        logging.info(str(endpoints))

        base_url = 'http://localhost:5000/api/unstable/repo-groups/%s/repos/%s/' % (
            entry_info['repo_id'], entry_info['repo_group_id'])
        for endpoint in endpoints:
            url = base_url + endpoint['cm_info']
            logging.info("Hitting endpoint: " + url + "\n")
            r = requests.get(url=url)
            data = r.json()
            


        # data[0]['repo_id'] = entry_info['repo_id']
        # metrics = []
        # for obj in data:
        #     metrics.append(obj['tag'])

        
        # self.db.execute(self.table.insert().values(data[0]))
        # requests.post('http://localhost:5000/api/completed_task', json=entry_info['git_url'])

    def update_metrics(self):
        logging.info("Preparing to update metrics ...\n\n" + 
            "Hitting endpoint: http://localhost:5000/api/unstable/metrics/status ...\n")
        r = requests.get(url='http://localhost:5000/api/unstable/metrics/status')
        data = r.json()

        active_metrics = [metric for metric in data if metric['backend_status'] == 'implemented']

        # Duplicate checking ...
        need_insertion = self.filter_duplicates({'cm_api_endpoint_repo': "endpoint"}, ['chaoss_metric_status'], active_metrics)
        logging.info("Count of contributors needing insertion: " + str(len(need_insertion)) + "\n")

        for metric in need_insertion:

            tuple = {
                "cm_group": metric['group'],
                "cm_source": metric['data_source'],
                "cm_type": metric['metric_type'],
                "cm_backend_status": metric['backend_status'],
                "cm_frontend_status": metric['frontend_status'],
                "cm_defined": True if metric['is_defined'] == 'true' else False,
                "cm_api_endpoint_repo": metric['endpoint'],
                "cm_api_endpoint_rg": None,
                "cm_name": metric['display_name'],
                "cm_working_group": metric['group'],
                "cm_info": metric['tag'],
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": metric['data_source']
            }
            # Commit metric insertion to the chaoss metrics table
            result = self.db.execute(self.metrics_table.insert().values(tuple))
            logging.info("Primary key inserted into the metrics table: " + str(result.inserted_primary_key))
            self.metric_results_counter += 1

            logging.info("Inserted metric: " + metric['display_name'] + "\n")

    def filter_duplicates(self, cols, tables, og_data):
        need_insertion = []

        table_str = tables[0]
        del tables[0]
        for table in tables:
            table_str += ", " + table
        for col in cols.keys():
            colSQL = s.sql.text("""
                SELECT {} FROM {}
                """.format(col, table_str))
            values = pd.read_sql(colSQL, self.db, params={})

            for obj in og_data:
                if values.isin([obj[cols[col]]]).any().any():
                    logging.info("value of tuple exists: " + str(obj[cols[col]]) + "\n")
                elif obj not in need_insertion:
                    need_insertion.append(obj)
        logging.info("While filtering duplicates, we reduced the data size from " + str(len(og_data)) + 
            " to " + str(len(need_insertion)) + "\n")
        return need_insertion

