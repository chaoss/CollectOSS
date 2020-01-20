""" Helper methods constant across all workers """
import requests, datetime, time, traceback, json
import sqlalchemy as s
import pandas as pd

def assign_tuple_action(self, logging, new_data, table_values, update_col_map, duplicate_col_map, table_pkey):
    """ map objects => { *our db col* : *gh json key*} """
    need_insertion_count = 0
    need_update_count = 0
    for obj in new_data:
        if type(obj) != dict:
            continue
        obj['flag'] = 'none' # default of no action needed
        for db_dupe_key in list(duplicate_col_map.keys()):
            if obj['flag'] == 'need_insertion' or obj['flag'] == 'need_update':
                break
            if not table_values.isin([obj[duplicate_col_map[db_dupe_key]]]).any().any():
                obj['flag'] = 'need_insertion'
                need_insertion_count += 1
            elif update_col_map:
                existing_tuple = table_values[table_values[db_dupe_key].isin(
                    [obj[duplicate_col_map[db_dupe_key]]])].to_dict('records')[0]
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
    logging.info("Page recieved has {} tuples, while filtering duplicates this ".format(len(new_data)) +
        "was reduced to {} tuples, and {} tuple updates are needed.\n".format(need_insertion_count, need_update_count))
    return new_data

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

def get_max_id(self, logging, table, column, default=25150, operations_table=False):
    maxIdSQL = s.sql.text("""
        SELECT max({0}.{1}) AS {1}
        FROM {0}
    """.format(table, column))
    db = self.db if not operations_table else self.helper_db
    rs = pd.read_sql(maxIdSQL, db, params={})
    if rs.iloc[0][column] is not None:
        max_id = int(rs.iloc[0][column]) + 1  
        logging.info("Found max id for {} column in the {} table: {}".format(column, table, max_id))
    else:
        max_id = default
        logging.info("Could not find max id for {} column in the {} table... using default set to: {}".format(column, table, max_id))
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
    logging.info("Getting table values with the following PSQL query: \n{}\n".format(tableValuesSQL))
    values = pd.read_sql(tableValuesSQL, self.db, params={})
    return values

def init_oauths(self, logging):
    self.oauths = []
    self.headers = None

    # Endpoint to hit solely to retrieve rate limit information from headers of the response
    url = "https://api.github.com/users/gabe-heim"

    # Make a list of api key in the config combined w keys stored in the database
    oauthSQL = s.sql.text("""
        SELECT * FROM worker_oauth WHERE access_token <> '{}'
    """.format(self.config['key']))
    for oauth in [{'oauth_id': 0, 'access_token': self.config['key']}] + json.loads(pd.read_sql(oauthSQL, self.helper_db, params={}).to_json(orient="records")):
        self.headers = {'Authorization': 'token %s' % oauth['access_token']}
        logging.info("Getting rate limit info for oauth: {}".format(oauth))
        response = requests.get(url=url, headers=self.headers)
        self.oauths.append({
                'oauth_id': oauth['oauth_id'],
                'access_token': oauth['access_token'],
                'rate_limit': int(response.headers['X-RateLimit-Remaining']),
                'seconds_to_reset': (datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])) - datetime.datetime.now()).total_seconds()
            })
        logging.info("Found OAuth available for use: {}".format(self.oauths[-1]))

    if len(self.oauths) == 0:
        logging.info("No API keys detected, please include one in your config or in the worker_oauths table in the augur_operations schema of your database\n")

    # First key to be used will be the one specified in the config (first element in 
    #   self.oauths array will always be the key in use)
    self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}

def paginate(self, logging, url, duplicate_col_map, update_col_map, table, table_pkey, where_clause=""):
    # Paginate backwards through all the tuples but get first page in order
    #   to determine if there are multiple pages and if the 1st page covers all
    update_keys = list(update_col_map.keys()) if update_col_map else []
    cols_query = list(duplicate_col_map.keys()) + update_keys + [table_pkey]
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
        
        try:
            j = r.json()
        except:
            j = json.loads(json.dumps(j))

        if len(j) == 0:
            logging.info("Response was empty, breaking from pagination.\n")
            break
            
        # Checking contents of requests with what we already have in the db
        j = assign_tuple_action(self, logging, j, table_values, update_col_map, duplicate_col_map, table_pkey)
        if not j:# or type(j) != dict:
            logging.info("Assigning tuple action failed, moving to next page.\n")
            i = i + 1 if self.finishing_task else i - 1
            continue
        try:
            to_add = [obj for obj in j if obj not in tuples and obj['flag'] != 'none']
        except Exception as e:
            logging.info("Failure accessing data of page: {}. moving to next page.\n".format(e))
            i = i + 1 if self.finishing_task else i - 1
            continue
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

def read_config(section, name=None, environment_variable=None, default=None, config_file='augur.config.json', no_config_file=0, use_main_config=0):
    """
    Read a variable in specified section of the config file, unless provided an environment variable

    :param section: location of given variable
    :param name: name of variable
    """

    __config_bad = False
    if use_main_config == 0:
        __config_file_path = os.path.abspath(os.getenv('AUGUR_CONFIG_FILE', config_file))
    else:        
        __config_file_path = os.path.abspath(os.path.dirname(os.path.dirname(os.getcwd())) + '/augur.config.json')

    __config_location = os.path.dirname(__config_file_path)
    __export_env = os.getenv('AUGUR_ENV_EXPORT', '0') == '1'
    __default_config = { 'Database': {"host": "nekocase.augurlabs.io"} }

    if os.getenv('AUGUR_ENV_ONLY', '0') != '1' and no_config_file == 0:
        try:
            __config_file = open(__config_file_path, 'r+')
        except:
            # logger.info('Couldn\'t open {}, attempting to create. If you have a augur.cfg, you can convert it to a json file using "make to-json"'.format(config_file))
            if not os.path.exists(__config_location):
                os.makedirs(__config_location)
            __config_file = open(__config_file_path, 'w+')
            __config_bad = True


        # Options to export the loaded configuration as environment variables for Docker
        if __export_env:
            
            export_filename = os.getenv('AUGUR_ENV_EXPORT_FILE', 'augur.cfg.sh')
            __export_file = open(export_filename, 'w+')
            # logger.info('Exporting {} to environment variable export statements in {}'.format(config_file, export_filename))
            __export_file.write('#!/bin/bash\n')

        # Load the config file and return [section][name]
        try:
            config_text = __config_file.read()
            __config = json.loads(config_text)
            if name is not None:
                return(__config[section][name])
            else:
                return(__config[section])

        except json.decoder.JSONDecodeError as e:
            if not __config_bad:
                __using_config_file = False
                # logger.error('%s could not be parsed, using defaults. Fix that file, or delete it and run this again to regenerate it. Error: %s', __config_file_path, str(e))

            __config = __default_config
            try:
                return(__config[section][name])
            except:
                return(__config[section])

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

def register_task_completion(self, logging, task, repo_id, model):
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
        register_task_failure(self, logging, task, repo_id, "INVALID_GIVEN: not github nor git url")
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
    logging.info("Printing traceback...")
    tb = traceback.format_exc()
    logging.info(tb)

    logging.info(f'This task inserted {self.results_counter} tuples before failure.')
    logging.info("Notifying broker and logging task failure in database...\n")
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

        if new_oauth['rate_limit'] <= 0 and new_oauth['seconds_to_reset'] > 0:
            logging.info("No oauths with >0 rate limit were found, waiting for oauth with smallest wait time: {}".format(new_oauth))
            time.sleep(new_oauth['seconds_to_reset'])

        # Change headers to be using the new oauth's key
        self.headers = {'Authorization': 'token %s' % new_oauth['access_token']}

        # Make new oauth the 0th element in self.oauths so we know which one is in use
        index = self.oauths.index(new_oauth)
        self.oauths[0], self.oauths[index] = self.oauths[index], self.oauths[0]
        logging.info("Using oauth: {}".format(self.oauths[0]))
