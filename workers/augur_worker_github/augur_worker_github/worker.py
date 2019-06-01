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

class GitHubWorker:
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
            self.config['user'], self.config['pass'], self.config['host'], self.config['port'], self.config['database']
        )
        
        dbschema = 'augur_data'
        self.db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        metadata = MetaData()

        metadata.reflect(self.db, only=['issues', 'message', 'issue_message_ref'])

        Base = automap_base(metadata=metadata)

        Base.prepare()

        self.table = Base.classes.issues.__table__
        self.table1 = Base.classes.issues.__table__
        self.table2 = Base.classes.message.__table__
        self.table3 = Base.classes.issue_message_ref.__table__


        # Query all repos // CHANGE THIS
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
            'database_connection_string': 'psql://localhost:5433/augur',
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
                print(message.models)
                for model in message.models:
                    if model == "issues":
                        self.query_issues(message.entry_info)

                self.query(message.entry_info)

    def query_issues(self, entry_info):
        """ Data collection function
        Query the github api for contributors and issues (not yet implemented)
        """

        tool_source = 'AUGWOP GitHub Woker'
        tool_version = '0.1.0' # See __init__.py
        data_source = 'GitHup API'

        url = entry_info['repo_git']

        path = urlparse(url)
        split = path[2].split('/')

        owner = split[1]
        name = split[2]

        ### CONTRIBUTORS ###

        url = ("https://api.github.com/repos/" + owner + "/" + name + "/contributors")

        r = requests.get(url=url)
        data = r.json()

        for i in range(len(data)):
            data[item]['repo_id'] = entry_info['repo_id']
            
            modified_data = {
                # "cntrb_login": 'test',
                # "cntrb_email": 'test',
                # "cntrb_company": 'test',
                # "cntrb_type": 'test',
                # "cntrb_fake": 1,
                # "cntrb_deleted": 1,
                # "cntrb_long": 1,
                # "cntrb_lat": 1,
                # "cntrb_country_code": 1,
                # "cntrb_state": 'test',
                # "cntrb_city": 'test',
                # "cntrb_location": 'test',
                # "cntrb_canonical": 'test',
                "gh_user_id": data[i]['id'],
                "gh_login": data[i]['login'],
                "gh_url": data[i]['url'],
                "gh_html_url": data[i]['html_url'],
                "gh_node_id": data[i]['node_id'],
                "gh_avatar_url": data[i]['avatar_url'],
                "gh_gravatar_id": data[i]['gravatar_id'],
                "gh_followers_url": data[i]['followers_url'],
                "gh_following_url": data[i]['following_url'],
                "gh_gists_url": data[i]['gists_url'],
                "gh_starred_url": data[i]['starred_url'],
                "gh_subscriptions_url": data[i]['subscriptions_url'],
                "gh_organizationas_url": data[i]['organizations_url'],
                "gh_repos_url": data[i]['repos_url'],
                "gh_events_url": data[i]['events_url'],
                "gh_received_events_url": data[i]['received_events_url'],
                "gh_type": data[i]['type'],
                "gh_site_admin": data[i]['site_admin'],
                "tool_source": tool_source,
                "tool_version": tool_version,
                "data_source": data_source
            }

            # self.db.execute(self.table.insert().values(modified_data))


        ### ISSUES ###

        url = ("https://api.github.com/repos/" + owner + "/" + name + "/issues")

        r = requests.get(url=url)
        data = r.json()

        for i in range(len(data)):
            data[i]['repo_id'] = entry_info['repo_id']

            modified_data = {
                "issue_id": data[i]['number'], # primary key
                "repo_id": data[i]['repo_id'],
            #     "reporter_id": 1,
                "pull_request": data[i]['number'],
                "pull_request_id": data[i]['number'],
                "issue_title": data[i]['title'],
                "issue_body": data[i]['body'],
            #     "cntrb_id": 1,
                "comment_count": data[i]['comments'],
                "updated_at": data[i]['updated_at'],
                "closed_at": data[i]['closed_at'],
                "repository_url": data[i]['repository_url'],
                "issue_url": data[i]['url'],
                "labels_url": data[i]['labels_url'],
                "comments_url": data[i]['comments_url'],
                "events_url": data[i]['events_url'],
                "html_url": data[i]['html_url'],
                "issue_state": data[i]['state'],
            #    "issue_node_id": 1, #data[i]['node_id'], change to int ?
                "gh_issue_id": data[i]['id'],
                "gh_user_id": data[i]['user']['id']
                "tool_source": tool_source,
                "tool_version": tool_version,
                "data_source": data_source
            }

            # self.db.execute(self.table.insert().values(modified_data))
        
        ### ISSUE COMMENTS ####

        issue_number = '245'

        url = ("https://api.github.com/repos/" + owner + "/" + name + "/issues/" + issue_number)
        r = requests.get(url=url)
        data_issues = r.json()

        data_issues['repo_id'] = entry_info['repo_id']

        modified_data_issues = {
            "issue_id": data_issues['number'], # primary key
            "repo_id": data_issues['repo_id'],
        #     "reporter_id": 1,
            "pull_request": data_issues['number'],
            "pull_request_id": data_issues['number'],
            "issue_title": data_issues['title'],
            "issue_body": data_issues['body'],
        #     "cntrb_id": 1,
            "comment_count": data_issues['comments'],
            "updated_at": data_issues['updated_at'],
            "closed_at": data_issues['closed_at'],
            "repository_url": data_issues['repository_url'],
            "issue_url": data_issues['url'],
            "labels_url": data_issues['labels_url'],
            "comments_url": data_issues['comments_url'],
            "events_url": data_issues['events_url'],
            "html_url": data_issues['html_url'],
            "issue_state": data_issues['state'],
        #    "issue_node_id": 1, #data[i]['node_id'], change to int ?
            "gh_issue_id": data_issues['id'],
            "gh_user_id": data_issues['user']['id']
            "tool_source": tool_source,
            "tool_version": tool_version,
            "data_source": data_source
        }

        # self.db.execute(self.table1.insert().values(modified_data_issues))

        url = (url + "/comments")
        r = requests.get(url=url)
        data_message = r.json()

        for i in range(len(data_message)):
            modified_data_message = {
                "pltfrm_id": 25150,
                "msg_text": data_message[i]['body'],
                "msg_timestamp": data_message[i]['created_at']
            }

            # self.db.execute(self.table2.insert().values(modified_data_message))

        ### ISSUE MESSAGE REF TABLE ###

        modified_data_issue_message = {
            "issue_id": modified_data_issues['issue_id'],
        }

        # self.db.execute(self.table3.insert().values(modified_data_issue_message))

        requests.post('http://localhost:5000/api/completed_task', json=entry_info['repo_git'])