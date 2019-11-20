from multiprocessing import Process, Queue
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
import requests, time, logging, json, os
from datetime import datetime
from workers.standard_methods import register_task_completion, register_task_failure, connect_to_broker, update_gh_rate_limit, record_model_process

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
        self.working_on = None
        self.db = None
        self.table = None
        self.tool_source = 'GitHub API Worker'
        self.tool_version = '0.0.3' # See __init__.py
        self.data_source = 'GitHub API'
        self.results_counter = 0
        self.history_id = None
        self.finishing_task = False

        self.specs = {
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
            'issue_message_ref', 'issue_events','issue_assignees','contributors_aliases'])
        helper_metadata.reflect(self.helper_db, only=['worker_history', 'worker_job', 'worker_oauth'])

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

        # Organize different api keys/oauths available
        self.oauths = []
        self.headers = None

        # Endpoint to hit solely to retrieve rate limit information from headers of the response
        url = "https://api.github.com/users/gabe-heim"

        # Make a list of api key in the config combined w keys stored in the database
        oauthSQL = s.sql.text("""
            SELECT * FROM worker_oauth WHERE access_token <> '{}'
        """.format(config['key']))
        for oauth in [{'oauth_id': 0, 'access_token': config['key']}] + json.loads(pd.read_sql(oauthSQL, self.helper_db, params={}).to_json(orient="records")):
            self.headers = {'Authorization': 'token %s' % oauth['access_token']}
            logging.info("Getting rate limit info for oauth: {}".format(oauth))
            response = requests.get(url=url, headers=self.headers)
            self.oauths.append({
                    'oauth_id': oauth['oauth_id'],
                    'access_token': oauth['access_token'],
                    'rate_limit': int(response.headers['X-RateLimit-Remaining']),
                    'seconds_to_reset': (datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])) - datetime.now()).total_seconds()
                })
            logging.info("Found OAuth available for use: {}".format(self.oauths[-1]))

        if len(self.oauths) == 0:
            logging.info("No API keys detected, please include one in your config or in the worker_oauths table in the augur_operations schema of your database\n")

        # First key to be used will be the one specified in the config (first element in 
        #   self.oauths array will always be the key in use)
        self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}

        # Send broker hello message
        connect_to_broker(self, logging.getLogger())
        

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
            logging.info("focused task is OFF\n")
        
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
        self._child = Process(target=self.collect, args=())
        self._child.start()
            
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
                """.format(message['given']['github_url']))
            repo_id = int(pd.read_sql(repoUrlSQL, self.db, params={}).iloc[0]['repo_id'])

            try:
                if message['models'][0] == 'contributors':
                    self.contributor_model(message, repo_id)
                if message['models'][0] == 'issues':
                    self.issues_model(message, repo_id)
            except Exception as e:
                register_task_failure(self, logging, message, repo_id, e)
                pass

    def insert_commit_contributors(self, entry_info):
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
        result = self.db.execute(self.contributors_table.insert().values(cntrb))
        logging.info("Primary key inserted into the contributors table: {}".format(result.inserted_primary_key))
        self.results_counter += 1

        logging.info("Inserted contributor: " + contributor['login'] + "\n")

        # Increment our global track of the cntrb id for the possibility of it being used as a FK
        self.cntrb_id_inc = int(result.inserted_primary_key[0])

    def insert_facade_contributors(self, entry_info):
        logging.info("Beginning process to insert contributors from facade commits for repo w entry info: {}\n".format(entry_info))

        # Get all distinct combinations of emails and names by querying the repo's commits
        userSQL = s.sql.text("""
            SELECT distinct(cmt_author_email) AS email, cmt_author_name AS name, cmt_author_affiliation AS affiliation
            FROM commits
            WHERE repo_id = {}
            AND cmt_author_email NOT IN (SELECT cntrb_email AS e FROM contributors)
            UNION
            SELECT distinct(cmt_committer_email) AS email, cmt_committer_name AS name, cmt_committer_affiliation AS affiliation
            FROM commits
            WHERE repo_id = {}
            AND cmt_committer_email NOT IN (SELECT cntrb_email AS e FROM contributors)
        """.format(repo_id,repo_id))

        commit_cntrbs = json.loads(pd.read_sql(userSQL, self.db, params={}).to_json(orient="records"))
        logging.info("We found {} distinct contributors needing insertion (repo_id = {})".format(
            len(commit_cntrbs), repo_id))

    def contributor_model(self, entry_info, repo_id):
        # self.insert_facade_contributors(self, entry_info)

        logging.info("Searching users for commits from the facade worker for repo with entry info: {}\n".format(entry_info))

        # Get all distinct combinations of emails and names by querying the repo's commits
        userSQL = s.sql.text("""
            SELECT cmt_author_name AS commit_name, cntrb_id, cmt_author_raw_email AS commit_email, cntrb_email, 
                cntrb_full_name, cntrb_login, cntrb_canonical, 
                cntrb_company, cntrb_created_at::timestamp, cntrb_type, cntrb_fake, cntrb_deleted, cntrb_long, 
                cntrb_lat, cntrb_country_code, cntrb_state, cntrb_city, cntrb_location, gh_user_id, 
                gh_login, gh_url, gh_html_url, gh_node_id, gh_avatar_url, gh_gravatar_id, gh_followers_url, 
                gh_following_url, gh_gists_url, gh_starred_url, gh_subscriptions_url, gh_organizations_url, 
                gh_repos_url, gh_events_url, gh_received_events_url, gh_type, gh_site_admin
            FROM commits, contributors
            WHERE repo_id = {}
            AND contributors.cntrb_full_name = cmt_author_name
                UNION
            SELECT cmt_author_name AS commit_name, cntrb_id, cmt_author_raw_email AS commit_email, cntrb_email, 
                cntrb_full_name, cntrb_login, cntrb_canonical, 
                cntrb_company, cntrb_created_at::timestamp, cntrb_type, cntrb_fake, cntrb_deleted, cntrb_long, 
                cntrb_lat, cntrb_country_code, cntrb_state, cntrb_city, cntrb_location, gh_user_id, 
                gh_login, gh_url, gh_html_url, gh_node_id, gh_avatar_url, gh_gravatar_id, gh_followers_url, 
                gh_following_url, gh_gists_url, gh_starred_url, gh_subscriptions_url, gh_organizations_url, 
                gh_repos_url, gh_events_url, gh_received_events_url, gh_type, gh_site_admin
            FROM commits, contributors
            WHERE repo_id = {}
            AND contributors.cntrb_email = cmt_author_raw_email
                UNION
            SELECT cmt_committer_name AS commit_name, cntrb_id, cmt_committer_raw_email AS commit_email, 
                cntrb_email, cntrb_full_name, cntrb_login, cntrb_canonical, 
                cntrb_company, cntrb_created_at::timestamp, cntrb_type, cntrb_fake, cntrb_deleted, cntrb_long, 
                cntrb_lat, cntrb_country_code, cntrb_state, cntrb_city, cntrb_location, gh_user_id, 
                gh_login, gh_url, gh_html_url, gh_node_id, gh_avatar_url, gh_gravatar_id, gh_followers_url, 
                gh_following_url, gh_gists_url, gh_starred_url, gh_subscriptions_url, gh_organizations_url, 
                gh_repos_url, gh_events_url, gh_received_events_url, gh_type, gh_site_admin
            FROM commits, contributors
            WHERE repo_id = {}
            AND contributors.cntrb_full_name = cmt_committer_name
                UNION
            SELECT cmt_committer_name AS commit_name, cntrb_id, cmt_committer_raw_email AS commit_email, 
                cntrb_email, cntrb_full_name, cntrb_login, cntrb_canonical, 
                cntrb_company, cntrb_created_at::timestamp, cntrb_type, cntrb_fake, cntrb_deleted, cntrb_long, 
                cntrb_lat, cntrb_country_code, cntrb_state, cntrb_city, cntrb_location, gh_user_id, 
                gh_login, gh_url, gh_html_url, gh_node_id, gh_avatar_url, gh_gravatar_id, gh_followers_url, 
                gh_following_url, gh_gists_url, gh_starred_url, gh_subscriptions_url, gh_organizations_url, 
                gh_repos_url, gh_events_url, gh_received_events_url, gh_type, gh_site_admin
            FROM commits, contributors
            WHERE repo_id = {}
            AND contributors.cntrb_email = cmt_committer_raw_email
                ORDER BY cntrb_id
        """.format(repo_id,repo_id,repo_id,repo_id))

        commit_cntrbs = json.loads(pd.read_sql(userSQL, self.db, params={}).to_json(orient="records"))
        logging.info("We found {} distinct emails to search for in this repo (repo_id = {})".format(
            len(commit_cntrbs), repo_id))

        # For every unique commit contributor info combination...
        for tuple in commit_cntrbs:
            # If cntrb_full_name column is not filled, go ahead and fill it bc we have that info
            if not tuple['cntrb_full_name'] and tuple['commit_name'] and tuple['cntrb_id']:
                name_col = {
                    'cntrb_full_name': tuple['commit_name']
                }

                result = self.db.execute(self.contributors_table.update().where(
                    self.contributors_table.c.cntrb_id==tuple['cntrb_id']).values(name_col))
                logging.info("Inserted cntrb_full_name column for existing tuple in the contributors "
                    "table with email: {}\n".format(tuple['cntrb_email']))

            # If cntrb_canonical column is not filled, go ahead and fill it w main email bc 
            #   an old version of the worker did not
            if not tuple['cntrb_canonical'] and tuple['cntrb_email']:
                canonical_col = {
                    'cntrb_canonical': tuple['cntrb_email']
                }

                result = self.db.execute(self.contributors_table.update().where(
                    self.contributors_table.c.cntrb_id==tuple['cntrb_id']).values(canonical_col))
                logging.info("Inserted cntrb_canonical column for existing tuple in the contributors "
                    "table with email: {}\n".format(tuple['cntrb_email']))

            match = None
            def search_users():
                # try/except to handle case of a first/last split or just first name
                try:
                    cmt_cntrb = {'fname': tuple['commit_name'].split()[0], 'lname': tuple['commit_name'].split()[1],
                        'email': tuple['commit_email']}
                    url = 'https://api.github.com/search/users?q={}+in:email+fullname:{}+{}'.format(
                        cmt_cntrb['email'],cmt_cntrb['fname'],cmt_cntrb['lname'])
                except:
                    cmt_cntrb = {'fname': tuple['commit_name'].split()[0], 'lname': '',
                        'email': tuple['commit_email']}
                    url = 'https://api.github.com/search/users?q={}+in:email+fullname:{}'.format(
                        cmt_cntrb['email'],cmt_cntrb['fname'])

                logging.info("Hitting endpoint: " + url + " ...\n")
                r = requests.get(url=url, headers=self.headers)
                update_gh_rate_limit(self, logging, r)
                results = r.json()

                # If no matches or bad response, continue with other contributors
                if 'total_count' not in results:
                    logging.info("Search query returned an empty response, moving on...\n")
                    return
                if results['total_count'] == 0:
                    logging.info("Search query did not return any results, moving on...\n")
                    return

                logging.info("When searching for a contributor with info {}, we found the following users: {}\n".format(
                    cmt_cntrb, results))

                # Grab first result and make sure it has the highest match score
                match = results['items'][0]
                for item in results['items']:
                    if item['score'] > match['score']:
                        match = item

                cntrb_url = ("https://api.github.com/users/" + match['login'])
                logging.info("Hitting endpoint: " + cntrb_url + " ...\n")
                r = requests.get(url=cntrb_url, headers=self.headers)
                update_gh_rate_limit(self, logging, r)
                contributor = r.json()

                # Fill in all github information
                cntrb_gh_info = {
                    "cntrb_login": contributor['login'],
                    "cntrb_created_at": contributor['created_at'],
                    "cntrb_email": email,
                    "cntrb_company": contributor['company'] if 'company' in contributor else None,
                    "cntrb_location": contributor['location'] if 'location' in contributor else None,
                    # "cntrb_type": , dont have a use for this as of now ... let it default to null
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
                result = self.db.execute(self.contributors_table.update().where(
                    self.contributors_table.c.cntrb_id==tuple['cntrb_id']).values(cntrb_gh_info))
                logging.info("Updated existing tuple in the contributors table with github info after "
                    "a successful search query on a facade commit's author : {} {}\n".format(tuple, cntrb_gh_info))

            # If the contributor already has a login, there is no use in performing the github search
            if not tuple['cntrb_login']:
                search_users()

            # If this is true, then it is an alias bc the commit has diff email than canonical
            if tuple['commit_email'] != tuple['cntrb_email']:
                cntrb_email = tuple['cntrb_email']
                commit_email = tuple['commit_email']
                cntrb_id = tuple['cntrb_id']
                # Check existing contributors table tuple
                existing_tuples = self.retrieve_tuple({'cntrb_email': tuple['commit_email']}, ['contributors'])
                if len(existing_tuples) < 1:
                    # Prepare tuple for insertion to contributor table (build it off of the tuple queried)
                    cntrb = tuple
                    cntrb['cntrb_created_at'] = datetime.fromtimestamp(cntrb['cntrb_created_at']/1000)
                    cntrb['cntrb_email'] = tuple['commit_email']
                    cntrb["tool_source"] = self.tool_source
                    cntrb["tool_version"] = self.tool_version
                    cntrb["data_source"] = self.data_source
                    del cntrb['commit_name']
                    del cntrb['commit_email']
                    del cntrb['cntrb_id']
                    
                    result = self.db.execute(self.contributors_table.insert().values(cntrb))
                    logging.info("Inserted alias into the contributors table with email: {}\n".format(cntrb['cntrb_email']))
                    self.results_counter += 1
                    self.cntrb_id_inc = int(result.inserted_primary_key[0])
                    alias_id = self.cntrb_id_inc
                elif len(existing_tuples) > 1:
                    logging.info("THERE IS A CASE FOR A DUPLICATE CONTRIBUTOR in the contributors table AND NEED TO ADD DELETION LOGIC\n")
                else:
                    alias_id = existing_tuples[0]['cntrb_id']

                # Now check existing alias table tuple
                existing_tuples = self.retrieve_tuple({'alias_email': commit_email}, ['contributors_aliases'])
                if len(existing_tuples) == 0:
                    alias_tuple = {
                        'cntrb_id': cntrb_id,
                        'cntrb_a_id': alias_id,
                        'canonical_email': cntrb_email,
                        'alias_email': commit_email,
                        'cntrb_active': 1,
                        "tool_source": self.tool_source,
                        "tool_version": self.tool_version,
                        "data_source": self.data_source
                    }
                    result = self.db.execute(self.contributors_aliases_table.insert().values(alias_tuple))
                    self.results_counter += 1
                    logging.info("Inserted alias with email: {}\n".format(commit_email))
                if len(existing_tuples) > 1:
                    logging.info("THERE IS A CASE FOR A DUPLICATE CONTRIBUTOR in the alias table AND NEED TO ADD DELETION LOGIC\n")

        #Register this task as completed
        register_task_completion(self, logging, entry_info, repo_id, "contributors")

    def query_contributors(self, entry_info, repo_id):

        """ Data collection function
        Query the GitHub API for contributors
        """
        logging.info("Querying contributors with given entry info: " + str(entry_info) + "\n")

        github_url = entry_info['given']['github_url']

        # Extract owner/repo from the url for the endpoint
        path = urlparse(github_url)
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
            update_gh_rate_limit(self, logging, r)

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
                update_gh_rate_limit(self, logging, r)
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
                    canonical_email = contributor['email']

                # aliasSQL = s.sql.text("""
                #     SELECT canonical_email
                #     FROM contributors_aliases
                #     WHERE alias_email = {}
                # """.format(contributor['email']))
                # rs = pd.read_sql(aliasSQL, self.db, params={})

                #canonical_email = rs.iloc[0]["canonical_email"]

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

    def issues_model(self, entry_info, repo_id):

        """ Data collection function
        Query the GitHub API for issues
        """

        github_url = entry_info['given']['github_url']

        logging.info("Beginning filling the issues model for repo: " + github_url + "\n")
        record_model_process(self, logging, repo_id, 'issues')

        #if str.find('github.com', str(github_url) < 0
        ### I have repos not on github and I need to skip them 
        #@if str.find('github.com', str(github_url) < 0
        #    return 

        # Contributors are part of this model, and finding all for the repo saves us 
        #   from having to add them as we discover committers in the issue process
        self.query_contributors(entry_info, repo_id)

        # Extract the owner/repo for the endpoint
        path = urlparse(github_url)
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
            update_gh_rate_limit(self, logging, r)

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

            if len(j) == 0:
                break
                
            # Checking contents of requests with what we already have in the db
            j = self.assign_tuple_action(j, issue_table_values, 
                {'comment_count': 'comments','issue_state': 'state'}, 
                {pseudo_key_augur: pseudo_key_gh}, 'issue_id')
            if not j:
                continue
            to_add = [obj for obj in j if obj not in issues and obj['flag'] != 'none']
            if len(to_add) == 0 and multiple_pages and 'last' in r.links:
                logging.info("{}".format(r.links['last']))
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
            issue_dict['repo_id'] = repo_id

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
                update_gh_rate_limit(self, logging, r)

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
                update_gh_rate_limit(self, logging, r)

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
                new_comments = self.check_duplicates(j, issue_comments_table_values, pseudo_key_gh)
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
        register_task_completion(self, logging.getLogger(), entry_info, repo_id, "issues")
            
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

    def retrieve_tuple(self, key_values, tables):
        table_str = tables[0]
        del tables[0]

        key_values_items = list(key_values.items())
        for col, value in [key_values_items[0]]:
            where_str = col + " = '" + value + "'"
        del key_values_items[0]

        for col, value in key_values_items:
            where_str += ' AND ' + col + " = '" + value + "'"
        for table in tables:
            table_str += ", " + table

        retrieveTupleSQL = s.sql.text("""
            SELECT * FROM {} WHERE {}
            """.format(table_str, where_str))
        values = json.loads(pd.read_sql(retrieveTupleSQL, self.db, params={}).to_json(orient="records"))
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
            update_gh_rate_limit(self, logging, r)
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
