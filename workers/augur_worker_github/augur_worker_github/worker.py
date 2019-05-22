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



class GitHubWorker:
    """ Worker that collects data from the Github API and stores it in our database
    task: current task being worked on
    child: current process of the queue being ran
    queue: queue of tasks to be fulfilled
    config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config, task=None):
        self._task = task
        self._child = None
        self._queue = Queue()
        self.config = config
        # self.update_config(self, config)
        self.db = None
        self.table = None
        self.API_KEY = self.config['key']
        
        specs = {
            "id": "com.augurlabs.core.github_worker",
            "location": "http://localhost:51232",
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["issues"]
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['database']
        )
        
        dbschema = 'augur_data'
        self.db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        metadata = MetaData()

        metadata.reflect(self.db, only=['contributors'])

        Base = automap_base(metadata=metadata)

        Base.prepare()

        self.table = Base.classes.contributors.__table__

        # Query all repos
        repoUrlSQL = s.sql.text("""
            SELECT repo_git, repo_id FROM repo
            """)

        rs = pd.read_sql(repoUrlSQL, self.db, params={})

        # Populate queue
        for index, row in rs.iterrows():
            self._queue.put(CollectorTask(message_type='TASK', entry_info=row))

        self.run()

        requests.post('http://localhost:5000/api/workers', json=specs) #hello message

    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            'database_connection_string': 'psql://localhost:5432/augur',
            "key": "2759b561575060cce0d87c0f8d7f72f53fe35e14",
            "host": "nekocase.augurlabs.io",
            "password": "avengers22",
            "port": "5433",
            "user": "augur",
            "database": "augur",
            "table": "contributors",
            "endpoint": "https://bestpractices.coreinfrastructure.org/projects.json",
            "display_name": "GitHub API Key",
            "description": "API Token for the GitHub API v3",
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
        """ Method to set or update the current task property's value
        Adds this task to the queue, and calls method to process queue
        """
        git_url = value[0]['given']['git_url']
        self._queue.put(CollectorTask(message_type='TASK', github_url=git_url))
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
        url = entry_info['repo_git']

        path = urlparse(url)
        split = path[2].split('/')

        owner = split[1]
        name = split[2]

        url = ("https://api.github.com/repos/" + owner + "/" + name + "/contributors") # Issues??
        # check if contributor has been loaded in already before creating duplicates
        # only store contributors in the database

        r = requests.get(url=url)
        data = r.json()
        data[0]['repo_id'] = entry_info['repo_id']
        
        modified_data = {
            "cntrb_id": data[0]['id'],
            "cntrb_login": 'test',
            "cntrb_email": 'test',
            "cntrb_company": 'test',
            "cntrb_created_at": '2016-06-22 19:10:25-07',
            "cntrb_type": 'test',
            "cntrb_fake": 1,
            "cntrb_deleted": 1,
            "cntrb_long": 1,
            "cntrb_lat": 1,
            "cntrb_country_code": 1,
            "cntrb_state": 'test',
            "cntrb_city": 'test',
            "cntrb_location": 'test',
            "cntrb_canonical": 'test',
            "gh_user_id": data[0]['id'],
            "gh_login": data[0]['login'],
            "gh_url": data[0]['url'],
            "gh_html_url": data[0]['html_url'],
            "gh_node_id": data[0]['node_id'],
            "gh_avatar_url": data[0]['avatar_url'],
            "gh_gravatar_id": data[0]['gravatar_id'],
            "gh_followers_url": data[0]['followers_url'],
            "gh_following_url": data[0]['following_url'],
            "gh_gists_url": data[0]['gists_url'],
            "gh_starred_url": data[0]['starred_url'],
            "gh_subscriptions_url": data[0]['subscriptions_url'],
            "gh_organizationas_url": data[0]['organizations_url'],
            "gh_repos_url": data[0]['repos_url'],
            "gh_events_url": data[0]['events_url'],
            "gh_received_events_url": data[0]['received_events_url'],
            "gh_type": data[0]['type'],
            "gh_site_admin": data[0]['site_admin'],
            "tool_source": 'test',
            "tool_version": 'test',
            "data_source": 'test',
            "data_collection_date": '2016-06-22 19:10:25-07'
        }

        self.db.execute(self.table.insert().values(modified_data))

        # request = requests.get(url)
        # if request.status_code == 200:
        #     print(request.json())
        #     return request.json()
        # else:
        #     raise Exception("ERROR {}".format(request.status_code))
        # #call method that starting