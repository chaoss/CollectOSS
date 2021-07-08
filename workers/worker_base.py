
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

    #Might cut down on these args to create subclasses
    def __init__(self, worker_type, config={}, given=[], models=[], data_tables=[], operations_tables=[]):

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


        #base
        self.task_info = None
        self.repo_id = None
        #not sure
        self.owner = None
        #git interface overrides these
        self.repo = None
        self.given = given
        self.models = models

        #back to base, might be overwritten by git integration subclass?
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

            ##base, doesn't use keys

            # Query repo_id corresponding to repo url of given task
            repoUrlSQL = s.sql.text("""
                SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
                """.format(message['given'][self.given[0][0]]))
            repo_id = int(pd.read_sql(repoUrlSQL, self.db, params={}).iloc[0]['repo_id'])
            self.logger.info("repo_id for which data collection is being initiated: {}".format(str(repo_id)))
            # Call method corresponding to model sent in task
            try:
                model_method = getattr(self, '{}_model'.format(message['models'][0]))
            except Exception as e:
                self.logger.error('Error: {}.\nNo defined method for model: {}, '.format(e, message['models'][0]) +
                    'must have name of {}_model'.format(message['models'][0]))
                self.register_task_failure(message, repo_id, e)
                break

            #Better error handling
            try:
                self.record_model_process(repo_id, 'repo_info')
            except Exception as e:
                self.logger.error('Error: {}. \n Problem recording model process'.format(e))

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

    #doesn't even query the api just gets it based on the url string, can stay in base
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

        task_history = {
            "repo_id": repo_id,
            "worker": self.config['id'],
            "job_model": model,
            #"oauth_id": self.oauths[0]['oauth_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Stopped",
            "total_results": self.results_counter
        }
        #log oauth if it applies to worker.
        try:
            self.oauths
            task_history['oauth_id'] = self.oauths[0]['oauth_id']
        except AttributeError:
            pass

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

        self.logger.info(f"Worker completed this task in {self.collection_start_time - time.time()} seconds.\n")

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
            'repo_id': repo_id,
            'worker': self.config['id'],
            'job_model': model,
            #'oauth_id': self.oauths[0]['oauth_id'], #messes up with workers that don't have this attribute
            'timestamp': datetime.datetime.now(),
            'status': "Success",
            'total_results': self.results_counter
        }

        #log oauth if it applies to worker.
        try:
            self.oauths
            task_history['oauth_id'] = self.oauths[0]['oauth_id']
        except AttributeError:
            pass
        
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
            #"oauth_id": self.oauths[0]['oauth_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Error",
            "total_results": self.results_counter
        }

        #log oauth if it applies to worker.
        try:
            self.oauths
            task_history['oauth_id'] = self.oauths[0]['oauth_id']
        except AttributeError:
            pass

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
