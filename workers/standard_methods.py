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
        self.history_id += 1
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
        'job_model': model
    }
    key = 'github_url' if 'github_url' in entry_info['given'] else 'git_url' if 'git_url' in entry_info['given'] else "INVALID_GIVEN"
    task_completed[key] = entry_info['given']['github_url'] if 'github_url' in entry_info['given'] else entry_info['given']['git_url'] if 'git_url' in entry_info['given'] else "INVALID_GIVEN"
    if key == 'INVALID_GIVEN':
        register_task_failure(self, logging, entry_info, repo_id, "INVALID_GIVEN: not github nor git url")
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

def paginate(self, logging, url, duplicate_col_map, update_col_map, table, table_pkey, where_clause=""):
    # Paginate backwards through all the tuples but get first page in order
    #   to determine if there are multiple pages and if the 1st page covers all
    cols_query = list(duplicate_col_map.keys()) + list(update_col_map.keys()) + [table_pkey]
    table_values = self.get_table_values(cols_query, [table], where_clause)

    i = 1
    multiple_pages = False
    tuples = []
    while True: # (self, url)
        logging.info("Hitting endpoint: " + url.format(i) + " ...\n")
        r = requests.get(url=url.format(i), headers=self.headers)
        update_gh_rate_limit(self, logging, r)
        logging.info("Analyzing page {} of {}\n".format(i, int(r.links['last']['url'][-6:].split('=')[1]) + 1 if 'last' in r.links else '*last page not known*'))

        # Find last page so we can decrement from there
        if 'last' in r.links and not multiple_pages and not self.finishing_task:
            param = r.links['last']['url'][-6:]
            i = int(param.split('=')[1]) + 1
            logging.info("Multiple pages of request, last page is " + str(i - 1) + "\n")
            multiple_pages = True
        elif not multiple_pages and not self.finishing_task:
            logging.info("Only 1 page of request\n")
        elif self.finishing_task:
            logging.info("Finishing a previous task, paginating forwards ..."
                " excess rate limit requests will be made\n")
        
        j = r.json()

        if len(j) == 0:
            logging.info("Response was empty, breaking from pagination.\n")
            break
            
        # Checking contents of requests with what we already have in the db
        j = assign_tuple_action(self, logging, j, table_values, update_col_map, duplicate_col_map, table_pkey)
        if not j:
            logging.info("Assigning tuple action failed, moving to next page.\n")
            continue
        to_add = [obj for obj in j if obj not in tuples and obj['flag'] != 'none']
        if len(to_add) == 0 and multiple_pages and 'last' in r.links:
            logging.info("{}".format(r.links['last']))
            if i - 1 != int(r.links['last']['url'][-6:].split('=')[1]):
                logging.info("No more pages with unknown tuples, breaking from pagination.\n")
                break
        tuples += to_add

        i = i + 1 if self.finishing_task else i - 1

        # Since we already wouldve checked the first page... break
        if (i == 1 and multiple_pages and not self.finishing_task) or i < 1 or len(j) == 0:
            logging.info("No more pages to check, breaking from pagination.\n")
            break

    return tuples

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
    logging.info("Getting table values with the following PSQL query: \n{}\n".format(tableValuesSQL))
    values = pd.read_sql(tableValuesSQL, self.db, params={})
    return values

def assign_tuple_action(self, logging, new_data, table_values, update_col_map, duplicate_col_map, table_pkey):
    """ map objects => { *our db col* : *gh json key*} """
    need_insertion_count = 0
    need_update_count = 0
    for obj in new_data:
        if type(obj) != dict:
            continue
        obj['flag'] = 'none'
        for db_dupe_key in list(duplicate_col_map.keys()):
            if obj['flag'] == 'need_insertion' or obj['flag'] == 'need_update':
                break
            if table_values.isin([obj[duplicate_col_map[db_dupe_key]]]).any().any():
                # try:
                existing_tuple = table_values[table_values[db_dupe_key].isin(
                    [obj[duplicate_col_map[db_dupe_key]]])].to_dict('records')[0]
                # except:
                #     logging.info("IT FAILED BUT WE GOING")
                # logging.info(table_values[table_values[db_dupe_key].isin(
                #     [obj[duplicate_col_map[db_dupe_key]]])].to_dict('records'))
                for col in update_col_map.keys():
                    if update_col_map[col] not in obj:
                        continue
                    if obj[update_col_map[col]] != existing_tuple[col]:
                        logging.info("Found a tuple that needs an ".format(obj) +
                            "update for column: {}\n".format(col)) #obj[duplicate_col_map[db_dupe_key]]
                        obj['flag'] = 'need_update'
                        obj['pkey'] = existing_tuple[table_pkey]
                        need_update_count += 1
                        break
            else:
                obj['flag'] = 'need_insertion'
                need_insertion_count += 1
    logging.info("Page recieved has {} tuples, while filtering duplicates this ".format(len(new_data)) +
        "was reduced to {} tuples, and {} tuple updates are needed.\n".format(need_insertion_count, need_update_count))
    return new_data
