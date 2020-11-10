#SPDX-License-Identifier: MIT
""" Helper methods constant across all workers """
import requests, datetime, time, traceback, json, os, sys, math, logging
from logging import FileHandler, Formatter, StreamHandler
from multiprocessing import Process, Queue
import sqlalchemy as s
import pandas as pd
from pathlib import Path
from urllib.parse import urlparse, quote
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from augur.config import AugurConfig
from augur.logging import AugurLogging

class Worker():

    ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self, worker_type, config={}, given=[], models=[], data_tables=[], operations_tables=[], platform="github"):

        self.worker_type = worker_type
        self._task = None # task currently being worked on (dict)
        self._child = None # process of currently running task (multiprocessing process)
        self._queue = Queue() # tasks stored here 1 at a time (in a mp queue so it can translate across multiple processes)
        self.data_tables = data_tables
        self.operations_tables = operations_tables
        self._root_augur_dir = Worker.ROOT_AUGUR_DIR
        self.platform = platform

        # count of tuples inserted in the database (to store stats for each task in op tables)
        self._results_counter = 0

        # if we are finishing a previous task, certain operations work differently
        self.finishing_task = False
        # Update config with options that are general and not specific to any worker
        self.augur_config = AugurConfig(self._root_augur_dir)

        self.config = {
                'worker_type': self.worker_type,
                'host': self.augur_config.get_value("Server", "host"),
                'gh_api_key': self.augur_config.get_value('Database', 'key'),
                'gitlab_api_key': self.augur_config.get_value('Database', 'gitlab_api_key'),
                'offline_mode': False
            }
        self.config.update(self.augur_config.get_section("Logging"))

        try:
            worker_defaults = self.augur_config.get_default_config()['Workers'][self.config['worker_type']]
            self.config.update(worker_defaults)
        except KeyError as e:
            logging.warn('Could not get default configuration for {}'.format(self.config['worker_type']))

        worker_info = self.augur_config.get_value('Workers', self.config['worker_type'])
        self.config.update(worker_info)

        worker_port = self.config['port']
        while True:
            try:
                r = requests.get('http://{}:{}/AUGWOP/heartbeat'.format(
                    self.config['host'], worker_port)).json()
                if 'status' in r:
                    if r['status'] == 'alive':
                        worker_port += 1
            except:
                break

        self.config.update({
            "port": worker_port,
            "id": "workers.{}.{}".format(self.worker_type, worker_port),
            "capture_output": False,
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

        try:
            self.tool_source
            self.tool_version
            self.data_source
        except:
            self.tool_source = 'Augur Worker Testing'
            self.tool_version = '0.0.0'
            self.data_source = 'Augur Worker Testing'

    def __repr__(self):
        return f"{self.config['id']}"

    def initialize_logging(self):
        self.config["log_level"] = self.config["log_level"].upper()
        if self.config["debug"]:
            self.config["log_level"] = "DEBUG"

        if self.config["verbose"]:
            format_string = AugurLogging.verbose_format_string
        else:
            format_string = AugurLogging.simple_format_string

        formatter = Formatter(fmt=format_string)
        error_formatter = Formatter(fmt=AugurLogging.error_format_string)

        worker_dir = AugurLogging.get_log_directories(self.augur_config, reset_logfiles=False) + "/workers/"
        Path(worker_dir).mkdir(exist_ok=True)
        logfile_dir = worker_dir + f"/{self.worker_type}/"
        Path(logfile_dir).mkdir(exist_ok=True)

        server_logfile = logfile_dir + '{}_{}_server.log'.format(self.worker_type, self.config["port"])
        collection_logfile = logfile_dir + '{}_{}_collection.log'.format(self.worker_type, self.config["port"])
        collection_errorfile = logfile_dir + '{}_{}_collection.err'.format(self.worker_type, self.config["port"])
        self.config.update({
            "logfile_dir": logfile_dir,
            "server_logfile": server_logfile,
            "collection_logfile": collection_logfile,
            "collection_errorfile": collection_errorfile
        })

        collection_file_handler = FileHandler(filename=self.config["collection_logfile"], mode="a")
        collection_file_handler.setFormatter(formatter)
        collection_file_handler.setLevel(self.config["log_level"])

        collection_errorfile_handler = FileHandler(filename=self.config["collection_errorfile"], mode="a")
        collection_errorfile_handler.setFormatter(error_formatter)
        collection_errorfile_handler.setLevel(logging.WARNING)

        logger = logging.getLogger(self.config["id"])
        logger.handlers = []
        logger.addHandler(collection_file_handler)
        logger.addHandler(collection_errorfile_handler)
        logger.setLevel(self.config["log_level"])
        logger.propagate = False

        if self.config["debug"]:
            self.config["log_level"] = "DEBUG"
            console_handler = StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(self.config["log_level"])
            logger.addHandler(console_handler)

        if self.config["quiet"]:
            logger.disabled = True

        self.logger = logger

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
                self.logger.error("Error setting attribute for table: {} : {}".format(table, e))

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = self.get_max_id('worker_history', 'history_id', operations_table=True) + 1

        # Organize different api keys/oauths available
        self.logger.info("Initializing API key.")
        if 'gh_api_key' in self.config or 'gitlab_api_key' in self.config:
            self.init_oauths(self.platform)
        else:
            self.oauths = [{'oauth_id': 0}]

    @property
    def results_counter(self):
        """ Property that is returned when the worker's current results_counter is referenced
        """
        if self.worker_type == 'facade_worker':
            return self.cfg.repos_processed #TODO: figure out why this doesn't work...
        else:
            return self._results_counter

    @results_counter.setter
    def results_counter(self, value):
        """ entry point for the broker to add a task to the queue
        Adds this task to the queue, and calls method to process queue
        """
        self._results_counter = value


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
                self.logger.debug("Focused task is ON\n")
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
                self.logger.info("No job found.")
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
            self.logger.info("repo_id for which data collection is being initiated: {}".format(str(repo_id)))
            # Call method corresponding to model sent in task
            try:
                model_method = getattr(self, '{}_model'.format(message['models'][0]))
                self.record_model_process(repo_id, 'repo_info')
            except Exception as e:
                self.logger.error('Error: {}.\nNo defined method for model: {}, '.format(e, message['models'][0]) +
                    'must have name of {}_model'.format(message['models'][0]))
                self.register_task_failure(message, repo_id, e)
                break

            # Model method calls wrapped in try/except so that any unexpected error that occurs can be caught
            #   and worker can move onto the next task without stopping
            try:
                self.logger.info("Calling model method {}_models".format(message['models'][0]))
                model_method(message, repo_id)
            except Exception as e: # this could be a custom exception, might make things easier
                self.register_task_failure(message, repo_id, e)
                break

        self.logger.debug('Closing database connections\n')
        self.db.dispose()
        self.helper_db.dispose()
        self.logger.info("Collection process finished")

    def assign_tuple_action(self, new_data, table_values, update_col_map, duplicate_col_map, table_pkey, value_update_col_map={}):
        """ Include an extra key-value pair on each element of new_data that represents
            the action that should be taken with this element (i.e. 'need_insertion')

        :param new_data: List of dictionaries, data to be assigned an action to
        :param table_values: Pandas DataFrame, existing data in the database to check
            what action should be taken on the new_data depending on the presence of
            each element in this DataFrame
        :param update_col_map: Dictionary, maps the column names of the source data
            to the field names in our database for columns that should be checked for
            updates (if source data value != value in existing database row, then an
            update is needed). Key is source data column name, value is database field name.
            Example: {'id': 'gh_issue_id'}
        :param duplicate_col_map: Dictionary, maps the column names of the source data
            to the field names in our database for columns that should be checked for
            duplicates (if source data value == value in existing database row, then this
            element is a duplicate and would not need an insertion). Key is source data
            column name, value is database field name. Example: {'id': 'gh_issue_id'}
        :param table_pkey: String, the field name of the primary key of the table in
            the database that we are checking the table_values for.
        :param value_update_col_map: Dictionary, sometimes we add a new field to a table,
            and we want to trigger an update of that row in the database even if all of the
            data values are the same and would not need an update ordinarily. Checking for
            a specific existing value in the database field allows us to do this. The key is the
            name of the field in the database we are checking for a specific value to trigger
            an update, the value is the value we are checking for equality to trigger an update.
            Example: {'cntrb_id': None}
        :return: List of dictionaries, contains all the same elements of new_data, except
            each element now has an extra key-value pair with the key being 'flag', and
            the value being 'need_insertion', 'need_update', or 'none'
        """
        need_insertion_count = 0
        need_update_count = 0
        for i, obj in enumerate(new_data):
            if type(obj) != dict:
                self.logger.info('Moving to next tuple, tuple is not dict: {}'.format(obj))
                continue

            obj['flag'] = 'none' # default of no action needed
            existing_tuple = None
            for db_dupe_key in list(duplicate_col_map.keys()):

                if table_values.isin([obj[duplicate_col_map[db_dupe_key]]]).any().any():
                    if table_values[table_values[db_dupe_key].isin(
                        [obj[duplicate_col_map[db_dupe_key]]])].to_dict('records'):

                        existing_tuple = table_values[table_values[db_dupe_key].isin(
                            [obj[duplicate_col_map[db_dupe_key]]])].to_dict('records')[0]
                    continue

                self.logger.info('Found a tuple that needs insertion based on dupe key: {}\n'.format(db_dupe_key))
                obj['flag'] = 'need_insertion'
                need_insertion_count += 1
                break

            if obj['flag'] == 'need_insertion':
                self.logger.info('Already determined that current tuple needs insertion, skipping checking updates. '
                    'Moving to next tuple.\n')
                continue

            if not existing_tuple:
                self.logger.info('An existing tuple was not found for this data ' +
                    'point and we have reached the check-updates portion of assigning ' +
                    'tuple action, so we will now move to next data point\n')
                continue

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
        """ Filters what items of the new_data json (list of dictionaries) that are not
        present in the table_values df

        :param new_data: List of dictionaries, new data to filter duplicates out of
        :param table_values: Pandas DataFrame, existing data to check what data is already
            present in the database
        :param key: String, key of each dict in new_data whose value we are checking
            duplicates with
        :return: List of dictionaries, contains elements of new_data that are not already
            present in the database
        """
        need_insertion = []
        for obj in new_data:
            if type(obj) != dict:
                continue
            if not table_values.isin([obj[key]]).any().any():
                need_insertion.append(obj)
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

    @staticmethod
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

    def find_id_from_login(self, login, platform='github'):
        """
        Retrieves our contributor table primary key value for the contributor with
            the given GitHub login credentials, if this contributor is not there, then
            they get inserted.

        :param login: String, the GitHub login username to find the primary key id for
        :return: Integer, the id of the row in our database with the matching GitHub login
        """
        idSQL = s.sql.text("""
            SELECT cntrb_id FROM contributors WHERE cntrb_login = '{}' \
            AND LOWER(data_source) = '{} api'
            """.format(login, platform))

        self.logger.info(idSQL)

        rs = pd.read_sql(idSQL, self.db, params={})
        data_list = [list(row) for row in rs.itertuples(index=False)]
        try:
            return data_list[0][0]
        except:
            self.logger.info('contributor needs to be added...')

        if platform == 'github':
            cntrb_url = ("https://api.github.com/users/" + login)
        elif platform == 'gitlab':
            cntrb_url = ("https://gitlab.com/api/v4/users?username=" + login )
        self.logger.info("Hitting endpoint: {} ...\n".format(cntrb_url))
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


        if platform == 'github':
            cntrb = {
                "cntrb_login": contributor['login'] if 'login' in contributor else None,
                "cntrb_email": contributor['email'] if 'email' in contributor else None,
                "cntrb_company": contributor['company'] if 'company' in contributor else None,
                "cntrb_location": contributor['location'] if 'location' in contributor else None,
                "cntrb_created_at": contributor['created_at'] if 'created_at' in contributor else None,
                "cntrb_canonical": None,
                "gh_user_id": contributor['id'] if 'id' in contributor else None,
                "gh_login": contributor['login'] if 'login' in contributor else None,
                "gh_url": contributor['url'] if 'url' in contributor else None,
                "gh_html_url": contributor['html_url'] if 'html_url' in contributor else None,
                "gh_node_id": contributor['node_id'] if 'node_id' in contributor else None,
                "gh_avatar_url": contributor['avatar_url'] if 'avatar_url' in contributor else None,
                "gh_gravatar_id": contributor['gravatar_id'] if 'gravatar_id' in contributor else None,
                "gh_followers_url": contributor['followers_url'] if 'followers_url' in contributor else None,
                "gh_following_url": contributor['following_url'] if 'following_url' in contributor else None,
                "gh_gists_url": contributor['gists_url'] if 'gists_url' in contributor else None,
                "gh_starred_url": contributor['starred_url'] if 'starred_url' in contributor else None,
                "gh_subscriptions_url": contributor['subscriptions_url'] if 'subscriptions_url' in contributor else None,
                "gh_organizations_url": contributor['organizations_url'] if 'organizations_url' in contributor else None,
                "gh_repos_url": contributor['repos_url'] if 'repos_url' in contributor else None,
                "gh_events_url": contributor['events_url'] if 'events_url' in contributor else None,
                "gh_received_events_url": contributor['received_events_url'] if 'received_events_url' in contributor else None,
                "gh_type": contributor['type'] if 'type' in contributor else None,
                "gh_site_admin": contributor['site_admin'] if 'site_admin' in contributor else None,
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source
            }

        elif platform == 'gitlab':
            cntrb =  {
                "cntrb_login": contributor[0]['username'] if 'username' in contributor[0] else None,
                "cntrb_email": email,
                "cntrb_company": company,
                "cntrb_location": location,
                "cntrb_created_at": contributor[0]['created_at'] if 'created_at' in contributor[0] else None,
                "cntrb_canonical": None,
                "gh_user_id": contributor[0]['id'],
                "gh_login": contributor[0]['username'],
                "gh_url": contributor[0]['web_url'],
                "gh_html_url": None,
                "gh_node_id": None,
                "gh_avatar_url": contributor[0]['avatar_url'],
                "gh_gravatar_id": None,
                "gh_followers_url": None,
                "gh_following_url": None,
                "gh_gists_url": None,
                "gh_starred_url": None,
                "gh_subscriptions_url": None,
                "gh_organizations_url": None,
                "gh_repos_url": None,
                "gh_events_url": None,
                "gh_received_events_url": None,
                "gh_type": None,
                "gh_site_admin": None,
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source
            }
        result = self.db.execute(self.contributors_table.insert().values(cntrb))
        self.logger.info("Primary key inserted into the contributors table: " + str(result.inserted_primary_key))
        self.results_counter += 1
        self.cntrb_id_inc = int(result.inserted_primary_key[0])

        self.logger.info("Inserted contributor: " + cntrb['cntrb_login'] + "\n")

        return self.find_id_from_login(login, platform)

    def get_owner_repo(self, git_url):
        """ Gets the owner and repository names of a repository from a git url

        :param git_url: String, the git url of a repository
        :return: Tuple, includes the owner and repository names in that order
        """
        split = git_url.split('/')

        owner = split[-2]
        repo = split[-1]

        if '.git' == repo[-4:]:
            repo = repo[:-4]

        return owner, repo

    def get_max_id(self, table, column, default=25150, operations_table=False):
        """ Gets the max value (usually used for id/pk's) of any Integer column
            of any table

        :param table: String, the table that consists of the column you want to
            query a max value for
        :param column: String, the column that you want to query the max value for
        :param default: Integer, if there are no values in the
            specified column, the value of this parameter will be returned
        :param operations_table: Boolean, if True, this signifies that the table/column
            that is wanted to be queried is in the augur_operations schema rather than
            the augur_data schema. Default False
        :return: Integer, the max value of the specified column/table
        """
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
            self.logger.warning('Could not find max id for {} column in the {} table... ' +
                'using default set to: {}\n'.format(column, table, max_id))
        return max_id

    def get_table_values(self, cols, tables, where_clause=""):
        """ Can query all values of any column(s) from any table(s)
            with an optional where clause

        :param cols: List of Strings, column(s) that user wants to query
        :param tables: List of Strings, table(s) that user wants to query
        :param where_clause: String, optional where clause to filter the values
            queried
        :return: Pandas DataFrame, contains all values queried in the columns, tables, and
            optional where clause provided
        """
        table_str = tables[0]
        del tables[0]

        col_str = cols[0]
        del cols[0]

        for table in tables:
            table_str += ", " + table
        for col in cols:
            col_str += ", " + col

        table_values_sql = s.sql.text("""
            SELECT {} FROM {} {}
        """.format(col_str, table_str, where_clause))
        self.logger.info('Getting table values with the following PSQL query: \n{}\n'.format(
            table_values_sql))
        values = pd.read_sql(table_values_sql, self.db, params={})
        return values

    def init_oauths(self, platform="github"):
        self.oauths = []
        self.headers = None
        self.logger.info("Trying initialization.")
        # Make a list of api key in the config combined w keys stored in the database
        # Select endpoint to hit solely to retrieve rate limit information from headers of the response
        # Adjust header keys needed to fetch rate limit information from the API responses
        if platform == "github":
            url = "https://api.github.com/users/gabe-heim"
            oauthSQL = s.sql.text("""
                SELECT * FROM worker_oauth WHERE access_token <> '{}' and platform = 'github'
                """.format(self.config['gh_api_key']))
            key_name = "gh_api_key"
            rate_limit_header_key = "X-RateLimit-Remaining"
            rate_limit_reset_header_key = "X-RateLimit-Reset"
        elif platform == "gitlab":
            url = "https://gitlab.com/api/v4/version"
            oauthSQL = s.sql.text("""
                SELECT * FROM worker_oauth WHERE access_token <> '{}' and platform = 'gitlab'
                """.format(self.config['gitlab_api_key']))
            key_name = "gitlab_api_key"
            rate_limit_header_key = "ratelimit-remaining"
            rate_limit_reset_header_key = "ratelimit-reset"

        for oauth in [{'oauth_id': 0, 'access_token': self.config[key_name]}] + json.loads(pd.read_sql(oauthSQL, self.helper_db, params={}).to_json(orient="records")):
            if platform == "github":
                self.headers = {'Authorization': 'token %s' % oauth['access_token']}
            elif platform == "gitlab":
                self.headers = {'Authorization': 'Bearer %s' % oauth['access_token']}
            self.logger.info("Getting rate limit info for oauth: {}\n".format(oauth))
            response = requests.get(url=url, headers=self.headers)
            self.oauths.append({
                    'oauth_id': oauth['oauth_id'],
                    'access_token': oauth['access_token'],
                    'rate_limit': int(response.headers[rate_limit_header_key]),
                    'seconds_to_reset': (datetime.datetime.fromtimestamp(int(response.headers[rate_limit_reset_header_key])) - datetime.datetime.now()).total_seconds()
                })
            self.logger.debug("Found OAuth available for use: {}\n\n".format(self.oauths[-1]))

        if len(self.oauths) == 0:
            self.logger.info("No API keys detected, please include one in your config or in the worker_oauths table in the augur_operations schema of your database\n")

        # First key to be used will be the one specified in the config (first element in
        #   self.oauths array will always be the key in use)
        if platform == "github":
            self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}
        elif platform == "gitlab":
            self.headers = {'Authorization': 'Bearer %s' % self.oauths[0]['access_token']}

        self.logger.info("OAuth initialized")

    def paginate(self, url, duplicate_col_map, update_col_map, table, table_pkey, where_clause="", value_update_col_map={}, platform="github"):
        """ Paginate either backwards or forwards (depending on the value of the worker's
            finishing_task attribute) through all the GitHub or GitLab api endpoint pages.

        :param url: String, the url of the API endpoint we are paginating through, expects
            a curly brace string formatter within the string to format the Integer
            representing the page number that is wanted to be returned
        :param duplicate_col_map: Dictionary, maps the column names of the source data
            to the field names in our database for columns that should be checked for
            duplicates (if source data value == value in existing database row, then this
            element is a duplicate and would not need an insertion). Key is source data
            column name, value is database field name. Example: {'id': 'gh_issue_id'}
        :param update_col_map: Dictionary, maps the column names of the source data
            to the field names in our database for columns that should be checked for
            updates (if source data value != value in existing database row, then an
            update is needed). Key is source data column name, value is database field name.
            Example: {'id': 'gh_issue_id'}
        :param table: String, the name of the table that holds the values to check for
            duplicates/updates against
        :param table_pkey: String, the field name of the primary key of the table in
            the database that we are getting the values for to cross-reference to check
            for duplicates.
        :param where_clause: String, optional where clause to filter the values
            that are queried when preparing the values that will be cross-referenced
            for duplicates/updates
        :param value_update_col_map: Dictionary, sometimes we add a new field to a table,
            and we want to trigger an update of that row in the database even if all of the
            data values are the same and would not need an update ordinarily. Checking for
            a specific existing value in the database field allows us to do this. The key is the
            name of the field in the database we are checking for a specific value to trigger
            an update, the value is the value we are checking for equality to trigger an update.
            Example: {'cntrb_id': None}
        :return: List of dictionaries, all data points from the pages of the specified API endpoint
            each with a 'flag' key-value pair representing the required action to take with that
            data point (i.e. 'need_insertion', 'need_update', 'none')
        """

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
                self.logger.info(f'Hitting endpoint: {url.format(i)}...\n')
                r = requests.get(url=url.format(i), headers=self.headers)

                self.update_rate_limit(r, platform=platform)
                if 'last' not in r.links:
                    last_page = None
                else:
                    if platform == "github":
                        last_page = r.links['last']['url'][-6:].split('=')[1]
                    elif platform == "gitlab":
                        last_page =  r.links['last']['url'].split('&')[2].split("=")[1]
                    self.logger.info("Analyzing page {} of {}\n".format(i, int(last_page) + 1 if last_page is not None else '*last page not known*'))

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
                        self.logger.warning("Github repo was not found or does not exist for endpoint: {}\n".format(url))
                        break
                    if j['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                        num_attempts -= 1
                        self.logger.info("rate limit update code goes here")
                        self.update_rate_limit(r, temporarily_disable=True,platform=platform)
                    if j['message'] == 'Bad credentials':
                        self.logger.info("rate limit update code goes here")
                        self.update_rate_limit(r, bad_credentials=True, platform=platform)
                elif type(j) == str:
                    self.logger.info(f'J was string: {j}\n')
                    if '<!DOCTYPE html>' in j:
                        self.logger.info('HTML was returned, trying again...\n')
                    elif len(j) == 0:
                        self.logger.warning('Empty string, trying again...\n')
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
                if platform == "github":
                    param = r.links['last']['url'][-6:]
                    i = int(param.split('=')[1]) + 1
                elif platform == "gitlab":
                    i = int(r.links['last']['url'].split('&')[2].split("=")[1]) + 1
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
                self.logger.error("Assigning tuple action failed, moving to next page.\n")
                i = i + 1 if self.finishing_task else i - 1
                continue
            try:
                to_add = [obj for obj in j if obj not in tuples and (obj['flag'] != 'none')]
            except Exception as e:
                self.logger.error("Failure accessing data of page: {}. Moving to next page.\n".format(e))
                i = i + 1 if self.finishing_task else i - 1
                continue
            if len(to_add) == 0 and multiple_pages and 'last' in r.links:
                self.logger.info("{}".format(r.links['last']))
                if platform == "github":
                    page_number = int(r.links['last']['url'][-6:].split('=')[1])
                elif platform == "gitlab":
                    page_number = int(r.links['last']['url'].split('&')[2].split("=")[1])
                if i - 1 != page_number:
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
        self.logger.info(f'Querying contributors with given entry info: {entry_info}\n')

        github_url = entry_info['given']['github_url'] if 'github_url' in entry_info['given'] else entry_info['given']['git_url']

        # Extract owner/repo from the url for the endpoint
        owner, name = self.get_owner_repo(github_url)

        # Set the base of the url and place to hold contributors to insert
        contributors_url = (f'https://api.github.com/repos/{owner}/{name}/' +
            'contributors?per_page=100&page={}')

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
                self.logger.error("Caught exception: {}".format(e))
                self.logger.error("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
                continue

    def query_gitlab_contribtutors(self, entry_info, repo_id):

        gitlab_url = entry_info['given']['gitlab_url'] if 'gitlab_url' in entry_info['given'] else entry_info['given']['git_url']

        self.logger.info("Querying contributors with given entry info: " + str(entry_info) + "\n")

        path = urlparse(gitlab_url)
        split = path[2].split('/')

        owner = split[1]
        name = split[2]

        # Handles git url case by removing the extension
        if ".git" in name:
            name = name[:-4]

        url_encoded_format = quote(owner + '/' + name, safe='')

        table = 'contributors'
        table_pkey = 'cntrb_id'
        update_col_map = {'cntrb_email': 'email'}
        duplicate_col_map = {'cntrb_login': 'email'}

        # list to hold contributors needing insertion or update
        contributors = self.paginate("https://gitlab.com/api/v4/projects/" + url_encoded_format + "/repository/contributors?per_page=100&page={}", duplicate_col_map, update_col_map, table, table_pkey, platform='gitlab')

        for repo_contributor in contributors:
            try:
                cntrb_compressed_url = ("https://gitlab.com/api/v4/users?search=" + repo_contributor['email'])
                self.logger.info("Hitting endpoint: " + cntrb_compressed_url + " ...\n")
                r = requests.get(url=cntrb_compressed_url, headers=self.headers)
                contributor_compressed = r.json()

                email = repo_contributor['email']
                self.logger.info(contributor_compressed)
                if len(contributor_compressed) == 0 or type(contributor_compressed) is dict or "id" not in contributor_compressed[0]:
                    continue

                self.logger.info("Fetching for user: " + str(contributor_compressed[0]["id"]))

                cntrb_url = ("https://gitlab.com/api/v4/users/" + str(contributor_compressed[0]["id"]))
                self.logger.info("Hitting end point to get complete contributor info now: " + cntrb_url + "...\n")
                r = requests.get(url=cntrb_url, headers=self.headers)
                contributor = r.json()

                cntrb = {
                    "cntrb_login": contributor.get('username', None),
                    "cntrb_created_at": contributor.get('created_at', None),
                    "cntrb_email": email,
                    "cntrb_company": contributor.get('organization', None),
                    "cntrb_location": contributor.get('location', None),
                    # "cntrb_type": , dont have a use for this as of now ... let it default to null
                    "cntrb_canonical": contributor.get('public_email', None),
                    "gh_user_id": contributor.get('id', None),
                    "gh_login": contributor.get('username', None),
                    "gh_url": contributor.get('web_url', None),
                    "gh_html_url": contributor.get('web_url', None),
                    "gh_node_id": None,
                    "gh_avatar_url": contributor.get('avatar_url', None),
                    "gh_gravatar_id": None,
                    "gh_followers_url": None,
                    "gh_following_url": None,
                    "gh_gists_url": None,
                    "gh_starred_url": None,
                    "gh_subscriptions_url": None,
                    "gh_organizations_url": None,
                    "gh_repos_url": None,
                    "gh_events_url": None,
                    "gh_received_events_url": None,
                    "gh_type": None,
                    "gh_site_admin": None,
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                # Commit insertion to table
                if repo_contributor['flag'] == 'need_update':
                    result = self.db.execute(self.contributors_table.update().where(
                        self.worker_history_table.c.cntrb_email == email).values(cntrb))
                    self.logger.info("Updated tuple in the contributors table with existing email: {}".format(email))
                    self.cntrb_id_inc = repo_contributor['pkey']
                elif repo_contributor['flag'] == 'need_insertion':
                    result = self.db.execute(self.contributors_table.insert().values(cntrb))
                    self.logger.info("Primary key inserted into the contributors table: {}".format(result.inserted_primary_key))
                    self.results_counter += 1

                    self.logger.info("Inserted contributor: " + contributor['username'] + "\n")

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
        key = 'github_url' if 'github_url' in task['given'] else 'git_url' if 'git_url' in task['given'] else \
            'gitlab_url' if 'gitlab_url' in task['given'] else 'INVALID_GIVEN'
        task_completed[key] = task['given']['github_url'] if 'github_url' in task['given'] else task['given']['git_url'] \
            if 'git_url' in task['given'] else task['given']['gitlab_url'] if 'gitlab_url' in task['given'] else 'INVALID_GIVEN'
        if key == 'INVALID_GIVEN':
            self.register_task_failure(task, repo_id, "INVALID_GIVEN: Not a github/gitlab/git url.")
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

        self.logger.error("Worker ran into an error for task: {}\n".format(task))
        self.logger.error("Printing traceback...\n")
        tb = traceback.format_exc()
        self.logger.error(tb)

        self.logger.info(f'This task inserted {self.results_counter} tuples before failure.\n')
        self.logger.info("Notifying broker and logging task failure in database...\n")
        key = 'github_url' if 'github_url' in task['given'] else 'git_url' if 'git_url' in task['given'] else \
            'gitlab_url' if 'gitlab_url' in task['given'] else 'INVALID_GIVEN'
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
            self.logger.error(e)
        except Exception:
            self.logger.error('An error occured while informing broker about task failure\n')
            self.logger.error(e)

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

        self.logger.error("Recorded job error in the history table for: " + str(task) + "\n")

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

    def update_gitlab_rate_limit(self, response, bad_credentials=False, temporarily_disable=False):
        # Try to get rate limit from request headers, sometimes it does not work (GH's issue)
        #   In that case we just decrement from last recieved header count
        if bad_credentials and len(self.oauths) > 1:
            self.logger.info("Removing oauth with bad credentials from consideration: {}".format(self.oauths[0]))
            del self.oauths[0]

        if temporarily_disable:
            self.logger.info("Gitlab rate limit reached. Temp. disabling...\n")
            self.oauths[0]['rate_limit'] = 0
        else:
            try:
                self.oauths[0]['rate_limit'] = int(response.headers['RateLimit-Remaining'])
                self.logger.info("Recieved rate limit from headers\n")
            except:
                self.oauths[0]['rate_limit'] -= 1
                self.logger.info("Headers did not work, had to decrement\n")
        self.logger.info("Updated rate limit, you have: " +
            str(self.oauths[0]['rate_limit']) + " requests remaining.\n")
        if self.oauths[0]['rate_limit'] <= 0:
            try:
                reset_time = response.headers['RateLimit-Reset']
            except Exception as e:
                self.logger.info("Could not get reset time from headers because of error: {}".format(e))
                reset_time = 3600
            time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
            self.logger.info("Rate limit exceeded, checking for other available keys to use.\n")

            # We will be finding oauth with the highest rate limit left out of our list of oauths
            new_oauth = self.oauths[0]
            # Endpoint to hit solely to retrieve rate limit information from headers of the response
            url = "https://gitlab.com/api/v4/version"

            other_oauths = self.oauths[0:] if len(self.oauths) > 1 else []
            for oauth in other_oauths:
                self.logger.info("Inspecting rate limit info for oauth: {}\n".format(oauth))
                self.headers = {"PRIVATE-TOKEN" : oauth['access_token']}
                response = requests.get(url=url, headers=self.headers)
                oauth['rate_limit'] = int(response.headers['RateLimit-Remaining'])
                oauth['seconds_to_reset'] = (datetime.datetime.fromtimestamp(int(response.headers['RateLimit-Reset'])) - datetime.datetime.now()).total_seconds()

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
            self.headers = {"PRIVATE-TOKEN" : self.oauths[0]['access_token']}


    def update_gh_rate_limit(self, response, bad_credentials=False, temporarily_disable=False):
        # Try to get rate limit from request headers, sometimes it does not work (GH's issue)
        #   In that case we just decrement from last recieved header count
        if bad_credentials and len(self.oauths) > 1:
            self.logger.warning("Removing oauth with bad credentials from consideration: {}".format(self.oauths[0]))
            del self.oauths[0]

        if temporarily_disable:
            self.logger.debug("Github thinks we are abusing their api. Preventing use of this key until it resets...\n")
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
                self.logger.error("Could not get reset time from headers because of error: {}".format(e))
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

                attempts = 3
                success = False
                while attempts > 0 and not success:
                    response = requests.get(url=url, headers=self.headers)
                    try:
                        oauth['rate_limit'] = int(response.headers['X-RateLimit-Remaining'])
                        oauth['seconds_to_reset'] = (datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])) - datetime.datetime.now()).total_seconds()
                        success = True
                    except Exception as e:
                        self.logger.info(f'oath method ran into error getting info from headers: {e}\n')
                        self.logger.info(f'{self.headers}\n{url}\n')
                    attempts -= 1
                if not success:
                    continue

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

    def update_rate_limit(self, response, bad_credentials=False, temporarily_disable=False, platform="gitlab"):
        if platform == 'gitlab':
            return self.update_gitlab_rate_limit(response, bad_credentials=bad_credentials,
                                        temporarily_disable=temporarily_disable)
        elif platform == 'github':
            return self.update_gh_rate_limit(response, bad_credentials=bad_credentials,
                                        temporarily_disable=temporarily_disable)
