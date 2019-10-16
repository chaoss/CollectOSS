from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
import datetime
import time
import logging
import json
import ast
import os

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
        self.config = config
        logging.basicConfig(filename='worker_{}.log'.format(self.config['id'].split('.')[len(self.config['id'].split('.')) - 1]), filemode='w', level=logging.INFO)
        logging.info('Worker (PID: {}) initializing...'.format(str(os.getpid())))
        self._task = task
        self._child = None
        self._queue = Queue()
        self._maintain_queue = Queue()
        self.working_on = None
        self.db = None
        self.table = None
        self.API_KEY = self.config['key']
        self.tool_source = 'GitHub API Worker'
        self.tool_version = '0.0.3' # See __init__.py
        self.data_source = 'GitHub API'
        self.results_counter = 0
        self.headers = {'Authorization': 'token %s' % self.config['key']}
        self.history_id = None
        self.finishing_task = False

        url = "https://api.github.com/users/gabe-heim"
        response = requests.get(url=url, headers=self.headers)
        self.rate_limit = int(response.headers['X-RateLimit-Remaining'])

        specs = {
            "id": self.config['id'],
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["github_url"]],
                    "models":["issues", "contributors"]
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['database']
        )

        #Database connections
        logging.info("Making database connections... {}".format(self.DB_STR))
        dbschema = 'augur_data'
        self.db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        metadata = MetaData()
        helper_metadata = MetaData()

        metadata.reflect(self.db, only=['contributors', 'issues', 'issue_labels', 'message',
            'issue_message_ref', 'issue_events',
            'issue_assignees','contributors_aliases'])
        helper_metadata.reflect(self.helper_db, only=['worker_history', 'worker_job'])

        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)

        Base.prepare()
        HelperBase.prepare()

        self.contributors_table = Base.classes.contributors.__table__
        self.issues_table = Base.classes.issues.__table__
        self.issue_labels_table = Base.classes.issue_labels.__table__
        self.issue_events_table = Base.classes.issue_events.__table__
        self.message_table = Base.classes.message.__table__
        self.issues_message_ref_table = Base.classes.issue_message_ref.__table__
        self.issue_assignees_table = Base.classes.issue_assignees.__table__
        self.contributors_aliases_table = Base.classes.contributors_aliases.__table__

        self.history_table = HelperBase.classes.worker_history.__table__
        self.job_table = HelperBase.classes.worker_job.__table__

        # Get max ids so we know where we are in our insertion and to have the current id when inserting FK's
        logging.info("Querying starting ids info...\n")
        maxIssueSQL = s.sql.text("""
            SELECT max(issues.issue_id) AS issue_id
            FROM issues
        """)
        rs = pd.read_sql(maxIssueSQL, self.db, params={})
        issue_start = int(rs.iloc[0]["issue_id"]) if rs.iloc[0]["issue_id"] is not None else 25150


        maxCntrbSQL = s.sql.text("""
            SELECT max(contributors.cntrb_id) AS cntrb_id
            FROM contributors
        """)
        rs = pd.read_sql(maxCntrbSQL, self.db, params={})
        cntrb_start = int(rs.iloc[0]["cntrb_id"]) if rs.iloc[0]["cntrb_id"] is not None else 25150


        maxMsgSQL = s.sql.text("""
            SELECT max(msg_id) AS msg_id
            FROM message
        """)
        rs = pd.read_sql(maxMsgSQL, self.db, params={})
        msg_start = int(rs.iloc[0]["msg_id"]) if rs.iloc[0]["msg_id"] is not None else 25150

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.issue_id_inc = (issue_start + 1)
        self.cntrb_id_inc = (cntrb_start + 1)
        self.msg_id_inc = (msg_start + 1)

        try:
            logging.info("Sending hello message to broker... @ -> {} with info: {}\n".format('http://{}:{}/api/unstable/workers'.format(
                self.config['broker_host'], self.config['broker_port']), specs))
            requests.post('http://{}:{}/api/unstable/workers'.format(
                self.config['broker_host'], self.config['broker_port']), json=specs) #hello message
        except:
            logging.info("Broker's port is busy, worker will not be able to accept tasks, "
                "please restart Augur if you want this worker to attempt connection again.")

        # self.search_users({'repo_git': 'https://github.com/rails/rails.git', 'repo_id': 21000})

    def search_users(self, entry_info):
        logging.info("Searching users for commits from the facade worker for repo with entry info: {}".format(entry_info))
        userSQL = s.sql.text("""
            SELECT distinct(cmt_author_name), cmt_author_email, 
                cmt_committer_name, cmt_committer_email
            FROM commits
            WHERE repo_id = {}
        """.format(entry_info['repo_id']))
        # cmt_author_raw_email
        # cmt_committer_raw_email
        rs = pd.read_sql(userSQL, self.db, params={})
        commits = rs.to_json(orient="records")
        commits = json.loads(commits)
        logging.info("We found {} distinct contributors to search for in this repo (repo_id = {})".format(
            len(commits), entry_info['repo_id']))

        pseudo_key_gh = 'login'
        pseudo_key_augur = 'cntrb_login'
        table = 'contributors'
        cntrb_table_values = self.get_table_values([pseudo_key_augur, 'cntrb_email', 'cntrb_id'], [table])
        for tuple in commits:
            try:
                author = {'fname': tuple['cmt_author_name'].split()[0], 'lname': tuple['cmt_author_name'].split()[1],
                    'email': tuple['cmt_author_email']}
                committer = {'fname': tuple['cmt_committer_name'].split()[0], 'lname': tuple['cmt_committer_name'].split()[1],
                    'email': tuple['cmt_committer_email']}
            except:
                author = {'fname': tuple['cmt_author_name'].split()[0], 'lname': '',
                    'email': tuple['cmt_author_email']}
                committer = {'fname': tuple['cmt_committer_name'].split()[0], 'lname': '',
                    'email': tuple['cmt_committer_email']}
            if author == committer:
                contributors = [author]
            else:
                contributors = [author, committer]
            for cmt_cntrb in contributors:
                url = 'https://api.github.com/search/users?q={}+in:email+fullname:{}+{}'.format(
                    cmt_cntrb['email'],cmt_cntrb['fname'],cmt_cntrb['lname'])
                logging.info("Hitting endpoint: " + url + " ...\n")
                r = requests.get(url=url, headers=self.headers)
                self.update_rate_limit(r)

                results = r.json()
                if 'total_count' in results:
                    if results['total_count'] != 0:
                        logging.info("When searching for a contributor with info {}, we found the following users: {}".format(
                            cmt_cntrb, results))
                        match = results['items'][0]
                        for item in results['items']:
                            if item['score'] > match['score']:
                                match = item

                        match = self.assign_tuple_action([match], cntrb_table_values, 
                            {'cntrb_email': 'email'}, {pseudo_key_augur: pseudo_key_gh}, 'cntrb_id')[0]
                        
                        cntrb_url = ("https://api.github.com/users/" + match['login'])
                        logging.info("Hitting endpoint: " + cntrb_url + " ...\n")
                        r = requests.get(url=cntrb_url, headers=self.headers)
                        self.update_rate_limit(r)
                        contributor = r.json()

                        company = None
                        location = None
                        email = cmt_cntrb['email']
                        canonical_email = cmt_cntrb['email']
                        alias = False
                        if 'company' in contributor:
                            company = contributor['company']
                        if 'location' in contributor:
                            location = contributor['location']
                        if 'email' in contributor:
                            email = contributor['email']
                            if email != cmt_cntrb['email']:
                                alias = True

                        # aliasSQL = s.sql.text("""
                        #     SELECT canonical_email
                        #     FROM contributors_aliases
                        #     WHERE alias_email = {}
                        # """.format(contributor['email']))
                        # rs = pd.read_sql(aliasSQL, self.db, params={})

                        #rs.iloc[0]["canonical_email"]

                        cntrb = {
                            "cntrb_login": contributor['login'],
                            "cntrb_created_at": contributor['created_at'],
                            "cntrb_email": email,
                            "cntrb_company": company,
                            "cntrb_location": location,
                            # "cntrb_type": , dont have a use for this as of now ... let it default to null
                            "cntrb_canonical": canonical_email,
                            "gh_user_id": contributor['id'],
                            "gh_login": contributor['login'],
                            "gh_url": contributor['url'],
                            "gh_html_url": contributor['html_url'],
                            "gh_node_id": contributor['node_id'],
                            "gh_avatar_url": contributor['avatar_url'],
                            "gh_gravatar_id": contributor['gravatar_id'],
                            "gh_followers_url": contributor['followers_url'],
                            "gh_following_url": contributor['following_url'],
                            "gh_gists_url": contributor['gists_url'],
                            "gh_starred_url": contributor['starred_url'],
                            "gh_subscriptions_url": contributor['subscriptions_url'],
                            "gh_organizations_url": contributor['organizations_url'],
                            "gh_repos_url": contributor['repos_url'],
                            "gh_events_url": contributor['events_url'],
                            "gh_received_events_url": contributor['received_events_url'],
                            "gh_type": contributor['type'],
                            "gh_site_admin": contributor['site_admin'],
                            "tool_source": self.tool_source,
                            "tool_version": self.tool_version,
                            "data_source": self.data_source,
                            'cntrb_full_name': cmt_cntrb['fname'] + ' ' + cmt_cntrb['lname']
                        }

                        # Commit insertion to table
                        if match['flag'] == 'need_update':
                            result = self.db.execute(self.contributors_table.update().where(
                                self.history_table.c.cntrb_email==email).values(cntrb))
                            logging.info("Updated tuple in the contributors table with existing email: {}".format(email))
                            self.cntrb_id_inc = match['pkey']
                        elif match['flag'] == 'need_insertion':
                            result = self.db.execute(self.contributors_table.insert().values(cntrb))
                            logging.info("Primary key inserted into the contributors table: {}".format(result.inserted_primary_key))
                            self.results_counter += 1
            
                            logging.info("Inserted contributor: " + contributor['login'] + "\n")

                            # Increment our global track of the cntrb id for the possibility of it being used as a FK
                            self.cntrb_id_inc = int(result.inserted_primary_key[0])

                        if alias:
                            try:
                                alias_tuple = {
                                    'cntrb_id': match['pkey'] if match['flag'] == 'need_update' else int(result.inserted_primary_key[0]),
                                    'cntrb_a_id': match['pkey'] if match['flag'] == 'need_update' else int(result.inserted_primary_key[0]),
                                    'canonical_email': cmt_cntrb['email'],
                                    'alias_email': contributor['email'],
                                    'cntrb_active': 1,
                                    "tool_source": self.tool_source,
                                    "tool_version": self.tool_version,
                                    "data_source": self.data_source
                                }
                                result = self.db.execute(self.contributors_aliases_table.insert().values(alias_tuple))
                                logging.info("Inserted alias with email: {}".format(email))
                            except Exception as e:
                                logging.info("Error inserting alias w emails {} and {}: {}".format(contributor['email'], cmt_cntrb['email'], e))





    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            'database_connection_string': 'psql://{}:5433/augur'.format(self.config['broker_host']),
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
        github_url = value['given']['github_url']

        """ Query all repos """
        repoUrlSQL = s.sql.text("""
            SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
            """.format(github_url))
        rs = pd.read_sql(repoUrlSQL, self.db, params={})
        try:
            repo_id = int(rs.iloc[0]['repo_id'])
            if value['job_type'] == "UPDATE":
                self._queue.put(CollectorTask(message_type='TASK', entry_info={"task": value, "repo_id": repo_id}))
            elif value['job_type'] == "MAINTAIN":
                self._maintain_queue.put(CollectorTask(message_type='TASK', entry_info={"task": value, "repo_id": repo_id}))
            if 'focused_task' in value:
                if value['focused_task'] == 1:
                    logging.info("focused task is ON\n")
                    self.finishing_task = True
                else:
                    self.finishing_task = False
                    logging.info("focused task is OFF\n")
            else:
                self.finishing_task = False
                logging.info("focused task is OFF\n")

        except Exception as e:
            logging.info("error: {}, or that repo is not in our database: {}".format(str(e), str(value)))
        
        self._task = CollectorTask(message_type='TASK', entry_info={"task": value, "repo_id": repo_id})
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
        if self._child is None:
            self._child = Process(target=self.collect, args=())
            self._child.start()
            
    def collect(self):
        """ Function to process each entry in the worker's task queue
        Determines what action to take based off the message type
        """
        while True:
            time.sleep(0.5)
            if not self._queue.empty():
                message = self._queue.get()
                self.working_on = "UPDATE"
            else:
                if not self._maintain_queue.empty():
                    message = self._maintain_queue.get()
                    logging.info("Popped off message: {}\n".format(str(message.entry_info)))
                    self.working_on = "MAINTAIN"
                else:
                    break

            if message.type == 'EXIT':
                break

            if message.type != 'TASK':
                raise ValueError(f'{message.type} is not a recognized task type')

            if message.type == 'TASK':
                try:
                    github_url = message.entry_info['task']['given']['github_url']
                    if message.entry_info['task']['models'][0] == 'contributors':
                        self.search_users({'github_url': github_url, 'repo_id': message.entry_info['repo_id']})
                    if message.entry_info['task']['models'][0] == 'issues':
                        self.query_issues({'github_url': github_url, 'repo_id': message.entry_info['repo_id']})
                except Exception as e:
                    logging.info("Worker ran into an error for task: {}\n".format(message.entry_info['task']))
                    logging.info("Error encountered: " + repr(e) + "\n")
                    logging.info("Notifying broker and logging task failure in database...\n")
                    message.entry_info['task']['worker_id'] = self.config['id']
                    requests.post("http://{}:{}/api/unstable/task_error".format(
                        self.config['broker_host'],self.config['broker_port']), json=message.entry_info['task'])
                    # Add to history table
                    task_history = {
                        "repo_id": message.entry_info['repo_id'],
                        "worker": self.config['id'],
                        "job_model": message.entry_info['task']['models'][0],
                        "oauth_id": self.config['zombie_id'],
                        "timestamp": datetime.datetime.now(),
                        "status": "Error",
                        "total_results": self.results_counter
                    }
                    self.helper_db.execute(self.history_table.update().where(self.history_table.c.history_id==self.history_id).values(task_history))

                    logging.info("Recorded job error for: " + str(message.entry_info['task']) + "\n")

                    # Update job process table
                    updated_job = {
                        "since_id_str": message.entry_info['repo_id'],
                        "last_count": self.results_counter,
                        "last_run": datetime.datetime.now(),
                        "analysis_state": 0
                    }
                    self.helper_db.execute(self.job_table.update().where(self.job_table.c.job_model==message.entry_info['task']['models'][0]).values(updated_job))
                    logging.info("Updated job process for model: " + message.entry_info['task']['models'][0] + "\n")

                    # Reset results counter for next task
                    self.results_counter = 0
                    pass

    def query_contributors(self, entry_info):

        """ Data collection function
        Query the GitHub API for contributors
        """
        logging.info("Querying contributors with given entry info: " + str(entry_info) + "\n")

        # Url of repo we are querying for
        url = entry_info['github_url']

        # Extract owner/repo from the url for the endpoint
        path = urlparse(url)
        split = path[2].split('/')

        owner = split[1]
        name = split[2]

        # Handles git url case by removing the extension
        if ".git" in name:
            name = name[:-4]

        # Set the base of the url and place to hold contributors to insert
        url = ("https://api.github.com/repos/" + owner + "/" + 
            name + "/contributors?per_page=100&page={}")
        contributors = []

        # Get values of tuples we already have in our table
        pseudo_key_gh = 'login'
        pseudo_key_augur = 'cntrb_login'
        table = 'contributors'
        cntrb_table_values = self.get_table_values([pseudo_key_augur, 'cntrb_email', 'cntrb_id'], [table])

        # Paginate backwards through all the contributors but starting with
        #   the first one in order to get last page # and check if 1st page 
        #   covers all of them
        i = 1
        multiple_pages = False
        while True:
            logging.info("Hitting endpoint: " + url.format(i) + " ...\n")
            r = requests.get(url=url.format(i), headers=self.headers)
            self.update_rate_limit(r)

            # If it lists the last page then there is more than 1
            if ('last' in r.links and not multiple_pages) and not self.finishing_task:
                param = r.links['last']['url'][-6:]
                i = int(param.split('=')[1]) + 1
                logging.info("Multiple pages of request, last page is " + str(i - 1) + "\n")
                multiple_pages = True
            elif not multiple_pages and not self.finishing_task:
                logging.info("Only 1 page of request\n")
            elif self.finishing_task:
                logging.info("Finishing a previous task, paginating forwards ... excess rate limit requests will be made\n")

            # The contributors endpoints has issues with getting json from request
            try:
                j = r.json()
            except Exception as e:
                logging.info("Caught exception: " + str(e) + "....\n")
                logging.info("Some kind of issue CHECKTHIS  " + url + " ...\n")
                j = json.loads(json.dumps(j))
            else:
                # logging.info("JSON seems ill-formed " + str(r) + "....\n")
                j = json.loads(json.dumps(j))

            if r.status_code == 204:
                j = []
            
            # Checking contents of requests with what we already have in the db
            # new_contributors = self.check_duplicates(j, cntrb_table_values, pseudo_key_gh)
            j = self.assign_tuple_action(j, cntrb_table_values, 
                {'cntrb_email': 'email'}, {pseudo_key_augur: pseudo_key_gh}, 'cntrb_id')
            
            if len(j) != 0:
                to_add = [obj for obj in j if obj not in contributors and obj['flag'] != 'none']
                if len(to_add) == 0 and multiple_pages and 'last' in r.links:
                    if i - 1 != int(r.links['last']['url'][-6:].split('=')[1]):
                        logging.info("No more pages with unknown contributors, breaking from pagination.\n")
                        break
                contributors += to_add

            i = i + 1 if self.finishing_task else i - 1

            if (i == 1 and multiple_pages and not self.finishing_task) or i < 1 or len(j) == 0:
                logging.info("No more pages to check, breaking from pagination.\n")
                break
            
        try:
            logging.info("Count of contributors needing insertion: " + str(len(contributors)) + "\n")

            for repo_contributor in contributors:

                # Need to hit this single contributor endpoint to get extra data including...
                #   created at
                #   i think that's it
                cntrb_url = ("https://api.github.com/users/" + repo_contributor['login'])
                logging.info("Hitting endpoint: " + cntrb_url + " ...\n")
                r = requests.get(url=cntrb_url, headers=self.headers)
                self.update_rate_limit(r)
                contributor = r.json()

                company = None
                location = None
                email = None
                if 'company' in contributor:
                    company = contributor['company']
                if 'location' in contributor:
                    location = contributor['location']
                if 'email' in contributor:
                    email = contributor['email']

                # aliasSQL = s.sql.text("""
                #     SELECT canonical_email
                #     FROM contributors_aliases
                #     WHERE alias_email = {}
                # """.format(contributor['email']))
                # rs = pd.read_sql(aliasSQL, self.db, params={})

                canonical_email = None#rs.iloc[0]["canonical_email"]

                cntrb = {
                    "cntrb_login": contributor['login'],
                    "cntrb_created_at": contributor['created_at'],
                    "cntrb_email": email,
                    "cntrb_company": company,
                    "cntrb_location": location,
                    # "cntrb_type": , dont have a use for this as of now ... let it default to null
                    "cntrb_canonical": canonical_email,
                    "gh_user_id": contributor['id'],
                    "gh_login": contributor['login'],
                    "gh_url": contributor['url'],
                    "gh_html_url": contributor['html_url'],
                    "gh_node_id": contributor['node_id'],
                    "gh_avatar_url": contributor['avatar_url'],
                    "gh_gravatar_id": contributor['gravatar_id'],
                    "gh_followers_url": contributor['followers_url'],
                    "gh_following_url": contributor['following_url'],
                    "gh_gists_url": contributor['gists_url'],
                    "gh_starred_url": contributor['starred_url'],
                    "gh_subscriptions_url": contributor['subscriptions_url'],
                    "gh_organizations_url": contributor['organizations_url'],
                    "gh_repos_url": contributor['repos_url'],
                    "gh_events_url": contributor['events_url'],
                    "gh_received_events_url": contributor['received_events_url'],
                    "gh_type": contributor['type'],
                    "gh_site_admin": contributor['site_admin'],
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                # Commit insertion to table
                if repo_contributor['flag'] == 'need_update':
                    result = self.db.execute(self.contributors_table.update().where(
                        self.history_table.c.cntrb_email==email).values(cntrb))
                    logging.info("Updated tuple in the contributors table with existing email: {}".format(email))
                    self.cntrb_id_inc = repo_contributor['pkey']
                elif repo_contributor['flag'] == 'need_insertion':
                    result = self.db.execute(self.contributors_table.insert().values(cntrb))
                    logging.info("Primary key inserted into the contributors table: {}".format(result.inserted_primary_key))
                    self.results_counter += 1
    
                    logging.info("Inserted contributor: " + contributor['login'] + "\n")

                    # Increment our global track of the cntrb id for the possibility of it being used as a FK
                    self.cntrb_id_inc = int(result.inserted_primary_key[0])

        except Exception as e:
            logging.info("Caught exception: " + str(e))
            logging.info("Contributor not defined. Please contact the manufacturers of Soylent Green " + url + " ...\n")
            logging.info("Cascading Contributor Anomalie from missing repo contributor data: " + url + " ...\n")
        else:
            if len(contributors) > 2:
                logging.info("Well, that contributor list of len {} with last 3 tuples as: {} just don't except because we hit the else-block yo\n".format(str(len(contributors)), str(contributors[-3:])))    

    def query_issues(self, entry_info):

        """ Data collection function
        Query the GitHub API for issues
        """
        logging.info("Beginning filling the issues model for repo: " + entry_info['github_url'] + "\n")
        self.record_model_process(entry_info, 'issues')

        #if str.find('github.com', str(entry_info['github_url']) < 0
        ### I have repos not on github and I need to skip them 
        #@if str.find('github.com', str(entry_info['github_url']) < 0
        #    return 

        # Contributors are part of this model, and finding all for the repo saves us 
        #   from having to add them as we discover committers in the issue process
        self.query_contributors(entry_info)

        url = entry_info['github_url']

        # Extract the owner/repo for the endpoint
        path = urlparse(url)
        split = path[2].split('/')
        owner = split[1]
        name = split[2]

        # Handle git url case by removing extension
        if ".git" in name:
            name = name[:-4]

        # Set base of endpoint url and list to hold issues needing insertion
        url = ("https://api.github.com/repos/" + owner + "/" + name + 
            "/issues?per_page=100&state=all&page={}")
        issues = []
        
        # Get issues that we already have stored
        #   Set pseudo key (something other than PK) to 
        #   check dupicates with
        pseudo_key_gh = 'id'
        pseudo_key_augur = 'gh_issue_id'
        table = 'issues'
        issue_table_values = self.get_table_values([pseudo_key_augur, 'comment_count',
            'issue_state', 'issue_id'], [table])
            
        # Paginate backwards through all the issues but get first page in order
        #   to determine if there are multiple pages and if the 1st page covers all
        i = 1
        multiple_pages = False
        while True:
            logging.info("Hitting endpoint: " + url.format(i) + " ...\n")
            r = requests.get(url=url.format(i), headers=self.headers)
            self.update_rate_limit(r)

            # Find last page so we can decrement from there
            if 'last' in r.links and not multiple_pages and not self.finishing_task:
                param = r.links['last']['url'][-6:]
                i = int(param.split('=')[1]) + 1
                logging.info("Multiple pages of request, last page is " + str(i - 1) + "\n")
                multiple_pages = True
            elif not multiple_pages and not self.finishing_task:
                logging.info("Only 1 page of request\n")
            elif self.finishing_task:
                logging.info("Finishing a previous task, paginating forwards ... excess rate limit requests will be made\n")
            
            j = r.json()

            # Checking contents of requests with what we already have in the db
            j = self.assign_tuple_action(j, issue_table_values, 
                {'comment_count': 'comments','issue_state': 'state'}, 
                {pseudo_key_augur: pseudo_key_gh}, 'issue_id')

            to_add = [obj for obj in j if obj not in issues and obj['flag'] != 'none']
            if len(to_add) == 0 and multiple_pages and 'last' in r.links:
                if i - 1 != int(r.links['last']['url'][-6:].split('=')[1]):
                    logging.info("No more pages with unknown issues, breaking from pagination.\n")
                    break
            issues += to_add

            i = i + 1 if self.finishing_task else i - 1

            # Since we already wouldve checked the first page... break
            if (i == 1 and multiple_pages and not self.finishing_task) or i < 1 or len(j) == 0:
                logging.info("No more pages to check, breaking from pagination.\n")
                break

        # Discover and remove duplicates before we start inserting
        logging.info("Count of issues needing update or insertion: " + str(len(issues)) + "\n")

        for issue_dict in issues:
            logging.info("Begin analyzing the issue with title: " + issue_dict['title'] + "\n")
            
            # Add the FK repo_id to the dict being inserted
            issue_dict['repo_id'] = entry_info['repo_id']

            # Figure out if this issue is a PR
            #   still unsure about this key value pair/what it means
            pr_id = None
            if "pull_request" in issue_dict:
                logging.info("Issue is a PR\n")
                # Right now we are just storing our issue id as the PR id if it is one
                pr_id = self.issue_id_inc
            else:
                logging.info("Issue is not a PR\n")

            # Begin on the actual issue...

            # Base of the url for comment and event endpoints
            url = ("https://api.github.com/repos/" + owner + "/" + name + "/issues/" + str(issue_dict['number']))

            # Get events ready in case the issue is closed and we need to insert the closer's id
            events_url = (url + "/events?per_page=100&page={}")
            issue_events = []
            
            # Get events that we already have stored
            #   Set pseudo key (something other than PK) to 
            #   check dupicates with
            pseudo_key_gh = 'url'
            pseudo_key_augur = 'node_url'
            table = 'issue_events'
            event_table_values = self.get_table_values([pseudo_key_augur], [table])
            
            # Paginate backwards through all the events but get first page in order
            #   to determine if there are multiple pages and if the 1st page covers all
            i = 1
            multiple_pages = False

            while True:
                logging.info("Hitting endpoint: " + events_url.format(i) + " ...\n")
                r = requests.get(url=events_url.format(i), headers=self.headers)
                self.update_rate_limit(r)

                # Find last page so we can decrement from there
                if 'last' in r.links and not multiple_pages and not self.finishing_task:
                    param = r.links['last']['url'][-6:]
                    i = int(param.split('=')[1]) + 1
                    logging.info("Multiple pages of request, last page is " + str(i - 1) + "\n")
                    multiple_pages = True
                elif not multiple_pages and not self.finishing_task:
                    logging.info("Only 1 page of request\n")
                elif self.finishing_task:
                    logging.info("Finishing a previous task, paginating forwards ... excess rate limit requests will be made\n")

                j = r.json()

                # Checking contents of requests with what we already have in the db
                new_events = self.check_duplicates(j, event_table_values, pseudo_key_gh)
                if len(new_events) == 0 and multiple_pages and 'last' in r.links:
                    if i - 1 != int(r.links['last']['url'][-6:].split('=')[1]):
                        logging.info("No more pages with unknown events, breaking from pagination.\n")
                        break
                elif len(new_events) != 0:
                    to_add = [obj for obj in new_events if obj not in issue_events]
                    issue_events += to_add

                i = i + 1 if self.finishing_task else i - 1

                # Since we already wouldve checked the first page... break
                if (i == 1 and multiple_pages and not self.finishing_task) or i < 1 or len(j) == 0:
                    logging.info("No more pages to check, breaking from pagination.\n")
                    break

            # If the issue is closed, then we search for the closing event and store the user's id
            cntrb_id = None
            if 'closed_at' in issue_dict:
                for event in issue_events:
                    if event['event'] == 'closed':
                        if event['actor'] is not None:
                            cntrb_id = self.find_id_from_login(event['actor']['login'])
                            if cntrb_id is None:
                                logging.info("SOMETHING WRONG WITH FINDING ID FROM LOGIN... using alt id of 1")
                                cntrb_id = 1
                        
            issue = {
                "repo_id": issue_dict['repo_id'],
                "reporter_id": self.find_id_from_login(issue_dict['user']['login']),
                "pull_request": pr_id,
                "pull_request_id": pr_id,
                "created_at": issue_dict['created_at'],
                "issue_title": issue_dict['title'],
                "issue_body": issue_dict['body'],
                "cntrb_id": cntrb_id,
                "comment_count": issue_dict['comments'],
                "updated_at": issue_dict['updated_at'],
                "closed_at": issue_dict['closed_at'],
                "repository_url": issue_dict['repository_url'],
                "issue_url": issue_dict['url'],
                "labels_url": issue_dict['labels_url'],
                "comments_url": issue_dict['comments_url'],
                "events_url": issue_dict['events_url'],
                "html_url": issue_dict['html_url'],
                "issue_state": issue_dict['state'],
                "issue_node_id": issue_dict['node_id'],
                "gh_issue_id": issue_dict['id'],
                "gh_issue_number": issue_dict['number'],
                "gh_user_id": issue_dict['user']['id'],
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source
            }

            # Commit insertion to the issues table
            if issue_dict['flag'] == 'need_update':
                result = self.db.execute(self.issues_table.update().where(
                    self.issues_table.c.gh_issue_id==issue_dict['id']).values(issue))
                logging.info("Updated tuple in the issues table with existing gh_issue_id: {}".format(
                    issue_dict['id']))
                self.issue_id_inc = issue_dict['pkey']
            elif issue_dict['flag'] == 'need_insertion':
                result = self.db.execute(self.issues_table.insert().values(issue))
                logging.info("Primary key inserted into the issues table: " + str(result.inserted_primary_key))
                self.results_counter += 1

                self.issue_id_inc = int(result.inserted_primary_key[0])

                logging.info("Inserted issue with our issue_id being: " + str(self.issue_id_inc) + 
                    " and title of: " + issue_dict['title'] + " and gh_issue_num of: " + str(issue_dict['number']) + "\n")

            # Check if the assignee key's value is already recorded in the assignees key's value
            #   Create a collective list of unique assignees
            collected_assignees = issue_dict['assignees']
            if issue_dict['assignee'] not in collected_assignees:
                collected_assignees.append(issue_dict['assignee'])

            # Handles case if there are no assignees
            if collected_assignees[0] is not None:
                logging.info("Count of assignees to insert for this issue: " + str(len(collected_assignees)) + "\n")
                for assignee_dict in collected_assignees:

                    assignee = {
                        "issue_id": self.issue_id_inc,
                        "cntrb_id": self.find_id_from_login(assignee_dict['login']),
                        "tool_source": self.tool_source,
                        "tool_version": self.tool_version,
                        "data_source": self.data_source,
                        "issue_assignee_src_id": assignee_dict['id'],
                        "issue_assignee_src_node": assignee_dict['node_id']
                    }
                    # Commit insertion to the assignee table
                    result = self.db.execute(self.issue_assignees_table.insert().values(assignee))
                    logging.info("Primary key inserted to the issues_assignees table: " + str(result.inserted_primary_key))
                    self.results_counter += 1

                    logging.info("Inserted assignee for issue id: " + str(self.issue_id_inc) + 
                        " with login/cntrb_id: " + assignee_dict['login'] + " " + str(assignee['cntrb_id']) + "\n")
            else:
                logging.info("Issue does not have any assignees\n")

            # Insert the issue labels to the issue_labels table
            for label_dict in issue_dict['labels']:
                desc = None
                if 'description' in label_dict:
                    desc = label_dict['description']
                label = {
                    "issue_id": self.issue_id_inc,
                    "label_text": label_dict["name"],
                    "label_description": desc,
                    "label_color": label_dict['color'],
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source,
                    "label_src_id": label_dict['id'],
                    "label_src_node_id": label_dict['node_id']
                }

                result = self.db.execute(self.issue_labels_table.insert().values(label))
                logging.info("Primary key inserted into the issue_labels table: " + str(result.inserted_primary_key))
                self.results_counter += 1

                logging.info("Inserted issue label with text: " + label_dict['name'] + "\n")


            #### Messages/comments and events insertion 
            #    (we collected events above but never inserted them)

            comments_url = (url + "/comments?page={}&per_page=100")
            issue_comments = []
            
            # Get comments that we already have stored
            #   Set pseudo key (something other than PK) to 
            #   check dupicates with
            pseudo_key_gh = 'created_at'
            pseudo_key_augur = 'msg_timestamp'
            table = 'message'
            issue_comments_table_values = self.get_table_values([pseudo_key_augur], [table])
            
            # Paginate backwards through all the comments but get first page in order
            #   to determine if there are multiple pages and if the 1st page covers all
            i = 1
            multiple_pages = False

            while True:
                logging.info("Hitting endpoint: " + comments_url.format(i) + " ...\n")
                r = requests.get(url=comments_url.format(i), headers=self.headers)
                self.update_rate_limit(r)

                # Find last page so we can decrement from there
                if 'last' in r.links and not multiple_pages and not self.finishing_task:
                    param = r.links['last']['url'][-6:]
                    i = int(param.split('=')[1]) + 1
                    logging.info("Multiple pages of request, last page is " + str(i - 1) + "\n")
                    multiple_pages = True
                elif not multiple_pages and not self.finishing_task:
                    logging.info("Only 1 page of request\n")
                elif self.finishing_task:
                    logging.info("Finishing a previous task, paginating forwards ... excess rate limit requests will be made\n")

                j = r.json()

                # Checking contents of requests with what we already have in the db
                new_comments = self.check_duplicates(j, event_table_values, pseudo_key_gh)
                if len(new_comments) == 0 and multiple_pages and 'last' in r.links:
                    if i - 1 != int(r.links['last']['url'][-6:].split('=')[1]):
                        logging.info("No more pages with unknown comments, breaking from pagination.\n")
                        break
                elif len(new_comments) != 0:
                    to_add = [obj for obj in new_comments if obj not in issue_comments]
                    issue_comments += to_add

                i = i + 1 if self.finishing_task else i - 1

                # Since we already wouldve checked the first page... break
                if (i == 1 and multiple_pages and not self.finishing_task) or i < 1 or len(j) == 0:
                    logging.info("No more pages to check, breaking from pagination.\n")
                    break

            # Add the FK of our cntrb_id to each comment dict to be inserted
            if len(issue_comments) != 0:
                for comment in issue_comments:
                    # logging.info("user: "+str(comment['user']) + "...\n") 
                    if "user" in comment:
                        if "login" in comment['user']:
                            comment['cntrb_id'] = self.find_id_from_login(comment['user']['login'])
                
            logging.info("Number of comments needing insertion: {}\n".format(len(issue_comments)))

            for comment in issue_comments:
                issue_comment = {
                    "pltfrm_id": 25150,
                    "msg_text": comment['body'],
                    "msg_timestamp": comment['created_at'],
                    "cntrb_id": self.find_id_from_login(comment['user']['login']),
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                result = self.db.execute(self.message_table.insert().values(issue_comment))
                logging.info("Primary key inserted into the message table: {}".format(result.inserted_primary_key))
                self.results_counter += 1
                self.msg_id_inc = int(result.inserted_primary_key[0])

                logging.info("Inserted issue comment: " + comment['body'] + "\n")

                ### ISSUE MESSAGE REF TABLE ###

                issue_message_ref = {
                    "issue_id": self.issue_id_inc,
                    "msg_id": self.msg_id_inc,
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source,
                    "issue_msg_ref_src_comment_id": comment['id'],
                    "issue_msg_ref_src_node_id": comment['node_id']
                }

                result = self.db.execute(self.issues_message_ref_table.insert().values(issue_message_ref))
                logging.info("Primary key inserted into the issue_message_ref table: {}".format(result.inserted_primary_key))
                self.results_counter += 1


            for event in issue_events:
                if event['actor'] is not None:
                    event['cntrb_id'] = self.find_id_from_login(event['actor']['login'])
                    if event['cntrb_id'] is None:
                        logging.info("SOMETHING WRONG WITH FINDING ID FROM LOGIN")
                        event['cntrb_id'] = 1
                else:
                    event['cntrb_id'] = 1
        
            logging.info("Number of events needing insertion: " + str(len(issue_events)) + "\n")

            for event in issue_events:
                issue_event = {
                    "issue_event_src_id": event['id'],
                    "issue_id": self.issue_id_inc,
                    "node_id": event['node_id'],
                    "node_url": event['url'],
                    "cntrb_id": event['cntrb_id'],
                    "created_at": event['created_at'],
                    "action": event["event"],
                    "action_commit_hash": event["commit_id"],
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                result = self.db.execute(self.issue_events_table.insert().values(issue_event))
                logging.info("Primary key inserted into the issue_events table: " + str(result.inserted_primary_key))
                self.results_counter += 1

                logging.info("Inserted issue event: " + event['event'] + " " + str(self.issue_id_inc) + "\n")
            
            self.issue_id_inc += 1

        #Register this task as completed
        self.register_task_completion(entry_info, "issues")

            
    def get_table_values(self, cols, tables):
        table_str = tables[0]
        del tables[0]
        col_str = cols[0]
        del cols[0]
        for table in tables:
            table_str += ", " + table
        for col in cols:
            col_str += ", " + col
        tableValuesSQL = s.sql.text("""
            SELECT {} FROM {}
            """.format(col_str, table_str))
        values = pd.read_sql(tableValuesSQL, self.db, params={})
        return values

    def find_id_from_login(self, login):
        idSQL = s.sql.text("""
            SELECT cntrb_id FROM contributors WHERE cntrb_login = '{}'
            """.format(login))
        rs = pd.read_sql(idSQL, self.db, params={})
        data_list = [list(row) for row in rs.itertuples(index=False)] 
        try:
            return data_list[0][0]
        except:
            logging.info("contributor needs to be added...")
            cntrb_url = ("https://api.github.com/users/" + login)
            logging.info("Hitting endpoint: {} ...\n".format(cntrb_url))
            r = requests.get(url=cntrb_url, headers=self.headers)
            self.update_rate_limit(r)
            contributor = r.json()

            company = None
            location = None
            email = None
            if 'company' in contributor:
                company = contributor['company']
            if 'location' in contributor:
                location = contributor['location']
            if 'email' in contributor:
                email = contributor['email']

            # aliasSQL = s.sql.text("""
            #     SELECT canonical_email
            #     FROM contributors_aliases
            #     WHERE alias_email = {}
            # """.format(contributor['email']))
            # rs = pd.read_sql(aliasSQL, self.db, params={})

            canonical_email = None#rs.iloc[0]["canonical_email"]

            cntrb = {
                "cntrb_login": contributor['login'] if 'login' in contributor else None,
                "cntrb_email": email,
                "cntrb_company": company,
                "cntrb_location": location,
                "cntrb_created_at": contributor['created_at'],                
                "cntrb_canonical": canonical_email,
                "gh_user_id": contributor['id'],
                "gh_login": contributor['login'],
                "gh_url": contributor['url'],
                "gh_html_url": contributor['html_url'],
                "gh_node_id": contributor['node_id'],
                "gh_avatar_url": contributor['avatar_url'],
                "gh_gravatar_id": contributor['gravatar_id'],
                "gh_followers_url": contributor['followers_url'],
                "gh_following_url": contributor['following_url'],
                "gh_gists_url": contributor['gists_url'],
                "gh_starred_url": contributor['starred_url'],
                "gh_subscriptions_url": contributor['subscriptions_url'],
                "gh_organizations_url": contributor['organizations_url'],
                "gh_repos_url": contributor['repos_url'],
                "gh_events_url": contributor['events_url'],
                "gh_received_events_url": contributor['received_events_url'],
                "gh_type": contributor['type'],
                "gh_site_admin": contributor['site_admin'],
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source
            }
            result = self.db.execute(self.contributors_table.insert().values(cntrb))
            logging.info("Primary key inserted into the contributors table: " + str(result.inserted_primary_key))
            self.results_counter += 1
            self.cntrb_id_inc = int(result.inserted_primary_key[0])

            logging.info("Inserted contributor: " + contributor['login'] + "\n")
            
            return self.find_id_from_login(login)


    def update_rate_limit(self, response):
        # Try to get rate limit from request headers, sometimes it does not work (GH's issue)
        #   In that case we just decrement from last recieved header count
        try:
            self.rate_limit = int(response.headers['X-RateLimit-Remaining'])
            logging.info("Recieved rate limit from headers\n")
        except:
            self.rate_limit -= 1
            logging.info("Headers did not work, had to decrement\n")
        logging.info("Updated rate limit, you have: " + 
            str(self.rate_limit) + " requests remaining.\n")
        if self.rate_limit <= 0:
            reset_time = response.headers['X-RateLimit-Reset']
            time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
            logging.info("Rate limit exceeded, waiting " + 
                str(time_diff.total_seconds()) + " seconds.\n")
            time.sleep(time_diff.total_seconds())
            self.rate_limit = int(response.headers['X-RateLimit-Limit'])
        
    def register_task_completion(self, entry_info, model):
        # Task to send back to broker
        task_completed = {
            'worker_id': self.config['id'],
            'job_type': self.working_on,
            'repo_id': entry_info['repo_id'],
            'github_url': entry_info['github_url']
        }
        # Add to history table
        task_history = {
            "repo_id": entry_info['repo_id'],
            "worker": self.config['id'],
            "job_model": model,
            "oauth_id": self.config['zombie_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Success",
            "total_results": self.results_counter
        }
        self.helper_db.execute(self.history_table.update().where(
            self.history_table.c.history_id==self.history_id).values(task_history))

        logging.info("Recorded job completion for: " + str(task_completed) + "\n")

        # Update job process table
        updated_job = {
            "since_id_str": entry_info['repo_id'],
            "last_count": self.results_counter,
            "last_run": datetime.datetime.now(),
            "analysis_state": 0
        }
        self.helper_db.execute(self.job_table.update().where(
            self.job_table.c.job_model==model).values(updated_job))
        logging.info("Update job process for model: " + model + "\n")

        # Notify broker of completion
        logging.info("Telling broker we completed task: " + str(task_completed) + "\n\n" + 
            "This task inserted: " + str(self.results_counter) + " tuples.\n\n")

        requests.post('http://{}:{}/api/unstable/completed_task'.format(
            self.config['broker_host'],self.config['broker_port']), json=task_completed)

        # Reset results counter for next task
        self.results_counter = 0

    def record_model_process(self, entry_info, model):
        task_history = {
            "repo_id": entry_info['repo_id'],
            "worker": self.config['id'],
            "job_model": model,
            "oauth_id": self.config['zombie_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Stopped",
            "total_results": self.results_counter
        }
        if self.finishing_task:
            result = self.helper_db.execute(self.history_table.update().where(
                self.history_table.c.history_id==self.history_id).values(task_history))
        else:
            result = self.helper_db.execute(self.history_table.insert().values(task_history))
            logging.info("Record incomplete history tuple: {}".format(result.inserted_primary_key))
            self.history_id = int(result.inserted_primary_key[0])
            
    def check_duplicates(self, new_data, table_values, key):
        need_insertion = []
        for obj in new_data:
            if type(obj) == dict:
                if table_values.isin([obj[key]]).any().any():
                    logging.info("Tuple with github's {} key value already".format(key) +
                        "exists in our db: {}\n".format(str(obj[key])))
                else:
                    need_insertion.append(obj)
        logging.info("Page recieved has {} tuples, while filtering duplicates this ".format(str(len(new_data))) +
            " was reduced to {} tuples.\n".format(str(len(need_insertion))))
        return need_insertion

    def assign_tuple_action(self, new_data, table_values, update_col_map, duplicate_key_map, db_pkey):
        """ map objects => { *our db col* : *gh json key*} """
        need_insertion_count = 0
        for obj in new_data:
            if type(obj) == dict:
                obj['flag'] = 'none'
                db_dupe_key = list(duplicate_key_map.keys())[0]
                if table_values.isin([obj[duplicate_key_map[db_dupe_key]]]).any().any():
                    logging.info("Tuple with github's {} key value already exists ".format(db_dupe_key) +
                        "exists in our db: {}\n".format(obj[duplicate_key_map[db_dupe_key]]))
                    existing_tuple = table_values[table_values[db_dupe_key].isin(
                        [obj[duplicate_key_map[db_dupe_key]]])].to_dict('records')[0]
                    for col in update_col_map.keys():
                        if update_col_map[col] in obj:
                            if obj[update_col_map[col]] != existing_tuple[col]:
                                logging.info("Tuple {} needs an " +
                                    "update for column: {}\n".format(obj[duplicate_key_map[db_dupe_key]], col, obj))
                                obj['flag'] = 'need_update'
                                obj['pkey'] = existing_tuple[db_pkey]
                else:
                    obj['flag'] = 'need_insertion'
                    need_insertion_count += 1
        logging.info("Page recieved has {} tuples, while filtering duplicates this ".format(len(new_data)) +
            "was reduced to {} tuples.\n".format(need_insertion_count))
        return new_data
