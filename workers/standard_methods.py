""" Helper methods constant across all workers """
import requests, datetime, time
import sqlalchemy as s
import pandas as pd

def connect_to_broker(self, logging):
    connected = False
    for i in range(5):
        try:
            logging.info("attempt {}".format(i))
            if i > 0:
                time.sleep(10)
            requests.post('http://{}:{}/api/unstable/workers'.format(
                self.config['broker_host'],self.config['broker_port']), json=self.specs)
            logging.info("Connection to the broker was successful")
            connected = True
            break
        except requests.exceptions.ConnectionError:
            logging.error('Cannot connect to the broker. Trying again...')
    if not connected:
        sys.exit('Could not connect to the broker after 5 attempts! Quitting...')

def record_model_process(self, logging, repo_id, model):

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
        result = self.helper_db.execute(self.history_table.update().where(
            self.history_table.c.history_id==self.history_id).values(task_history))
    else:
        result = self.helper_db.execute(self.history_table.insert().values(task_history))
        logging.info("Record incomplete history tuple: {}".format(result.inserted_primary_key))
        self.history_id = int(result.inserted_primary_key[0])

def register_task_completion(self, logging, entry_info, repo_id, model):
    # Task to send back to broker
    task_completed = {
        'worker_id': self.config['id'],
        'job_type': self.working_on,
        'repo_id': repo_id,
        'github_url': entry_info['given']['github_url'],
        'job_model': model
    }
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
    self.helper_db.execute(self.history_table.update().where(
        self.history_table.c.history_id==self.history_id).values(task_history))

    logging.info("Recorded job completion for: " + str(task_completed) + "\n")

    # Update job process table
    updated_job = {
        "since_id_str": repo_id,
        "last_count": self.results_counter,
        "last_run": datetime.datetime.now(),
        "analysis_state": 0
    }
    self.helper_db.execute(self.job_table.update().where(
        self.job_table.c.job_model==model).values(updated_job))
    logging.info("Updated job process for model: " + model + "\n")

    # Notify broker of completion
    logging.info("Telling broker we completed task: " + str(task_completed) + "\n\n" + 
        "This task inserted: " + str(self.results_counter) + " tuples.\n\n")

    requests.post('http://{}:{}/api/unstable/completed_task'.format(
        self.config['broker_host'],self.config['broker_port']), json=task_completed)

    # Reset results counter for next task
    self.results_counter = 0

def register_task_failure(self, logging, task, repo_id, e):

    logging.info("Worker ran into an error for task: {}".format(task))
    logging.info("Error encountered: " + repr(e))
    logging.info(f'This task inserted {self.results_counter} tuples before failure.')
    logging.info("Notifying broker and logging task failure in database...\n")

    github_url = task['given']['github_url']

    """ Query all repos with repo url of given task """
    repoUrlSQL = s.sql.text("""
        SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
        """.format(github_url))
    repo_id = int(pd.read_sql(repoUrlSQL, self.db, params={}).iloc[0]['repo_id'])

    task['worker_id'] = self.config['id']
    try:
        requests.post("http://{}:{}/api/unstable/task_error".format(
            self.config['broker_host'],self.config['broker_port']), json=task)
    except requests.exceptions.ConnectionError:
        logging.error('Could not send task failure message to the broker')
    except Exception:
        logging.exception('An error occured while informing broker about task failure')

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
    self.helper_db.execute(self.history_table.update().where(self.history_table.c.history_id==self.history_id).values(task_history))

    logging.info("Recorded job error in the history table for: " + str(task) + "\n")

    # Update job process table
    updated_job = {
        "since_id_str": repo_id,
        "last_count": self.results_counter,
        "last_run": datetime.datetime.now(),
        "analysis_state": 0
    }
    self.helper_db.execute(self.job_table.update().where(self.job_table.c.job_model==task['models'][0]).values(updated_job))
    logging.info("Updated job process for model: " + task['models'][0] + "\n")

    # Reset results counter for next task
    self.results_counter = 0    

def update_gh_rate_limit(self, logging, response):
    # Try to get rate limit from request headers, sometimes it does not work (GH's issue)
    #   In that case we just decrement from last recieved header count
    try:
        self.oauths[0]['rate_limit'] = int(response.headers['X-RateLimit-Remaining'])
        logging.info("Recieved rate limit from headers\n")
    except:
        self.oauths[0]['rate_limit'] -= 1
        logging.info("Headers did not work, had to decrement\n")
    logging.info("Updated rate limit, you have: " + 
        str(self.oauths[0]['rate_limit']) + " requests remaining.\n")
    if self.oauths[0]['rate_limit'] <= 0:
        reset_time = response.headers['X-RateLimit-Reset']
        time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
        logging.info("Rate limit exceeded, checking for other available keys to use.\n")

        # We will be finding oauth with the highest rate limit left out of our list of oauths
        new_oauth = self.oauths[0]
        # Endpoint to hit solely to retrieve rate limit information from headers of the response
        url = "https://api.github.com/users/gabe-heim"

        for oauth in self.oauths:
            logging.info("Inspecting rate limit info for oauth: {}\n".format(oauth))
            self.headers = {'Authorization': 'token %s' % oauth['access_token']}
            response = requests.get(url=url, headers=self.headers)
            oauth['rate_limit'] = int(response.headers['X-RateLimit-Remaining'])
            oauth['seconds_to_reset'] = (datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])) - datetime.datetime.now()).total_seconds()

            # Update oauth to switch to if a higher limit is found
            if oauth['rate_limit'] > new_oauth['rate_limit']:
                logging.info("Higher rate limit found in oauth: {}".format(oauth))
                new_oauth = oauth
            elif oauth['rate_limit'] == new_oauth['rate_limit'] and oauth['seconds_to_reset'] < new_oauth['seconds_to_reset']:
                logging.info("Lower wait time found in oauth with same rate limit: {}".format(oauth))
                new_oauth = oauth

        if new_oauth['rate_limit'] <= 0:
            logging.info("No oauths with >0 rate limit were found, waiting for oauth with smallest wait time: {}".format(new_oauth))
            time.sleep(new_oauth['seconds_to_reset'])

        # Change headers to be using the new oauth's key
        self.headers = {'Authorization': 'token %s' % new_oauth['access_token']}

        # Make new oauth the 0th element in self.oauths so we know which one is in use
        index = self.oauths.index(new_oauth)
        self.oauths[0], self.oauths[index] = self.oauths[index], self.oauths[0]
        logging.info("Using oauth: {}".format(self.oauths[0]))
