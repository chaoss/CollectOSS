""" Helper methods constant across all workers """
import requests, datetime, time, traceback, json, os, sys, math, logging
from logging import FileHandler, Formatter, StreamHandler
from multiprocessing import Process, Queue
import sqlalchemy as s
import pandas as pd
from pathlib import Path
from urllib.parse import urlparse
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from augur.config import AugurConfig
from augur.logging import verbose_formatter, generic_formatter

class Worker():

    ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self, worker_type, config={}, given=[], models=[], data_tables=[], operations_tables=[]):

        self.worker_type = worker_type
        self._task = None # task currently being worked on (dict)
        self._child = None # process of currently running task (multiprocessing process)
        self._queue = Queue() # tasks stored here 1 at a time (in a mp queue so it can translate across multiple processes)
        self.data_tables = data_tables
        self.operations_tables = operations_tables
        self._root_augur_dir = Worker.ROOT_AUGUR_DIR

        # count of tuples inserted in the database (to store stats for each task in op tables)
        self.results_counter = 0 

        # if we are finishing a previous task, certain operations work differenty
        self.finishing_task = False 

        # Update config with options that are general and not specific to any worker
        self.augur_config = AugurConfig(self._root_augur_dir)

        self.config = { 
                "worker_type": self.worker_type,
                "host": self.augur_config.get_value("Server", "host"),
                'gh_api_key': self.augur_config.get_value('Database', 'key'),
                'offline_mode': False
            }
        self.config.update(self.augur_config.get_section("Development"))

        try:
            worker_defaults = self.augur_config.get_default_config()["Workers"][self.config["worker_type"]]
            self.config.update(worker_defaults)
        except KeyError as e:
            logging.warn("Could not get default configuration for {}", self.config["worker_type"])

        worker_info = self.augur_config.get_value("Workers", self.config["worker_type"])
        self.config.update(worker_info)

        worker_port = self.config["port"]
        while True:
            try:
                r = requests.get("http://{}:{}/AUGWOP/heartbeat".format(self.config["host"], worker_port)).json()
                if 'status' in r:
                    if r['status'] == 'alive':
                        worker_port += 1
            except:
                break

        logfile_dir = f"{self._root_augur_dir}/logs/workers/{self.worker_type}/"
        server_logfile = logfile_dir + "{}_{}_server.log".format(self.worker_type, worker_port)
        collection_logfile = logfile_dir + "{}_{}_collection.log".format(self.worker_type, worker_port)
        self.config.update({ 
            "port": worker_port,
            "id": "com.augurlabs.core.{}.{}".format(self.worker_type, worker_port),
            "logfile_dir": logfile_dir,
            "server_logfile": server_logfile,
            "collection_logfile": collection_logfile,
            "capture_output": True,
            'location': 'http://{}:{}'.format(self.config["host"], worker_port),
            'port_broker': self.augur_config.get_value('Server', 'port'),
            'host_broker': self.augur_config.get_value('Server', 'host'),
            'host_database': self.augur_config.get_value('Database', 'host'),
            'port_database': self.augur_config.get_value('Database', 'port'),
            'user_database': self.augur_config.get_value('Database', 'user'),
            'name_database': self.augur_config.get_value('Database', 'name'),
            'password_database': self.augur_config.get_value('Database', 'password')
        })
        self.config.update(config)

        # Initialize logging in the main process
        self.initialize_logging()

        # Clear log contents from previous runs
        open(self.config["server_logfile"], "w").close()
        open(self.config["collection_logfile"], "w").close()

        # Get configured collection logger
        self.logger = logging.getLogger(self.config["id"])
        self.logger.info('Worker (PID: {}) initializing...'.format(str(os.getpid())))

        self.given = given
        self.models = models
        self.specs = {
            'id': self.config['id'], # what the broker knows this worker as
            'location': self.config['location'], # host + port worker is running on (so broker can send tasks here)
            'qualifications':  [
                {
                    'given': self.given, # type of repo this worker can be given as a task
                    'models': self.models # models this worker can fill for a repo as a task
                }
            ],
            'config': self.config
        }

        # Send broker hello message
        if self.config["offline_mode"] is False:
            self.connect_to_broker()

    def __repr__(self):
        return f"{self.config['id']}"

    def initialize_logging(self):
        self.config["log_level"] = self.config["log_level"].upper()
        formatter = generic_formatter
        if self.config["verbose"] is True:
            formatter = verbose_formatter

        Path(self.config["logfile_dir"]).mkdir(exist_ok=True)

        collection_file_handler = FileHandler(filename=self.config["collection_logfile"], mode="a")
        collection_file_handler.setFormatter(formatter)
        collection_file_handler.setLevel(self.config["log_level"])

        self.logger = logging.getLogger(self.config["id"])
        self.logger.handlers = []
        self.logger.addHandler(collection_file_handler)
        self.logger.setLevel(self.config["log_level"])

        if self.config["debug"]:
            console_handler = StreamHandler()
            self.config["log_level"] = "DEBUG"
            console_handler.setLevel(self.config["log_level"])
            console_handler.setFormatter(formatter)
            self.logger.handlers = []
            self.logger.addHandler(console_handler)
            self.logger.addHandler(collection_file_handler)
            self.config["capture_output"] = False

        if self.config["quiet"]:
            self.logger.disabled = True
            self.config["capture_output"] = False

    def initialize_database_connections(self):
        DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user_database'], self.config['password_database'], self.config['host_database'], self.config['port_database'], self.config['name_database']
        )

        # Create an sqlalchemy engine for both database schemas
        self.logger.info("Making database connections")

        db_schema = 'augur_data'
        self.db = s.create_engine(DB_STR,  poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(db_schema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        metadata = MetaData()
        helper_metadata = MetaData()

        # Reflect only the tables we will use for each schema's metadata object
        metadata.reflect(self.db, only=self.data_tables)
        helper_metadata.reflect(self.helper_db, only=self.operations_tables)

        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)

        Base.prepare()
        HelperBase.prepare()

        # So we can access all our tables when inserting, updating, etc
        for table in self.data_tables:
            setattr(self, '{}_table'.format(table), Base.classes[table].__table__)

        try:
            self.logger.info(HelperBase.classes.keys())
        except:
            pass
        for table in self.operations_tables:
            try:
                setattr(self, '{}_table'.format(table), HelperBase.classes[table].__table__)
            except Exception as e:
                self.logger.info("Error setting attribute for table: {} : {}".format(table, e))

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = self.get_max_id('worker_history', 'history_id', operations_table=True) + 1

        # Organize different api keys/oauths available
        if 'gh_api_key' in self.config:
            self.init_oauths()
        else:
            self.oauths = [{'oauth_id': 0}]

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
        # If the task has one of our "valid" job types
        if value['job_type'] == "UPDATE" or value['job_type'] == "MAINTAIN":
            self._queue.put(value)

        # Setting that causes paginating through ALL pages, not just unknown ones
        # This setting is set by the housekeeper and is attached to the task before it gets sent here
        if 'focused_task' in value:
            if value['focused_task'] == 1:
                self.logger.info("Focused task is ON\n")
                self.finishing_task = True
        
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
        # Spawn a subprocess to handle message reading and performing the tasks
        self._child = Process(target=self.collect, args=())
        self._child.start()

    def collect(self):
        """ Function to process each entry in the worker's task queue
        Determines what action to take based off the message type
        """
        self.initialize_logging() # need to initialize logging again in child process cause multiprocessing
        self.logger.info("Starting data collection process\n")
        self.initialize_database_connections() 
        while True:
            if not self._queue.empty():
                message = self._queue.get() # Get the task off our MP queue
            else:
                break
            self.logger.info("Popped off message: {}\n".format(str(message)))

            if message['job_type'] == 'STOP':
                break

            # If task is not a valid job type
            if message['job_type'] != 'MAINTAIN' and message['job_type'] != 'UPDATE':
                raise ValueError('{} is not a recognized task type'.format(message['job_type']))
                pass

            # Query repo_id corresponding to repo url of given task 
            repoUrlSQL = s.sql.text("""
                SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
                """.format(message['given'][self.given[0][0]]))
            repo_id = int(pd.read_sql(repoUrlSQL, self.db, params={}).iloc[0]['repo_id'])

            # Call method corresponding to model sent in task
            try:
                model_method = getattr(self, '{}_model'.format(message['models'][0]))
                self.record_model_process(repo_id, 'repo_info')
            except Exception as e:
                self.logger.info('Error: {}.\nNo defined method for model: {}, '.format(e, message['models'][0]) +
                    'must have name of {}_model'.format(message['models'][0]))
                self.register_task_failure(message, repo_id, e)
                break

            # Model method calls wrapped in try/except so that any unexpected error that occurs can be caught
            #   and worker can move onto the next task without stopping
            try:
                model_method(message, repo_id)
            except Exception as e: # this could be a custom exception, might make things easier
                self.register_task_failure(message, repo_id, e)
                break

        self.logger.info("Closing database connections for current task\n")
        self.db.dispose()
        self.helper_db.dispose()

    def assign_tuple_action(self, new_data, table_values, update_col_map, duplicate_col_map, table_pkey, value_update_col_map={}):
        """ map objects => { *our db col* : *gh json key*} """
        need_insertion_count = 0
        need_update_count = 0
        for i, obj in enumerate(new_data):
            if type(obj) != dict:
                self.logger.info('Moving to next tuple, tuple is not dict: {}'.format(obj))
                continue

            obj['flag'] = 'none' # default of no action needed
            for db_dupe_key in list(duplicate_col_map.keys()):

                if table_values.isin([obj[duplicate_col_map[db_dupe_key]]]).any().any():
                    continue

                self.logger.info('Found a tuple that needs insertion based on dupe key: {}\n'.format(db_dupe_key))
                obj['flag'] = 'need_insertion'
                need_insertion_count += 1
                break

            if obj['flag'] == 'need_insertion':
                self.logger.info('Already determined that current tuple needs insertion, skipping checking updates. '
                    'Moving to next tuple.\n')
                continue

            existing_tuple = table_values[table_values[db_dupe_key].isin(
                    [obj[duplicate_col_map[db_dupe_key]]])].to_dict('records')[0]

            # If we need to check the values of the existing tuple to determine if an update is needed
            for augur_col, value_check in value_update_col_map.items():
                not_nan_check = not (math.isnan(value_check) and math.isnan(existing_tuple[augur_col])) if value_check is not None else True
                if existing_tuple[augur_col] != value_check and not_nan_check:
                    continue
                self.logger.info("Found a tuple that needs an update for column: {}\n".format(augur_col)) 
                obj['flag'] = 'need_update'
                obj['pkey'] = existing_tuple[table_pkey]
                need_update_count += 1

            if obj['flag'] == 'need_update':
                self.logger.info('Already determined that current tuple needs update, skipping checking further updates. '
                    'Moving to next tuple.\n')
                continue

            # Now check the existing tuple's values against the response values to determine if an update is needed
            for col in update_col_map.keys():
                if update_col_map[col] not in obj:
                    continue
                if obj[update_col_map[col]] == existing_tuple[col]:
                    continue
                self.logger.info("Found a tuple that needs an update for column: {}\n".format(col)) 
                obj['flag'] = 'need_update'
                obj['pkey'] = existing_tuple[table_pkey]
                need_update_count += 1

        self.logger.info("Page recieved has {} tuples, while filtering duplicates this ".format(len(new_data)) +
            "was reduced to {} tuples, and {} tuple updates are needed.\n".format(need_insertion_count, need_update_count))
        return new_data

    def check_duplicates(self, new_data, table_values, key):
        need_insertion = []
        for obj in new_data:
            if type(obj) == dict:
                if not table_values.isin([obj[key]]).any().any():
                    need_insertion.append(obj)
                # else:
                    # self.logger.info("Tuple with github's {} key value already".format(key) +
                    #     "exists in our db: {}\n".format(str(obj[key])))
        self.logger.info("Page recieved has {} tuples, while filtering duplicates this ".format(str(len(new_data))) +
            "was reduced to {} tuples.\n".format(str(len(need_insertion))))
        return need_insertion

    def connect_to_broker(self):
        connected = False
        for i in range(5):
            try:
                self.logger.debug("Connecting to broker, attempt {}\n".format(i))
                if i > 0:
                    time.sleep(10)
                requests.post('http://{}:{}/api/unstable/workers'.format(
                    self.config['host_broker'],self.config['port_broker']), json=self.specs)
                self.logger.info("Connection to the broker was successful\n")
                connected = True
                break
            except requests.exceptions.ConnectionError:
                self.logger.error('Cannot connect to the broker. Trying again...\n')
        if not connected:
            sys.exit('Could not connect to the broker after 5 attempts! Quitting...\n')

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

    def find_id_from_login(self, login):
        idSQL = s.sql.text("""
            SELECT cntrb_id FROM contributors WHERE cntrb_login = '{}'
            """.format(login))
        rs = pd.read_sql(idSQL, self.db, params={})
        data_list = [list(row) for row in rs.itertuples(index=False)]
        try:
            return data_list[0][0]
        except:
            self.logger.info("contributor needs to be added...")

        cntrb_url = ("https://api.github.com/users/" + login)
        self.logger.info("Hitting endpoint: {} ...\n".format(cntrb_url))
        r = requests.get(url=cntrb_url, headers=self.headers)
        self.update_gh_rate_limit(r)
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

        cntrb = {
            "cntrb_login": contributor['login'] if 'login' in contributor else None,
            "cntrb_email": email,
            "cntrb_company": company,
            "cntrb_location": location,
            "cntrb_created_at": contributor['created_at'] if 'created_at' in contributor else None,                
            "cntrb_canonical": None,
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
        self.logger.info("Primary key inserted into the contributors table: " + str(result.inserted_primary_key))
        self.results_counter += 1
        self.cntrb_id_inc = int(result.inserted_primary_key[0])

        self.logger.info("Inserted contributor: " + contributor['login'] + "\n")
        
        return self.find_id_from_login(login)

    def get_owner_repo(self, github_url):
        split = github_url.split('/')

        owner = split[-2]
        repo = split[-1]

        if '.git' in repo:
            repo = repo[:-4]

        return owner, repo

    def get_max_id(self, table, column, default=25150, operations_table=False):
        maxIdSQL = s.sql.text("""
            SELECT max({0}.{1}) AS {1}
            FROM {0}
        """.format(table, column))
        db = self.db if not operations_table else self.helper_db
        rs = pd.read_sql(maxIdSQL, db, params={})
        if rs.iloc[0][column] is not None:
            max_id = int(rs.iloc[0][column]) + 1  
            self.logger.info("Found max id for {} column in the {} table: {}\n".format(column, table, max_id))
        else:
            max_id = default
            self.logger.info("Could not find max id for {} column in the {} table... using default set to: \
                {}\n".format(column, table, max_id))
        return max_id

    def get_table_values(self, cols, tables, where_clause=""):
        table_str = tables[0]
        del tables[0]

        col_str = cols[0]
        del cols[0]

        for table in tables:
            table_str += ", " + table
        for col in cols:
            col_str += ", " + col

        tableValuesSQL = s.sql.text("""
            SELECT {} FROM {} {}
        """.format(col_str, table_str, where_clause))
        self.logger.info("Getting table values with the following PSQL query: \n{}\n".format(tableValuesSQL))
        values = pd.read_sql(tableValuesSQL, self.db, params={})
        return values

    def init_oauths(self):
        self.oauths = []
        self.headers = None

        # Endpoint to hit solely to retrieve rate limit information from headers of the response
        url = "https://api.github.com/users/gabe-heim"

        # Make a list of api key in the config combined w keys stored in the database
        oauthSQL = s.sql.text("""
            SELECT * FROM worker_oauth WHERE access_token <> '{}'
        """.format(self.config['gh_api_key']))
        for oauth in [{'oauth_id': 0, 'access_token': self.config['gh_api_key']}] + json.loads(pd.read_sql(oauthSQL, self.helper_db, params={}).to_json(orient="records")):
            self.headers = {'Authorization': 'token %s' % oauth['access_token']}
            self.logger.info("Getting rate limit info for oauth: {}\n".format(oauth))
            response = requests.get(url=url, headers=self.headers)
            self.oauths.append({
                    'oauth_id': oauth['oauth_id'],
                    'access_token': oauth['access_token'],
                    'rate_limit': int(response.headers['X-RateLimit-Remaining']),
                    'seconds_to_reset': (datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])) - datetime.datetime.now()).total_seconds()
                })
            self.logger.info("Found OAuth available for use: {}\n\n".format(self.oauths[-1]))

        if len(self.oauths) == 0:
            self.logger.info("No API keys detected, please include one in your config or in the worker_oauths table in the augur_operations schema of your database\n")

        # First key to be used will be the one specified in the config (first element in 
        #   self.oauths array will always be the key in use)
        self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}

    def paginate(self, url, duplicate_col_map, update_col_map, table, table_pkey, where_clause="", value_update_col_map={}):
        # Paginate backwards through all the tuples but get first page in order
        #   to determine if there are multiple pages and if the 1st page covers all
        update_keys = list(update_col_map.keys()) if update_col_map else []
        update_keys += list(value_update_col_map.keys()) if value_update_col_map else []
        cols_query = list(duplicate_col_map.keys()) + update_keys + [table_pkey]
        table_values = self.get_table_values(cols_query, [table], where_clause)

        i = 1
        multiple_pages = False
        tuples = []
        while True:
            num_attempts = 0
            success = False
            while num_attempts < 3:
                self.logger.info("Hitting endpoint: " + url.format(i) + " ...\n")
                r = requests.get(url=url.format(i), headers=self.headers)
                self.update_gh_rate_limit(r)
                self.logger.info("Analyzing page {} of {}\n".format(i, int(r.links['last']['url'][-6:].split('=')[1]) + 1 if 'last' in r.links else '*last page not known*'))

                try:
                    j = r.json()
                except:
                    j = json.loads(json.dumps(r.text))

                if type(j) != dict and type(j) != str:
                    success = True
                    break
                elif type(j) == dict:
                    self.logger.info("Request returned a dict: {}\n".format(j))
                    if j['message'] == 'Not Found':
                        self.logger.info("Github repo was not found or does not exist for endpoint: {}\n".format(url))
                        break
                    if j['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                        num_attempts -= 1
                        self.update_gh_rate_limit(r, temporarily_disable=True)
                    if j['message'] == 'Bad credentials':
                        self.update_gh_rate_limit(r, bad_credentials=True)
                elif type(j) == str:
                    self.logger.info("J was string: {}\n".format(j))
                    if '<!DOCTYPE html>' in j:
                        self.logger.info("HTML was returned, trying again...\n")
                    elif len(j) == 0:
                        self.logger.info("Empty string, trying again...\n")
                    else:
                        try:
                            j = json.loads(j)
                            success = True
                            break
                        except:
                            pass
                num_attempts += 1
            if not success:
                break

            # Find last page so we can decrement from there
            if 'last' in r.links and not multiple_pages and not self.finishing_task:
                param = r.links['last']['url'][-6:]
                i = int(param.split('=')[1]) + 1
                self.logger.info("Multiple pages of request, last page is " + str(i - 1) + "\n")
                multiple_pages = True
            elif not multiple_pages and not self.finishing_task:
                self.logger.info("Only 1 page of request\n")
            elif self.finishing_task:
                self.logger.info("Finishing a previous task, paginating forwards ..."
                    " excess rate limit requests will be made\n")
            
            if len(j) == 0:
                self.logger.info("Response was empty, breaking from pagination.\n")
                break
                
            # Checking contents of requests with what we already have in the db
            j = self.assign_tuple_action(j, table_values, update_col_map, duplicate_col_map, table_pkey, value_update_col_map)
            if not j:
                self.logger.info("Assigning tuple action failed, moving to next page.\n")
                i = i + 1 if self.finishing_task else i - 1
                continue
            try:
                to_add = [obj for obj in j if obj not in tuples and obj['flag'] != 'none']
            except Exception as e:
                self.logger.info("Failure accessing data of page: {}. Moving to next page.\n".format(e))
                i = i + 1 if self.finishing_task else i - 1
                continue
            if len(to_add) == 0 and multiple_pages and 'last' in r.links:
                self.logger.info("{}".format(r.links['last']))
                if i - 1 != int(r.links['last']['url'][-6:].split('=')[1]):
                    self.logger.info("No more pages with unknown tuples, breaking from pagination.\n")
                    break
            tuples += to_add

            i = i + 1 if self.finishing_task else i - 1

            # Since we already wouldve checked the first page... break
            if (i == 1 and multiple_pages and not self.finishing_task) or i < 1 or len(j) == 0:
                self.logger.info("No more pages to check, breaking from pagination.\n")
                break

        return tuples

    def query_github_contributors(self, entry_info, repo_id):

        """ Data collection function
        Query the GitHub API for contributors
        """
        self.logger.info("Querying contributors with given entry info: " + str(entry_info) + "\n")

        github_url = entry_info['given']['github_url'] if 'github_url' in entry_info['given'] else entry_info['given']['git_url']

        # Extract owner/repo from the url for the endpoint
        path = urlparse(github_url)
        split = path[2].split('/')

        owner = split[1]
        name = split[2]

        # Handles git url case by removing the extension
        if ".git" in name:
            name = name[:-4]

        # Set the base of the url and place to hold contributors to insert
        contributors_url = ("https://api.github.com/repos/" + owner + "/" + 
            name + "/contributors?per_page=100&page={}")

        # Get contributors that we already have stored
        #   Set our duplicate and update column map keys (something other than PK) to 
        #   check dupicates/needed column updates with
        table = 'contributors'
        table_pkey = 'cntrb_id'
        update_col_map = {'cntrb_email': 'email'}
        duplicate_col_map = {'cntrb_login': 'login'}

        #list to hold contributors needing insertion or update
        contributors = self.paginate(contributors_url, duplicate_col_map, update_col_map, table, table_pkey)
        
        self.logger.info("Count of contributors needing insertion: " + str(len(contributors)) + "\n")
        
        for repo_contributor in contributors:
            try:
                # Need to hit this single contributor endpoint to get extra data including...
                #   `created at`
                #   i think that's it
                cntrb_url = ("https://api.github.com/users/" + repo_contributor['login'])
                self.logger.info("Hitting endpoint: " + cntrb_url + " ...\n")
                r = requests.get(url=cntrb_url, headers=self.headers)
                self.update_gh_rate_limit(r)
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
                        self.worker_history_table.c.cntrb_email==email).values(cntrb))
                    self.logger.info("Updated tuple in the contributors table with existing email: {}".format(email))
                    self.cntrb_id_inc = repo_contributor['pkey']
                elif repo_contributor['flag'] == 'need_insertion':
                    result = self.db.execute(self.contributors_table.insert().values(cntrb))
                    self.logger.info("Primary key inserted into the contributors table: {}".format(result.inserted_primary_key))
                    self.results_counter += 1

                    self.logger.info("Inserted contributor: " + contributor['login'] + "\n")

                    # Increment our global track of the cntrb id for the possibility of it being used as a FK
                    self.cntrb_id_inc = int(result.inserted_primary_key[0])

            except Exception as e:
                self.logger.info("Caught exception: {}".format(e))
                self.logger.info("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
                continue

    def record_model_process(self, repo_id, model):

        task_history = {
            "repo_id": repo_id,
            "worker": self.config['id'],
            "job_model": model,
            "oauth_id": self.oauths[0]['oauth_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Stopped",
            "total_results": self.results_counter
        }
        if self.finishing_task:
            result = self.helper_db.execute(self.worker_history_table.update().where(
                self.worker_history_table.c.history_id==self.history_id).values(task_history))
            self.history_id += 1
        else:
            result = self.helper_db.execute(self.worker_history_table.insert().values(task_history))
            self.logger.info("Record incomplete history tuple: {}\n".format(result.inserted_primary_key))
            self.history_id = int(result.inserted_primary_key[0])

    def register_task_completion(self, task, repo_id, model):
        # Task to send back to broker
        task_completed = {
            'worker_id': self.config['id'],
            'job_type': "MAINTAIN",
            'repo_id': repo_id,
            'job_model': model
        }
        key = 'github_url' if 'github_url' in task['given'] else 'git_url' if 'git_url' in task['given'] else "INVALID_GIVEN"
        task_completed[key] = task['given']['github_url'] if 'github_url' in task['given'] else task['given']['git_url'] if 'git_url' in task['given'] else "INVALID_GIVEN"
        if key == 'INVALID_GIVEN':
            self.register_task_failure(task, repo_id, "INVALID_GIVEN: not github nor git url")
            return

        # Add to history table
        task_history = {
            "repo_id": repo_id,
            "worker": self.config['id'],
            "job_model": model,
            "oauth_id": self.oauths[0]['oauth_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Success",
            "total_results": self.results_counter
        }
        self.helper_db.execute(self.worker_history_table.update().where(
            self.worker_history_table.c.history_id==self.history_id).values(task_history))

        self.logger.info("Recorded job completion for: " + str(task_completed) + "\n")

        # Update job process table
        updated_job = {
            "since_id_str": repo_id,
            "last_count": self.results_counter,
            "last_run": datetime.datetime.now(),
            "analysis_state": 0
        }
        self.helper_db.execute(self.worker_job_table.update().where(
            self.worker_job_table.c.job_model==model).values(updated_job))
        self.logger.info("Updated job process for model: " + model + "\n")

        if self.config["offline_mode"] is False:
            
            # Notify broker of completion
            self.logger.info("Telling broker we completed task: " + str(task_completed) + "\n\n" + 
                "This task inserted: " + str(self.results_counter) + " tuples.\n")

            requests.post('http://{}:{}/api/unstable/completed_task'.format(
                self.config['host_broker'],self.config['port_broker']), json=task_completed)

        # Reset results counter for next task
        self.results_counter = 0

    def register_task_failure(self, task, repo_id, e):

        self.logger.info("Worker ran into an error for task: {}\n".format(task))
        self.logger.info("Printing traceback...\n")
        tb = traceback.format_exc()
        self.logger.info(tb)

        self.logger.info(f'This task inserted {self.results_counter} tuples before failure.\n')
        self.logger.info("Notifying broker and logging task failure in database...\n")
        key = 'github_url' if 'github_url' in task['given'] else 'git_url' if 'git_url' in task['given'] else "INVALID_GIVEN"
        url = task['given'][key]

        """ Query all repos with repo url of given task """
        repoUrlSQL = s.sql.text("""
            SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
            """.format(url))
        repo_id = int(pd.read_sql(repoUrlSQL, self.db, params={}).iloc[0]['repo_id'])

        task['worker_id'] = self.config['id']
        try:
            requests.post("http://{}:{}/api/unstable/task_error".format(
                self.config['host_broker'],self.config['port_broker']), json=task)
        except requests.exceptions.ConnectionError:
            self.logger.error('Could not send task failure message to the broker\n')
        except Exception:
            logging.exception('An error occured while informing broker about task failure\n')

        # Add to history table
        task_history = {
            "repo_id": repo_id,
            "worker": self.config['id'],
            "job_model": task['models'][0],
            "oauth_id": self.oauths[0]['oauth_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Error",
            "total_results": self.results_counter
        }
        self.helper_db.execute(self.worker_history_table.update().where(self.worker_history_table.c.history_id==self.history_id).values(task_history))

        self.logger.info("Recorded job error in the history table for: " + str(task) + "\n")

        # Update job process table
        updated_job = {
            "since_id_str": repo_id,
            "last_count": self.results_counter,
            "last_run": datetime.datetime.now(),
            "analysis_state": 0
        }
        self.helper_db.execute(self.worker_job_table.update().where(self.worker_job_table.c.job_model==task['models'][0]).values(updated_job))
        self.logger.info("Updated job process for model: " + task['models'][0] + "\n")

        # Reset results counter for next task
        self.results_counter = 0  

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

    def update_gh_rate_limit(self, response, bad_credentials=False, temporarily_disable=False):
        # Try to get rate limit from request headers, sometimes it does not work (GH's issue)
        #   In that case we just decrement from last recieved header count
        if bad_credentials and len(self.oauths) > 1:
            self.logger.info("Removing oauth with bad credentials from consideration: {}".format(self.oauths[0]))
            del self.oauths[0]

        if temporarily_disable:
            self.logger.info("Github thinks we are abusing their api. Preventing use of this key until it resets...\n")
            self.oauths[0]['rate_limit'] = 0
        else:
            try:
                self.oauths[0]['rate_limit'] = int(response.headers['X-RateLimit-Remaining'])
                self.logger.info("Recieved rate limit from headers\n")
            except:
                self.oauths[0]['rate_limit'] -= 1
                self.logger.info("Headers did not work, had to decrement\n")
        self.logger.info("Updated rate limit, you have: " + 
            str(self.oauths[0]['rate_limit']) + " requests remaining.\n")
        if self.oauths[0]['rate_limit'] <= 0:
            try:
                reset_time = response.headers['X-RateLimit-Reset']
            except Exception as e:
                self.logger.info("Could not get reset time from headers because of error: {}".format(error))
                reset_time = 3600
            time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
            self.logger.info("Rate limit exceeded, checking for other available keys to use.\n")

            # We will be finding oauth with the highest rate limit left out of our list of oauths
            new_oauth = self.oauths[0]
            # Endpoint to hit solely to retrieve rate limit information from headers of the response
            url = "https://api.github.com/users/gabe-heim"

            other_oauths = self.oauths[0:] if len(self.oauths) > 1 else []
            for oauth in other_oauths:
                self.logger.info("Inspecting rate limit info for oauth: {}\n".format(oauth))
                self.headers = {'Authorization': 'token %s' % oauth['access_token']}
                response = requests.get(url=url, headers=self.headers)
                oauth['rate_limit'] = int(response.headers['X-RateLimit-Remaining'])
                oauth['seconds_to_reset'] = (datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])) - datetime.datetime.now()).total_seconds()

                # Update oauth to switch to if a higher limit is found
                if oauth['rate_limit'] > new_oauth['rate_limit']:
                    self.logger.info("Higher rate limit found in oauth: {}\n".format(oauth))
                    new_oauth = oauth
                elif oauth['rate_limit'] == new_oauth['rate_limit'] and oauth['seconds_to_reset'] < new_oauth['seconds_to_reset']:
                    self.logger.info("Lower wait time found in oauth with same rate limit: {}\n".format(oauth))
                    new_oauth = oauth

            if new_oauth['rate_limit'] <= 0 and new_oauth['seconds_to_reset'] > 0:
                self.logger.info("No oauths with >0 rate limit were found, waiting for oauth with smallest wait time: {}\n".format(new_oauth))
                time.sleep(new_oauth['seconds_to_reset'])

            # Make new oauth the 0th element in self.oauths so we know which one is in use
            index = self.oauths.index(new_oauth)
            self.oauths[0], self.oauths[index] = self.oauths[index], self.oauths[0]
            self.logger.info("Using oauth: {}\n".format(self.oauths[0]))

            # Change headers to be using the new oauth's key
            self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}
