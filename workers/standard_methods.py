""" Helper methods constant across all workers """
import requests, datetime, time, traceback, json, os, sys, math
import sqlalchemy as s
import pandas as pd
import os
import sys, logging
from urllib.parse import urlparse

def assign_tuple_action(self, new_data, table_values, update_col_map, duplicate_col_map, table_pkey, value_update_col_map={}):
    """ map objects => { *our db col* : *gh json key*} """
    need_insertion_count = 0
    need_update_count = 0
    for i, obj in enumerate(new_data):
        if type(obj) != dict:
            logging.info('Moving to next tuple, tuple is not dict: {}'.format(obj))
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

            logging.info('Found a tuple that needs insertion based on dupe key: {}\n'.format(db_dupe_key))
            obj['flag'] = 'need_insertion'
            need_insertion_count += 1
            break

        if obj['flag'] == 'need_insertion':
            logging.info('Already determined that current tuple needs insertion, skipping checking updates. '
                'Moving to next tuple.\n')
            continue

        # If we need to check the values of the existing tuple to determine if an update is needed
        for augur_col, value_check in value_update_col_map.items():
            not_nan_check = not (pd.isna(value_check) and pd.isna(existing_tuple[augur_col])) if value_check is not None else True
            if existing_tuple[augur_col] != value_check and not_nan_check:
                continue
            logging.info("Found a tuple that needs an update for column: {}\n".format(augur_col)) 
            obj['flag'] = 'need_update'
            obj['pkey'] = existing_tuple[table_pkey]
            need_update_count += 1

        if obj['flag'] == 'need_update':
            logging.info('Already determined that current tuple needs update, skipping checking further updates. '
                'Moving to next tuple.\n')
            continue

        # Now check the existing tuple's values against the response values to determine if an update is needed
        for col in update_col_map.keys():
            if update_col_map[col] not in obj:
                continue
            if obj[update_col_map[col]] == existing_tuple[col]:
                continue
            logging.info("Found a tuple that needs an update for column: {}\n".format(col)) 
            obj['flag'] = 'need_update'
            obj['pkey'] = existing_tuple[table_pkey]
            need_update_count += 1

    logging.info("Page recieved has {} tuples, while filtering duplicates this ".format(len(new_data)) +
        "was reduced to {} tuples, and {} tuple updates are needed.\n".format(need_insertion_count, need_update_count))
    return new_data

def check_duplicates(new_data, table_values, key):
    need_insertion = []
    for obj in new_data:
        if type(obj) == dict:
            if not table_values.isin([obj[key]]).any().any():
                need_insertion.append(obj)
            # else:
                # logging.info("Tuple with github's {} key value already".format(key) +
                #     "exists in our db: {}\n".format(str(obj[key])))
    logging.info("Page recieved has {} tuples, while filtering duplicates this ".format(str(len(new_data))) +
        "was reduced to {} tuples.\n".format(str(len(need_insertion))))
    return need_insertion

def connect_to_broker(self):
    connected = False
    for i in range(5):
        try:
            logging.info("attempt {}\n".format(i))
            if i > 0:
                time.sleep(10)
            requests.post('http://{}:{}/api/unstable/workers'.format(
                self.config['broker_host'],self.config['broker_port']), json=self.specs)
            logging.info("Connection to the broker was successful\n")
            connected = True
            break
        except requests.exceptions.ConnectionError:
            logging.error('Cannot connect to the broker. Trying again...\n')
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
        logging.info("contributor needs to be added...")

    cntrb_url = ("https://api.github.com/users/" + login)
    logging.info("Hitting endpoint: {} ...\n".format(cntrb_url))
    r = requests.get(url=cntrb_url, headers=self.headers)
    update_gh_rate_limit(self, r)
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
    logging.info("Primary key inserted into the contributors table: " + str(result.inserted_primary_key))
    self.results_counter += 1
    self.cntrb_id_inc = int(result.inserted_primary_key[0])

    logging.info("Inserted contributor: " + contributor['login'] + "\n")
    
    return find_id_from_login(self, login)

def get_owner_repo(github_url):
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
        logging.info("Found max id for {} column in the {} table: {}\n".format(column, table, max_id))
    else:
        max_id = default
        logging.info("Could not find max id for {} column in the {} table... using default set to: \
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
    logging.info("Getting table values with the following PSQL query: \n{}\n".format(tableValuesSQL))
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
    """.format(self.config['key']))
    for oauth in [{'oauth_id': 0, 'access_token': self.config['key']}] + json.loads(pd.read_sql(oauthSQL, self.helper_db, params={}).to_json(orient="records")):
        self.headers = {'Authorization': 'token %s' % oauth['access_token']}
        logging.info("Getting rate limit info for oauth: {}\n".format(oauth))
        response = requests.get(url=url, headers=self.headers)
        self.oauths.append({
                'oauth_id': oauth['oauth_id'],
                'access_token': oauth['access_token'],
                'rate_limit': int(response.headers['X-RateLimit-Remaining']),
                'seconds_to_reset': (datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])) - datetime.datetime.now()).total_seconds()
            })
        logging.info("Found OAuth available for use: {}\n\n".format(self.oauths[-1]))

    if len(self.oauths) == 0:
        logging.info("No API keys detected, please include one in your config or in the worker_oauths table in the augur_operations schema of your database\n")

    # First key to be used will be the one specified in the config (first element in 
    #   self.oauths array will always be the key in use)
    self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}

def paginate(self, url, duplicate_col_map, update_col_map, table, table_pkey, where_clause="", value_update_col_map={}, platform="github"):
    # Paginate backwards through all the tuples but get first page in order
    #   to determine if there are multiple pages and if the 1st page covers all
    update_keys = list(update_col_map.keys()) if update_col_map else []
    update_keys += list(value_update_col_map.keys()) if value_update_col_map else []
    cols_query = list(duplicate_col_map.keys()) + update_keys + [table_pkey]
    table_values = get_table_values(self, cols_query, [table], where_clause)

    i = 1
    multiple_pages = False
    tuples = []
    while True:
        num_attempts = 0
        success = False
        while num_attempts < 3:
            logging.info("Hitting endpoint: " + url.format(i) + " ...\n")
            r = requests.get(url=url.format(i), headers=self.headers)
            update_gh_rate_limit(self, r)
            if platform == "github":
                last_page = r.links['last']['url'][-6:].split('=')[1]
            elif platform == "gitlab":
                last_page =  r.links['last']['url'].split('&')[2].split("=")[1]
            logging.info("Analyzing page {} of {}\n".format(i, int(last_page) + 1 if 'last' in r.links else '*last page not known*'))

            try:
                j = r.json()
            except:
                j = json.loads(json.dumps(r.text))

            if type(j) != dict and type(j) != str:
                success = True
                break
            elif type(j) == dict:
                logging.info("Request returned a dict: {}\n".format(j))
                if j['message'] == 'Not Found':
                    logging.info("Github repo was not found or does not exist for endpoint: {}\n".format(url))
                    break
                if j['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                    num_attempts -= 1
                    update_gh_rate_limit(self, r, temporarily_disable=True)
                if j['message'] == 'Bad credentials':
                    update_gh_rate_limit(self, r, bad_credentials=True)
            elif type(j) == str:
                logging.info("J was string: {}\n".format(j))
                if '<!DOCTYPE html>' in j:
                    logging.info("HTML was returned, trying again...\n")
                elif len(j) == 0:
                    logging.info("Empty string, trying again...\n")
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
                i =  int(r.links['last']['url'].split('&')[2].split("=")[1])
            logging.info("Multiple pages of request, last page is " + str(i - 1) + "\n")
            multiple_pages = True
        elif not multiple_pages and not self.finishing_task:
            logging.info("Only 1 page of request\n")
        elif self.finishing_task:
            logging.info("Finishing a previous task, paginating forwards ..."
                " excess rate limit requests will be made\n")
        
        if len(j) == 0:
            logging.info("Response was empty, breaking from pagination.\n")
            break
            
        # Checking contents of requests with what we already have in the db
        j = assign_tuple_action(self, j, table_values, update_col_map, duplicate_col_map, table_pkey, value_update_col_map)
        if not j:
            logging.info("Assigning tuple action failed, moving to next page.\n")
            i = i + 1 if self.finishing_task else i - 1
            continue
        try:
            to_add = [obj for obj in j if obj not in tuples and (obj['flag'] != 'none' or include_all)]
        except Exception as e:
            logging.info("Failure accessing data of page: {}. Moving to next page.\n".format(e))
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

def query_gitlab_contributors(self, entry_info, repo_id):
    """ 
    Contributors Info Collection function - GitLab
    Query the GitHub API for contributors
    """
    pass

def query_github_contributors(self, entry_info, repo_id):

    """ Data collection function
    Query the GitHub API for contributors
    """
    logging.info("Querying contributors with given entry info: " + str(entry_info) + "\n")

    github_url = entry_info['given']['github_url'] if 'github_url' in entry_info['given'] else entry_info['given']['git_url']

    # Extract owner/repo from the url for the endpoin_t
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
    contributors = paginate(self, contributors_url, duplicate_col_map, update_col_map, table, table_pkey)
    
    logging.info("Count of contributors needing insertion: " + str(len(contributors)) + "\n")
    
    for repo_contributor in contributors:
        try:
            # Need to hit this single contributor endpoint to get extra data including...
            #   `created at`
            #   i think that's it
            cntrb_url = ("https://api.github.com/users/" + repo_contributor['login'])
            logging.info("Hitting endpoint: " + cntrb_url + " ...\n")
            r = requests.get(url=cntrb_url, headers=self.headers)
            update_gh_rate_limit(self, r)
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
            logging.info("Caught exception: {}".format(e))
            logging.info("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
            continue

def read_config(section, name=None, environment_variable=None, default=None, config_file_path='../../augur.config.json', no_config_file=0, use_main_config=0):
    """
    Read a variable in specified section of the config file, unless provided an environment variable

    :param section: location of given variable
    :param name: name of variable
    """
    config_file_path = os.getenv("AUGUR_CONFIG_FILE", config_file_path)
    _config_file_name = 'augur.config.json'
    _config_bad = False
    _already_exported = {}
    _runtime_location = 'runtime/'
    _default_config = {}
    _config_file = None

    try:
        _config_file = open(config_file_path, 'r+')
    except:
        print('Couldn\'t open {}'.format(_config_file_name))

    # Load the config file
    try:
        config_text = _config_file.read()
        _config = json.loads(config_text)
    except json.decoder.JSONDecodeError as e:
        if not _config_bad:
            _using_config_file = False
            print('{} could not be parsed, using defaults. Fix that file, or delete it and run this again to regenerate it. Error: {}'.format(config_file_path, str(e)))
        _config = _default_config

    value = None
    if environment_variable is not None:
        value = os.getenv(environment_variable)
    if value is None:
        try:
            if name is not None:
                value = _config[section][name]
            else:
                value = _config[section]
        except Exception as e:
            value = default
            if not section in _config:
                _config[section] = {}

    return value


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
        result = self.helper_db.execute(self.history_table.update().where(
            self.history_table.c.history_id==self.history_id).values(task_history))
        self.history_id += 1
    else:
        result = self.helper_db.execute(self.history_table.insert().values(task_history))
        logging.info("Record incomplete history tuple: {}\n".format(result.inserted_primary_key))
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
        register_task_failure(self, task, repo_id, "INVALID_GIVEN: not github nor git url")
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

def register_task_failure(self, task, repo_id, e):

    logging.info("Worker ran into an error for task: {}\n".format(task))
    logging.info("Printing traceback...\n")
    tb = traceback.format_exc()
    logging.info(tb)

    logging.info(f'This task inserted {self.results_counter} tuples before failure.\n')
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
        logging.error('Could not send task failure message to the broker\n')
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
        logging.info("Removing oauth with bad credentials from consideration: {}".format(self.oauths[0]))
        del self.oauths[0]

    if temporarily_disable:
        logging.info("Github thinks we are abusing their api. Preventing use of this key until it resets...\n")
        self.oauths[0]['rate_limit'] = 0
    else:
        try:
            self.oauths[0]['rate_limit'] = int(response.headers['X-RateLimit-Remaining'])
            logging.info("Recieved rate limit from headers\n")
        except:
            self.oauths[0]['rate_limit'] -= 1
            logging.info("Headers did not work, had to decrement\n")
    logging.info("Updated rate limit, you have: " + 
        str(self.oauths[0]['rate_limit']) + " requests remaining.\n")
    if self.oauths[0]['rate_limit'] <= 0:
        try:
            reset_time = response.headers['X-RateLimit-Reset']
        except Exception as e:
            logging.info("Could not get reset time from headers because of error: {}".format(e))
            logging.info('Headers: {}'.format(response.headers))
            reset_time = 3600
        time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
        logging.info("Rate limit exceeded, checking for other available keys to use.\n")

        # We will be finding oauth with the highest rate limit left out of our list of oauths
        new_oauth = self.oauths[0]
        # Endpoint to hit solely to retrieve rate limit information from headers of the response
        url = "https://api.github.com/users/gabe-heim"

        other_oauths = self.oauths[0:] if len(self.oauths) > 1 else []
        for oauth in other_oauths:
            logging.info("Inspecting rate limit info for oauth: {}\n".format(oauth))
            self.headers = {'Authorization': 'token %s' % oauth['access_token']}
            response = requests.get(url=url, headers=self.headers)
            oauth['rate_limit'] = int(response.headers['X-RateLimit-Remaining'])
            oauth['seconds_to_reset'] = (datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])) - datetime.datetime.now()).total_seconds()

            # Update oauth to switch to if a higher limit is found
            if oauth['rate_limit'] > new_oauth['rate_limit']:
                logging.info("Higher rate limit found in oauth: {}\n".format(oauth))
                new_oauth = oauth
            elif oauth['rate_limit'] == new_oauth['rate_limit'] and oauth['seconds_to_reset'] < new_oauth['seconds_to_reset']:
                logging.info("Lower wait time found in oauth with same rate limit: {}\n".format(oauth))
                new_oauth = oauth

        if new_oauth['rate_limit'] <= 0 and new_oauth['seconds_to_reset'] > 0:
            logging.info("No oauths with >0 rate limit were found, waiting for oauth with smallest wait time: {}\n".format(new_oauth))
            time.sleep(new_oauth['seconds_to_reset'])

        # Make new oauth the 0th element in self.oauths so we know which one is in use
        index = self.oauths.index(new_oauth)
        self.oauths[0], self.oauths[index] = self.oauths[index], self.oauths[0]
        logging.info("Using oauth: {}\n".format(self.oauths[0]))

        # Change headers to be using the new oauth's key
        self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}
