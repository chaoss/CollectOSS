
from workers.worker_persistance import *
#I figure I can seperate this class into at least three parts.
#I should also look into the subclass and see what uses what.
#
#   Parts (Hierarchal relation)
#1. Persistance
#2. Base
#3. Github/lab 
# Might be good to seperate the machine learning functionality into its own class too.


class Worker(Persistant):

    ## Set Thread Safety for OSX
    # os.system("./osx-thread.sh")

    def __init__(self, worker_type, config={}, given=[], models=[], data_tables=[], operations_tables=[], platform="github"):

        #Construct the persistant functionality for the worker
        super().__init__(worker_type,data_tables,operations_tables)
        self.collection_start_time = None
        self._task = None # task currently being worked on (dict)
        self._child = None # process of currently running task (multiprocessing process)
        self._queue = Queue() # tasks stored here 1 at a time (in a mp queue so it can translate across multiple processes)

        # if we are finishing a previous task, certain operations work differently
        self.finishing_task = False
        # Update config with options that are general and not specific to any worker
        self.augur_config = AugurConfig(self._root_augur_dir)

        #TODO: consider taking parts of this out for the base class and then overriding it in WorkerGitInterfaceable
        self.config.update({'offline_mode': False})

        self.config.update(config)


        self.task_info = None
        self.repo_id = None
        self.owner = None
        self.repo = None
        self.given = given
        self.models = models
        self.debug_data = [] if 'debug_data' not in self.config else self.config['debug_data']
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
        if self.config['offline_mode'] is False:
            self.connect_to_broker()

        try:
            self.tool_source
            self.tool_version
            self.data_source
        except:
            self.tool_source = 'Augur Worker Testing'
            self.tool_version = '0.0.0'
            self.data_source = 'Augur Worker Testing'

    def write_debug_data(self, data, name):
        """
            Writes json data to file, so it doesn't clog the log files

            :param data: json - json data that needs to be dumped to a file
            :param name: string - name of file to dump json data to
        """
        if name in self.debug_data:
            with open(f'{name}.json', 'w') as f:
                json.dump(data, f)

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
        #self.logger.info("Got to this point.")
        #self.logger.info(f"This is the oauths 0 index {self.oauths}")
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
                #TODO: set this to record exceptions seperatly. This errored and it took a while to figure that ^ wasn't the line that was erroring.
                self.record_model_process(repo_id, 'repo_info')
            except Exception as e:
                self.logger.error('Error: {}.\nNo defined method for model: {}, '.format(e, message['models'][0]) +
                    'must have name of {}_model'.format(message['models'][0]))
                self.register_task_failure(message, repo_id, e)
                break

            # Model method calls wrapped in try/except so that any unexpected error that occurs can be caught
            #   and worker can move onto the next task without stopping
            try:
                self.logger.info("Calling model method {}_model".format(message['models'][0]))
                self.task_info = message
                self.repo_id = repo_id
                self.owner, self.repo = self.get_owner_repo(list(message['given'].values())[0])
                model_method(message, repo_id)
            except Exception as e: # this could be a custom exception, might make things easier
                self.register_task_failure(message, repo_id, e)
                break

        self.logger.debug('Closing database connections\n')
        self.db.dispose()
        self.helper_db.dispose()
        self.logger.info("Collection process finished")

    def connect_to_broker(self):
        """
        Connects to the broker,
        with 5 attempts at a successful connection,
        and sleeps 10 seconds after each failed connection
        """
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
        """ Empties all pending items in a queue and returns them in a list.
        """
        result = []
        queue.put("STOP")
        for i in iter(queue.get, 'STOP'):
            result.append(i)
        # time.sleep(.1)
        return result

    def find_id_from_login(self, login, platform='github'):
        """ Retrieves our contributor table primary key value for the contributor with
            the given GitHub login credentials, if this contributor is not there, then
            they get inserted.

        :param login: String, the GitHub login username to find the primary key id for
        :return: Integer, the id of the row in our database with the matching GitHub login
        """
        idSQL = s.sql.text("""
            SELECT cntrb_id FROM contributors WHERE cntrb_login = '{}' \
            AND LOWER(data_source) = '{} api'
            """.format(login, platform))

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


        while True:
            try:
                r = requests.get(url=cntrb_url, headers=self.headers)
                break
            except TimeoutError as e:
                self.logger.info("Request timed out. Sleeping 10 seconds and trying again...\n")
                time.sleep(30)

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
                'cntrb_login': contributor['login'] if 'login' in contributor else None,
                'cntrb_email': contributor['email'] if 'email' in contributor else None,
                'cntrb_company': contributor['company'] if 'company' in contributor else None,
                'cntrb_location': contributor['location'] if 'location' in contributor else None,
                'cntrb_created_at': contributor['created_at'] if 'created_at' in contributor else None,
                'cntrb_canonical': contributor['email'] if 'email' in contributor else None,
                'gh_user_id': contributor['id'] if 'id' in contributor else None,
                'gh_login': contributor['login'] if 'login' in contributor else None,
                'gh_url': contributor['url'] if 'url' in contributor else None,
                'gh_html_url': contributor['html_url'] if 'html_url' in contributor else None,
                'gh_node_id': contributor['node_id'] if 'node_id' in contributor else None,
                'gh_avatar_url': contributor['avatar_url'] if 'avatar_url' in contributor else None,
                'gh_gravatar_id': contributor['gravatar_id'] if 'gravatar_id' in contributor else None,
                'gh_followers_url': contributor['followers_url'] if 'followers_url' in contributor else None,
                'gh_following_url': contributor['following_url'] if 'following_url' in contributor else None,
                'gh_gists_url': contributor['gists_url'] if 'gists_url' in contributor else None,
                'gh_starred_url': contributor['starred_url'] if 'starred_url' in contributor else None,
                'gh_subscriptions_url': contributor['subscriptions_url'] if 'subscriptions_url' in contributor else None,
                'gh_organizations_url': contributor['organizations_url'] if 'organizations_url' in contributor else None,
                'gh_repos_url': contributor['repos_url'] if 'repos_url' in contributor else None,
                'gh_events_url': contributor['events_url'] if 'events_url' in contributor else None,
                'gh_received_events_url': contributor['received_events_url'] if 'received_events_url' in contributor else None,
                'gh_type': contributor['type'] if 'type' in contributor else None,
                'gh_site_admin': contributor['site_admin'] if 'site_admin' in contributor else None,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }

        elif platform == 'gitlab':
            cntrb =  {
                'cntrb_login': contributor[0]['username'] if 'username' in contributor[0] else None,
                'cntrb_email': email,
                'cntrb_company': company,
                'cntrb_location': location,
                'cntrb_created_at': contributor[0]['created_at'] if 'created_at' in contributor[0] else None,
                'cntrb_canonical': email,
                'gh_user_id': contributor[0]['id'],
                'gh_login': contributor[0]['username'],
                'gh_url': contributor[0]['web_url'],
                'gh_html_url': None,
                'gh_node_id': None,
                'gh_avatar_url': contributor[0]['avatar_url'],
                'gh_gravatar_id': None,
                'gh_followers_url': None,
                'gh_following_url': None,
                'gh_gists_url': None,
                'gh_starred_url': None,
                'gh_subscriptions_url': None,
                'gh_organizations_url': None,
                'gh_repos_url': None,
                'gh_events_url': None,
                'gh_received_events_url': None,
                'gh_type': None,
                'gh_site_admin': None,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }
        result = self.db.execute(self.contributors_table.insert().values(cntrb))
        self.logger.info("Primary key inserted into the contributors table: " + str(result.inserted_primary_key))
        self.results_counter += 1
        self.cntrb_id_inc = int(result.inserted_primary_key[0])
        self.logger.info(f"Inserted contributor: {cntrb['cntrb_login']}\n")

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

    def record_model_process(self, repo_id, model):

        self.logger.info(f"This is the oauths 0 index {self.oauths[0]}")
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

        self.collection_start_time = time.time()

    def register_task_completion(self, task, repo_id, model):
        """Registers a task as complete with broker,
        adds task to the worker_history table,
        and updates the worker_job table"""

        self.logger.info(f"Worker completed this task in {self.collection_start_time - time.time()} seconds.\n")

        # Task to send back to broker
        task_completed = {
            'worker_id': self.config['id'],
            'job_type': "MAINTAIN",
            'repo_id': repo_id,
            'job_model': model
        }

        key = None
        if 'github_url' in task['given']:
            key = 'github_url'
        elif 'git_url' in task['given']:
            key = 'git_url'
        elif 'gitlab_url' in task['given']:
            key = 'gitlab_url'
        else:
            self.register_task_failure(task, repo_id, "INVALID_GIVEN: Not a github/gitlab/git url.")
            return

        task_completed[key] = task['given'][key]
        
        # Add to history table
        task_history = {
            'repo_id': repo_id,
            'worker': self.config['id'],
            'job_model': model,
            'oauth_id': self.oauths[0]['oauth_id'],
            'timestamp': datetime.datetime.now(),
            'status': "Success",
            'total_results': self.results_counter
        }
        self.helper_db.execute(self.worker_history_table.update().where(
            self.worker_history_table.c.history_id==self.history_id).values(task_history))

        self.logger.info(f"Recorded job completion for: {task_completed}\n")

        # Update job process table
        updated_job = {
            'since_id_str': repo_id,
            'last_count': self.results_counter,
            'last_run': datetime.datetime.now(),
            'analysis_state': 0
        }
        self.helper_db.execute(self.worker_job_table.update().where(
            self.worker_job_table.c.job_model==model).values(updated_job))
        self.logger.info(f"Updated job process for model: {model}\n")

        if self.config['offline_mode'] is False:

            # Notify broker of completion
            self.logger.info(f"Telling broker we completed task: {task_completed}\n")
            self.logger.info(f"This task inserted: {self.results_counter + self.insert_counter} tuples " +
                f"and updated {self.update_counter} tuples.\n")

            requests.post('http://{}:{}/api/unstable/completed_task'.format(
                self.config['host_broker'],self.config['port_broker']), json=task_completed)

        # Reset results counter for next task
        self.results_counter = 0
        self.insert_counter = 0
        self.update_counter = 0

    def register_task_failure(self, task, repo_id, e):
        """Registers a task as failed with the broker,
        updates the worker_history table,
        and updates the worker_job table"""

        self.logger.error(f"Worker ran into an error for task: {task}")
        self.logger.error(
            f"Worker was processing this task for {self.collection_start_time - time.time()} "
            "seconds."
        )
        self.logger.error("Printing traceback...")
        self.logger.error(e)
        tb = traceback.format_exc()
        self.logger.error(tb)

        self.logger.info(f"This task inserted {self.results_counter} tuples before failure.")
        self.logger.info("Notifying broker and logging task failure in database...")
        key = (
            'github_url' if 'github_url' in task['given'] else 'git_url'
            if 'git_url' in task['given'] else 'gitlab_url'
            if 'gitlab_url' in task['given'] else 'INVALID_GIVEN'
        )
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
            self.logger.error("Could not send task failure message to the broker:")
            self.logger.error(e)
        except Exception:
            self.logger.error("An error occured while informing broker about task failure:")
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
        self.helper_db.execute(
            self.worker_history_table.update().where(
                self.worker_history_table.c.history_id==self.history_id
            ).values(task_history)
        )

        self.logger.error(f"Recorded job error in the history table for: {task}")

        # Update job process table
        updated_job = {
            "since_id_str": repo_id,
            "last_count": self.results_counter,
            "last_run": datetime.datetime.now(),
            "analysis_state": 0
        }
        self.helper_db.execute(
            self.worker_job_table.update().where(
                self.worker_job_table.c.job_model==task['models'][0]
            ).values(updated_job)
        )
        self.logger.info(f"Updated job process for model: {task['models'][0]}\n")

        # Reset results counter for next task
        self.results_counter = 0
