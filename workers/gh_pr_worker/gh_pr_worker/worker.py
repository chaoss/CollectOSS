import ast
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse

import pandas as pd
import requests
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base


logging.basicConfig(filename='worker.log', filemode='w', level=logging.INFO)

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

    :param queue: The queue to be emptied.
    """
    result = []
    queue.put("STOP")
    for i in iter(queue.get, 'STOP'):
        result.append(i)
    # time.sleep(.1)
    return result

class GHPullRequestWorker:
    """
    Worker that collects Pull Request related data from the Github API and stores it in our database.

    :param task: most recent task the broker added to the worker's queue
    :param config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config, task=None):
        logging.info('Worker (PID: {}) initializing...'.format(str(os.getpid())))
        self._task = task
        self._child = None
        self._queue = Queue()
        self._maintain_queue = Queue()
        self.working_on = None
        self.config = config
        self.db = None
        self.table = None
        self.API_KEY = self.config['key']
        self.tool_source = 'GitHub Pull Request Worker'
        self.tool_version = '0.0.1' # See __init__.py
        self.data_source = 'GitHub API'
        self.results_counter = 0
        self.headers = {'Authorization': f'token {self.API_KEY}'}
        self.history_id = None
        self.finishing_task = False

        url = "https://api.github.com"
        response = requests.get(url=url, headers=self.headers)
        self.rate_limit = int(response.headers['X-RateLimit-Remaining'])


        specs = {
            "id": self.config['id'],
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["pull_requests"]
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'],
            self.config['port'], self.config['database']
        )

        #Database connections
        logging.info("Making database connections...")
        dbschema = 'augur_data'
        self.db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        metadata = MetaData()
        helper_metadata = MetaData()

        metadata.reflect(self.db, only=['contributors', 'pull_requests',
            'pull_request_assignees', 'pull_request_events', 'pull_request_labels',
            'pull_request_message_ref', 'pull_request_meta', 'pull_request_repo',
            'pull_request_reviewers', 'pull_request_teams', 'message'])

        helper_metadata.reflect(self.helper_db, only=['gh_worker_history', 'gh_worker_job'])

        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)

        Base.prepare()
        HelperBase.prepare()

        self.contributors_table = Base.classes.contributors.__table__
        self.pull_requests_table = Base.classes.pull_requests.__table__
        self.pull_request_assignees_table = Base.classes.pull_request_assignees.__table__
        self.pull_request_events_table = Base.classes.pull_request_events.__table__
        self.pull_request_labels_table = Base.classes.pull_request_labels.__table__
        self.pull_request_message_ref_table = Base.classes.pull_request_message_ref.__table__
        self.pull_request_meta_table = Base.classes.pull_request_meta.__table__
        self.pull_request_repo_table = Base.classes.pull_request_repo.__table__
        self.pull_request_reviewers_table = Base.classes.pull_request_reviewers.__table__
        self.pull_request_teams_table = Base.classes.pull_request_teams.__table__
        self.message_table = Base.classes.message.__table__

        self.history_table = HelperBase.classes.gh_worker_history.__table__
        self.job_table = HelperBase.classes.gh_worker_job.__table__

        logging.info("Querying starting ids info...")

        max_pr_id_SQL = s.sql.text("""
            SELECT max(pull_request_id) AS pr_id FROM pull_requests
        """)
        rs = pd.read_sql(max_pr_id_SQL, self.db)
        pr_start = int(rs.iloc[0]['pr_id']) if rs.iloc[0]['pr_id'] is not None else 25150

        max_cntrb_id_SQL = s.sql.text("""
            SELECT max(cntrb_id) AS cntrb_id FROM contributors
        """)
        rs = pd.read_sql(max_cntrb_id_SQL, self.db)
        cntrb_start = int(rs.iloc[0]["cntrb_id"]) if rs.iloc[0]["cntrb_id"] is not None else 25150

        max_msg_id_SQL = s.sql.text("""
            SELECT max(msg_id) AS msg_id FROM message
        """)
        rs = pd.read_sql(max_msg_id_SQL, self.db)
        msg_start = int(rs.iloc[0]["msg_id"]) if rs.iloc[0]["msg_id"] is not None else 25150

        max_pr_labels_id_SQL = s.sql.text("""
            SELECT max(pr_label_id) AS label_id FROM pull_request_labels
        """)
        rs = pd.read_sql(max_pr_labels_id_SQL, self.db)
        label_start = int(rs.iloc[0]['label_id']) if rs.iloc[0]['label_id'] else 25150

        max_pr_event_id_SQL = s.sql.text("""
            SELECT MAX(pr_event_id) AS event_id FROM pull_request_events
        """)
        rs = pd.read_sql(max_pr_event_id_SQL, self.db)
        event_start = int(rs.iloc[0]['event_id']) if rs.iloc[0]['event_id'] else 25150

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.pr_id_inc = (pr_start + 1)
        self.cntrb_id_inc = (cntrb_start + 1)
        self.msg_id_inc = (msg_start + 1)
        self.label_id_inc = (label_start + 1)
        self.event_id_inc = (event_start + 1)

        # self.run()

        requests.post('http://localhost:{}/api/unstable/workers'.format(
            self.config['broker_port']), json=specs) #hello message

    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            'database_connection_string': 'psql://localhost:5433/augur',
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
        git_url = value['given']['git_url']

        repo_url_SQL = s.sql.text("""
            SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
            """.format(git_url))
        rs = pd.read_sql(repo_url_SQL, self.db, params={})

        try:
            repo_id = int(rs.iloc[0]['repo_id'])
            if value['job_type'] == "UPDATE":
                self._queue.put(CollectorTask(message_type='TASK', entry_info={"task": value, "repo_id": repo_id}))
            elif value['job_type'] == "MAINTAIN":
                self._maintain_queue.put(CollectorTask(message_type='TASK', entry_info={"task": value, "repo_id": repo_id}))
            if 'focused_task' in value:
                if value['focused_task'] == 1:
                    self.finishing_task = True

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
        logging.info("Running...")
        if self._child is None:
            self._child = Process(target=self.collect, args=())
            self._child.start()
            requests.post("http://localhost:{}/api/unstable/add_pids".format(
                self.config['broker_port']), json={'pids': [self._child.pid, os.getpid()]})

    def collect(self):
        """ Function to process each entry in the worker's task queue
        Determines what action to take based off the message type
        """
        while True:
            time.sleep(2)
            logging.info('Maintain Queue Empty: ' + str(self._maintain_queue.empty()))
            if not self._queue.empty():
                message = self._queue.get()
                self.working_on = "UPDATE"
            elif not self._maintain_queue.empty():
                message = self._maintain_queue.get()
                logging.info("Popped off message: {}".format(str(message.entry_info)))
                self.working_on = "MAINTAIN"
            else:
                break

            if message.type == 'EXIT':
                break

            if message.type != 'TASK':
                raise ValueError(f'{message.type} is not a recognized task type')

            if message.type == 'TASK':
                # try:
                git_url = message.entry_info['task']['given']['git_url']
                self.query_pr({'git_url': git_url, 'repo_id': message.entry_info['repo_id']})
                # except Exception as e:
                #     logging.error("Worker ran into an error for task: {}\n".format(message.entry_info['task']))
                #     logging.error("Error encountered: " + str(e) + "\n")
                #     traceback.format_exc()
                #     logging.info("Notifying broker and logging task failure in database...\n")

                #     message.entry_info['task']['worker_id'] = self.config['id']

                #     requests.post("http://localhost:{}/api/unstable/task_error".format(
                #         self.config['broker_port']), json=message.entry_info['task'])

                    # Add to history table
                    # task_history = {
                    #     "repo_id": message.entry_info['repo_id'],
                    #     "worker": self.config['id'],
                    #     "job_model": message.entry_info['task']['models'][0],
                    #     "oauth_id": self.config['zombie_id'],
                    #     "timestamp": datetime.datetime.now(),
                    #     "status": "Error",
                    #     "total_results": self.results_counter
                    # }
                    # self.helper_db.execute(self.history_table.update().where(self.history_table.c.history_id==self.history_id).values(task_history))

                    # logging.info("Recorded job error for: " + str(message.entry_info['task']) + "\n")

                    # Update job process table
                    # updated_job = {
                    #     "since_id_str": message.entry_info['repo_id'],
                    #     "last_count": self.results_counter,
                    #     "last_run": datetime.datetime.now(),
                    #     "analysis_state": 0
                    # }
                    # self.helper_db.execute(self.job_table.update().where(self.job_table.c.job_model==message.entry_info['task']['models'][0]).values(updated_job))
                    # logging.info("Updated job process for model: " + message.entry_info['task']['models'][0] + "\n")

                    # Reset results counter for next task
                self.results_counter = 0
                logging.info("passed")

    def query_pr(self, entry_info):
        """Pull Request data collection function. Query GitHub API for PRs.

        :param entry_info: A dictionary consisiting of 'git_url' and 'repo_id'
        :type entry_info: dict
        """
        git_url = entry_info['git_url']
        repo_id = entry_info['repo_id']

        logging.info('Beginning collection of Pull Requests...')
        logging.info(f'Repo ID: {repo_id}, Git URL: {git_url}')

        owner, repo = self.get_owner_repo(git_url)

        url = (f'https://api.github.com/repos/{owner}/{repo}/'
               + f'pulls?state=all&direction=asc&per_page=100')

        pseudo_key_gh = 'id'
        psuedo_key_augur = 'pr_src_id'
        table = 'pull_requests'
        pr_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        prs = []
        try:
            while True:
                r = requests.get(url, headers=self.headers)
                self.update_rate_limit(r)

                j = r.json()

                new_prs = self.check_duplicates(j, pr_table_values, pseudo_key_gh)

                if len(new_prs) == 0:
                    logging.info('No more unknown PRs... Exiting pagination')
                    break
                else:
                    prs += new_prs

                if 'next' not in r.links:
                    break
                else:
                    url = r.links['next']['url']

        except Exception as e:
            logging.error(f'Caught Exception on url {url}')
            logging.error(str(e))
            logging.info('Exiting...')
            sys.exit(1)

        for pr_dict in prs:

            pr = {
                'pull_request_id': self.pr_id_inc,
                'repo_id': repo_id,
                'pr_url': pr_dict['url'],
                'pr_src_id': pr_dict['id'],
                'pr_src_node_id': None,
                'pr_html_url': pr_dict['html_url'],
                'pr_diff_url': pr_dict['diff_url'],
                'pr_patch_url': pr_dict['patch_url'],
                'pr_issue_url': pr_dict['issue_url'],
                'pr_augur_issue_id': None,
                'pr_src_number': pr_dict['number'],
                'pr_src_state': pr_dict['state'],
                'pr_src_locked': pr_dict['locked'],
                'pr_src_title': pr_dict['title'],
                'pr_augur_contributor_id': None,
                'pr_body': pr_dict['body'],
                'pr_created_at': pr_dict['created_at'],
                'pr_updated_at': pr_dict['updated_at'],
                'pr_closed_at': pr_dict['closed_at'],
                'pr_merged_at': pr_dict['merged_at'],
                'pr_merge_commit_sha': pr_dict['merge_commit_sha'],
                'pr_teams': None,
                'pr_milestone': pr_dict['milestone'],
                'pr_commits_url': pr_dict['commits_url'],
                'pr_review_comments_url': pr_dict['review_comments_url'],
                'pr_review_comment_url': pr_dict['review_comment_url'],
                'pr_comments_url': pr_dict['comments_url'],
                'pr_statuses_url': pr_dict['statuses_url'],
                'pr_meta_head_id': None,
                'pr_meta_base_id': None,
                'pr_src_issue_url': pr_dict['issue_url'],
                'pr_src_comments_url': pr_dict['comments_url'], # NOTE: this seems redundant
                'pr_src_review_comments_url': pr_dict['review_comments_url'], # this too
                'pr_src_commits_url': pr_dict['commits_url'], # this one also seems redundant
                'pr_src_statuses_url': pr_dict['statuses_url'],
                'pr_src_author_association': pr_dict['author_association'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': 'GitHub API',
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(self.pull_requests_table.insert().values(pr))
            logging.info(f"Primary Key inserted pull_requests table: {result.inserted_primary_key}")

            self.query_labels(pr_dict['labels'], self.pr_id_inc)
            self.query_pr_events(owner, repo, pr_dict['number'], self.pr_id_inc)

            logging.info(f"Inserted PR data for {owner}/{repo}")
            self.results_counter += 1
            self.pr_id_inc += 1

        self.register_task_completion(entry_info, 'pull_requests')

    def query_labels(self, labels, pr_id):
        logging.info('Querying PR Labels')
        pseudo_key_gh = 'id'
        psuedo_key_augur = 'pr_src_id'
        table = 'pull_request_labels'
        pr_labels_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        new_labels = self.check_duplicates(labels, pr_labels_table_values, pseudo_key_gh)

        if len(new_labels) == 0:
            logging.info('No new labels to add')
            return

        logging.info(f'Found {len(new_labels)} labels')

        for label_dict in new_labels:

            label = {
                'pr_label_id': self.label_id_inc,
                'pull_request_id': pr_id,
                'pr_src_id': label_dict['id'],
                'pr_src_node_id': label_dict['node_id'],
                'pr_src_url': label_dict['url'],
                'pr_src_description': label_dict['name'],
                'pr_src_color': label_dict['color'],
                'pr_src_default_bool': label_dict['default'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(self.pull_request_labels_table.insert().values(label))
            logging.info(f"Primary Key inserted in pull_request_labels table: {result.inserted_primary_key}")
            logging.info(f"Inserted PR Labels data for PR with id {pr_id}")

            self.results_counter += 1
            self.label_id_inc += 1

    def query_pr_events(self, owner, repo, gh_pr_no, pr_id):
        logging.info('Querying PR Events')

        url = (f'https://api.github.com/repos/{owner}/{repo}/issues/'
              + f'{gh_pr_no}/events?per_page=100')

        pseudo_key_gh = 'id'
        psuedo_key_augur = 'pr_event_id'
        table = 'pull_request_events'
        pr_events_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        pr_events = []
        try:
            while True:
                r = requests.get(url, headers=self.headers)
                self.update_rate_limit(r)

                j = r.json()

                new_pr_events = self.check_duplicates(j, pr_events_table_values, pseudo_key_gh)

                if len(new_pr_events) == 0:
                    logging.info('No new PR Events to add... Exiting Pagination')
                    break
                else:
                    pr_events += new_pr_events

                if 'next' not in r.links:
                    break
                else:
                    url = r.links['next']['url']
        except Exception as e:
            logging.error(f'Caught Exception on url {url}')
            logging.error(str(e))
            logging.info(f'Not adding PR events for PR {pr_id}')
            return

        for pr_event_dict in pr_events:

            if pr_event_dict['actor']:
                cntrb_id = self.find_id_from_login(pr_event_dict['actor']['login'])
            else:
                cntrb_id = 1

            pr_event = {
                'pr_event_id': self.event_id_inc,
                'pull_request_id': pr_id,
                'cntrb_id': cntrb_id,
                'action': pr_event_dict['event'],
                'action_commit_hash': None,
                'created_at': pr_event_dict['created_at'],
                'issue_event_src_id': pr_event_dict['id'],
                'node_id': pr_event_dict['node_id'],
                'node_url': pr_event_dict['url'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(self.pull_request_events_table.insert().values(pr_event))
            logging.info(f"Primary Key inserted in pull_request_events table: {result.inserted_primary_key}")
            logging.info(f"Inserted PR Events data for PR with id {pr_id}")

            self.results_counter += 1
            self.event_id_inc += 1

    def query_contributors(self, entry_info):

        """ Data collection function
        Query the GitHub API for contributors
        """
        logging.info("Querying contributors with given entry info: " + str(entry_info) + "\n")

        # Url of repo we are querying for
        url = entry_info['git_url']

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
        pseydo_key_augur = 'cntrb_login'
        table = 'contributors'
        cntrb_table_values = self.get_table_values({pseydo_key_augur: pseudo_key_gh}, [table])

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
            if 'last' in r.links and not multiple_pages and not self.finishing_task:
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
                logging.info("JSON seems ill-formed " + str(r) + "....\n")
                j = json.loads(json.dumps(j))

            if r.status_code == 204:
                j = []

            # Checking contents of requests with what we already have in the db
            new_contributors = self.check_duplicates(j, cntrb_table_values, pseudo_key_gh)
            if len(new_contributors) == 0 and multiple_pages and 'last' in r.links:
                if i - 1 != int(r.links['last']['url'][-6:].split('=')[1]):
                    logging.info("No more pages with unknown contributors, breaking from pagination.\n")
                    break
            elif len(new_contributors) != 0:
                to_add = [obj for obj in new_contributors if obj not in contributors]
                contributors += to_add

            i = i + 1 if self.finishing_task else i - 1

            if i == 1 and multiple_pages or i < 1 or len(j) == 0:
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
                result = self.db.execute(self.contributors_table.insert().values(cntrb))
                logging.info("Primary key inserted into the contributors table: " + str(result.inserted_primary_key))
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

    def get_owner_repo(self, git_url):
        split = git_url.split('/')

        owner = split[-2]
        repo = split[-1]

        if '.git' in repo:
            repo = repo[:-4]

        return owner, repo

    def get_table_values(self, cols, tables):
        table_str = tables[0]
        del tables[0]
        for table in tables:
            table_str += ", " + table
        for col in cols.keys():
            colSQL = s.sql.text("""
                SELECT {} FROM {}
                """.format(col, table_str))
            values = pd.read_sql(colSQL, self.db, params={})
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
            logging.info(f"Contributor '{login}' needs to be added...")
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
        logging.info("Updated rate limit, you have: " + str(self.rate_limit) + " requests remaining.\n")
        if self.rate_limit <= 0:
            reset_time = response.headers['X-RateLimit-Reset']
            time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
            logging.info("Rate limit exceeded, waiting " + str(time_diff.total_seconds()) + " seconds.\n")
            time.sleep(time_diff.total_seconds())
            self.rate_limit = int(response.headers['X-RateLimit-Limit'])

    def register_task_completion(self, entry_info, model):
        # Task to send back to broker
        task_completed = {
            'worker_id': self.config['id'],
            'job_type': self.working_on,
            'repo_id': entry_info['repo_id'],
            'git_url': entry_info['git_url']
        }
        # # Add to history table
        # task_history = {
        #     "repo_id": entry_info['repo_id'],
        #     "worker": self.config['id'],
        #     "job_model": model,
        #     "oauth_id": self.config['zombie_id'],
        #     "timestamp": datetime.datetime.now(),
        #     "status": "Success",
        #     "total_results": self.results_counter
        # }
        # self.helper_db.execute(self.history_table.update().where(self.history_table.c.history_id==self.history_id).values(task_history))

        # logging.info("Recorded job completion for: " + str(task_completed) + "\n")

        # # Update job process table
        # updated_job = {
        #     "since_id_str": entry_info['repo_id'],
        #     "last_count": self.results_counter,
        #     "last_run": datetime.datetime.now(),
        #     "analysis_state": 0
        # }
        # self.helper_db.execute(self.job_table.update().where(self.job_table.c.job_model==model).values(updated_job))
        # logging.info("Update job process for model: " + model + "\n")

        # Notify broker of completion
        logging.info("Telling broker we completed task: " + str(task_completed) + "\n" +
            "This task inserted: " + str(self.results_counter) + " tuples.\n\n")

        requests.post('http://localhost:{}/api/unstable/completed_task'.format(
            self.config['broker_port']), json=task_completed)

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
            result = self.helper_db.execute(self.history_table.update().where(self.history_table.c.history_id==self.history_id).values(task_history))
        else:
            result = self.helper_db.execute(self.history_table.insert().values(task_history))
            logging.info("Record incomplete history tuple: " + str(result.inserted_primary_key))
            self.history_id = int(result.inserted_primary_key[0])

    def check_duplicates(self, new_data, table_values, key):
        need_insertion = []
        for obj in new_data:
            if type(obj) == dict:
                if table_values.isin([obj[key]]).any().any():
                    logging.info("Tuple with github's {} key value already exists in our db: {}\n".format(key, str(obj[key])))
                else:
                    need_insertion.append(obj)
        logging.info("Page recieved has {} tuples, while filtering duplicates this was reduced to {} tuples.\n".format(str(len(new_data)), str(len(need_insertion))))
        return need_insertion
