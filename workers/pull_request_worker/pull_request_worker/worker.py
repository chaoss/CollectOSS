import ast, json, logging, os, sys, time, traceback, requests
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from workers.standard_methods import register_task_completion, register_task_failure, connect_to_broker, update_gh_rate_limit, record_model_process

class GHPullRequestWorker:
    """
    Worker that collects Pull Request related data from the Github API and stores it in our database.

    :param task: most recent task the broker added to the worker's queue
    :param config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config, task=None):
        self._task = task
        self._child = None
        self._queue = Queue()
        self._maintain_queue = Queue()
        self.working_on = None
        self.config = config
        LOG_FORMAT = '%(levelname)s:[%(name)s]: %(message)s'
        logging.basicConfig(filename='worker_{}.log'.format(self.config['id'].split('.')[len(self.config['id'].split('.')) - 1]), filemode='w', level=logging.INFO, format=LOG_FORMAT)
        logging.info('Worker (PID: {}) initializing...'.format(str(os.getpid())))
        # logger = logging.getLogger('PullRequestWorker')
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

        self.specs = {
            "id": self.config['id'],
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["github_url"]],
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

        helper_metadata.reflect(self.helper_db, only=['worker_history', 'worker_job', 'worker_oauth'])

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

        self.history_table = HelperBase.classes.worker_history.__table__
        self.job_table = HelperBase.classes.worker_job.__table__

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

        max_pr_msg_ref_id_SQL = s.sql.text("""
            SELECT MAX(pr_msg_ref_id) AS pr_msg_ref_id FROM pull_request_message_ref
        """)
        rs = pd.read_sql(max_pr_msg_ref_id_SQL, self.db)
        pr_msg_ref_start = int(rs.iloc[0]['pr_msg_ref_id']) if rs.iloc[0]['pr_msg_ref_id'] else 25150

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

        max_reviewer_id_SQL = s.sql.text("""
            SELECT MAX(pr_reviewer_map_id) AS reviewer_id FROM pull_request_reviewers
        """)
        rs = pd.read_sql(max_reviewer_id_SQL, self.db)
        reviewer_start = rs.iloc[0]['reviewer_id'] if rs.iloc[0]['reviewer_id'] else 25150

        max_assignee_id_SQL = s.sql.text("""
            SELECT MAX(pr_assignee_map_id) AS assignee_id FROM pull_request_assignees
        """)
        rs = pd.read_sql(max_assignee_id_SQL, self.db)
        assignee_start = rs.iloc[0]['assignee_id'] if rs.iloc[0]['assignee_id'] else 25150

        max_pr_meta_id_SQL = s.sql.text("""
            SELECT MAX(pr_repo_meta_id) AS pr_meta_id FROM pull_request_meta
        """)
        rs = pd.read_sql(max_pr_meta_id_SQL, self.db)
        pr_meta_id_start = rs.iloc[0]['pr_meta_id'] if rs.iloc[0]['pr_meta_id'] else 25150

        maxHistorySQL = s.sql.text("""
            SELECT max(history_id) AS history_id
            FROM worker_history
        """)
        rs = pd.read_sql(maxHistorySQL, self.helper_db, params={})
        self.history_id = int(rs.iloc[0]["history_id"]) if rs.iloc[0]["history_id"] is not None else 25150        

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = self.history_id if self.finishing_task else self.history_id + 1
        self.pr_id_inc = (pr_start + 1)
        self.cntrb_id_inc = (cntrb_start + 1)
        self.msg_id_inc = (msg_start + 1)
        self.pr_msg_ref_id_inc = (pr_msg_ref_start + 1)
        self.label_id_inc = (label_start + 1)
        self.event_id_inc = (event_start + 1)
        self.reviewer_id_inc = (reviewer_start + 1)
        self.assignee_id_inc = (assignee_start + 1)
        self.pr_meta_id_inc = (pr_meta_id_start + 1)

        # Organize different keys available
        self.oauths = []
        self.headers = None

        # Endpoint to hit solely to retrieve rate limit information from headers of the response
        url = "https://api.github.com/users/gabe-heim"

        # Make a list of api key in the config combined w keys stored in the database
        oauthSQL = s.sql.text("""
            SELECT * FROM worker_oauth WHERE access_token <> '{}'
        """.format(config['key']))
        for oauth in [{'oauth_id': 0, 'access_token': config['key']}] + json.loads(pd.read_sql(oauthSQL, self.helper_db, params={}).to_json(orient="records")):
            # self.headers = {'Authorization': 'token %s' % oauth['access_token']}
            self.headers = {'Authorization': 'token {}'.format(oauth['access_token']),
                        'Accept': 'application/vnd.github.vixen-preview+json'}
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
        github_url = value['given']['github_url']

        repo_url_SQL = s.sql.text("""
            SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
            """.format(github_url))
        rs = pd.read_sql(repo_url_SQL, self.db, params={})

        try:
            repo_id = int(rs.iloc[0]['repo_id'])
            if value['job_type'] == "UPDATE" or value['job_type'] == "MAINTAIN":
                self._queue.put(value)
            if 'focused_task' in value:
                if value['focused_task'] == 1:
                    self.finishing_task = True

        except Exception as e:
            logging.error(f"error: {e}, or that repo is not in our database: {value}")

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
        logging.info("Running...")
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

            # Query all repos with repo url of given task
            repoUrlSQL = s.sql.text("""
                SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
                """.format(message['given']['github_url']))
            repo_id = int(pd.read_sql(repoUrlSQL, self.db, params={}).iloc[0]['repo_id'])

            try:
                if message['models'][0] == 'pull_requests':
                    self.query_pr(message, repo_id)
            except Exception as e:
                register_task_failure(self, logging, message, repo_id, e)
                pass

    def query_pr(self, entry_info, repo_id):
        """Pull Request data collection function. Query GitHub API for PhubRs.

        :param entry_info: A dictionary consisiting of 'git_url' and 'repo_id'
        :type entry_info: dict
        """
        github_url = entry_info['given']['github_url']

        logging.info('Beginning collection of Pull Requests...')
        logging.info(f'Repo ID: {repo_id}, Git URL: {github_url}')
        record_model_process(self, logging, repo_id, 'pull_requests')

        owner, repo = self.get_owner_repo(github_url)

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
                update_gh_rate_limit(self, logging, r)

                j = r.json()

                self.mark_new_records(j, pr_table_values, pseudo_key_gh)

                if len(j) == 0:
                    logging.info('No more unknown PRs... Exiting pagination')
                    #break
                else:
                    prs += j

                if 'next' not in r.links:
                    logging.info('No next page ... ')
                    break
                else:
                    url = r.links['next']['url']

        except Exception as e:
            logging.exception('Encountered an error while paginating through PRs')
            register_task_failure(self, logging, entry_info, repo_id, e)
            return

        for pr_dict in prs:

            if pr_dict['to_insert']:
                logging.info(f'PR {pr_dict["id"]} needs to be inserted')

                pr = {
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
                    'pr_milestone': pr_dict['milestone']['title'] if pr_dict['milestone'] else None,
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
                logging.info(f"Added Pull Request: {result.inserted_primary_key}")
                self.pr_id_inc = int(result.inserted_primary_key[0])

            else:
                logging.info("PR does not need to be inserted. Fetching its id from DB")
                pr_id_sql = s.sql.text("""
                    SELECT pull_request_id FROM pull_requests
                    WHERE pr_src_id={}
                """.format(pr_dict['id']))

                self.pr_id_inc = int(pd.read_sql(pr_id_sql, self.db).iloc[0]['pull_request_id'])

            self.query_labels(pr_dict['labels'], self.pr_id_inc)
            self.query_pr_events(owner, repo, pr_dict['number'], self.pr_id_inc)
            self.query_pr_comments(owner, repo, pr_dict['number'], self.pr_id_inc)
            self.query_reviewers(pr_dict['requested_reviewers'], self.pr_id_inc)
            self.query_pr_meta(pr_dict['head'], pr_dict['base'], self.pr_id_inc)

            logging.info(f"Inserted PR data for {owner}/{repo}")
            self.results_counter += 1

        register_task_completion(self, logging, entry_info, repo_id, 'pull_requests')

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
            logging.info(f"Added PR Label: {result.inserted_primary_key}")
            logging.info(f"Inserted PR Labels data for PR with id {pr_id}")

            self.results_counter += 1
            self.label_id_inc = int(result.inserted_primary_key[0])

    def query_pr_events(self, owner, repo, gh_pr_no, pr_id):
        logging.info('Querying PR Events')

        url = (f'https://api.github.com/repos/{owner}/{repo}/issues/'
              + f'{gh_pr_no}/events?per_page=100')

        pseudo_key_gh = 'id'
        psuedo_key_augur = 'issue_event_src_id'
        table = 'pull_request_events'
        pr_events_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        pr_events = []
        try:
            while True:
                r = requests.get(url, headers=self.headers)
                update_gh_rate_limit(self, logging, r)

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
        except Exception:
            logging.exception('Encountered an error while paginating through PR Events')
            return

        for pr_event_dict in pr_events:

            if pr_event_dict['actor']:
                cntrb_id = self.find_id_from_login(pr_event_dict['actor']['login'])
            else:
                cntrb_id = 1

            pr_event = {
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
            logging.info(f"Added PR Event: {result.inserted_primary_key}")

            self.results_counter += 1
            self.event_id_inc = int(result.inserted_primary_key[0])

        logging.info(f"Inserted PR Events data for PR with id {pr_id}")

    def query_reviewers(self, reviewers, pr_id):
        logging.info('Querying Reviewers')

        if reviewers is None or len(reviewers) == 0:
            logging.info('No reviewers to add')
            return

        pseudo_key_gh = 'id'
        psuedo_key_augur = 'pr_reviewer_map_id'
        table = 'pull_request_reviewers'
        reviewers_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        new_reviewers = self.check_duplicates(reviewers, reviewers_table_values, pseudo_key_gh)

        if len(new_reviewers) == 0:
            logging.info('No new reviewers to add')
            return

        logging.info(f'Found {len(new_reviewers)} reviewers')

        for reviewers_dict in reviewers:

            if 'login' in reviewers_dict:
                cntrb_id = self.find_id_from_login(reviewers_dict['login'])
            else:
                cntrb_id = 1

            reviewer = {
                'pull_request_id': pr_id,
                'cntrb_id': cntrb_id,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(self.pull_request_reviewers_table.insert().values(reviewer))
            logging.info(f"Added PR Reviewer {result.inserted_primary_key}")

            self.reviewer_id_inc = int(result.inserted_primary_key[0])
            self.results_counter += 1

        logging.info(f"Finished inserting PR Reviewer data for PR with id {pr_id}")

    def query_assignee(self, assignees, pr_id):
        logging.info('Querying Assignees')

        if assignees is None or len(assignees) == 0:
            logging.info('No assignees to add')
            return

        pseudo_key_gh = 'id'
        psuedo_key_augur = 'pr_assignee_map_id'
        table = 'pull_request_assignees'
        assignee_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        new_assignees = self.check_duplicates(assignees, assignee_table_values, pseudo_key_gh)

        if len(new_assignees) == 0:
            logging.info('No new assignees to add')
            return

        logging.info(f'Found {len(new_assignees)} assignees')

        for assignee_dict in assignees:

            if 'login' in assignee_dict:
                cntrb_id = self.find_id_from_login(assignee_dict['login'])
            else:
                cntrb_id = 1

            assignee = {
                'pull_request_id': pr_id,
                'contrib_id': cntrb_id,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(self.pull_request_assignees_table.insert().values(assignee))
            logging.info(f'Added PR Assignee {result.inserted_primary_key}')

            self.assignee_id_inc = int(result.inserted_primary_key[0])
            self.results_counter += 1

        logging.info(f'Finished inserting PR Assignee data for PR with id {pr_id}')

    def query_pr_meta(self, head, base,  pr_id):
        logging.info('Querying PR Meta')

        pseudo_key_gh = 'sha'
        psuedo_key_augur = 'pr_sha'
        table = 'pull_request_meta'
        meta_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        new_head = [head]
        new_base = [base]
        self.mark_new_records(new_head, meta_table_values, pseudo_key_gh)
        self.mark_new_records(new_base, meta_table_values, pseudo_key_gh)

        if new_head[0]['to_insert']:
            if new_head[0]['user'] and 'login' in new_head[0]['user']:
                cntrb_id = self.find_id_from_login(new_head[0]['user']['login'])
            else:
                cntrb_id = 1

            pr_meta = {
                'pull_request_id': pr_id,
                'pr_head_or_base': 'head',
                'pr_src_meta_label': new_head[0]['label'],
                'pr_src_meta_ref': new_head[0]['ref'],
                'pr_sha': new_head[0]['sha'],
                'cntrb_id': cntrb_id,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(self.pull_request_meta_table.insert().values(pr_meta))
            logging.info(f'Added PR Head {result.inserted_primary_key}')

            self.pr_meta_id_inc = int(result.inserted_primary_key[0])
            self.results_counter += 1
        else:
            pr_meta_id_sql = """
                SELECT pr_repo_meta_id FROM pull_request_meta
                WHERE pr_sha='{}'
            """.format(new_head[0]['sha'])

            self.pr_meta_id_inc = int(int(pd.read_sql(pr_meta_id_sql, self.db).iloc[0]['pr_repo_meta_id']))

        if new_head[0]['repo']:
            self.query_pr_repo(new_head[0]['repo'], 'head', self.pr_meta_id_inc)
        else:
            logging.info('No new PR Head data to add')

        if new_base[0]['to_insert']:
            if new_base[0]['user'] and 'login' in new_base[0]['user']:
                cntrb_id = self.find_id_from_login(new_base[0]['user']['login'])
            else:
                cntrb_id = 1

            pr_meta = {
                'pull_request_id': pr_id,
                'pr_head_or_base': 'base',
                'pr_src_meta_label': new_base[0]['label'],
                'pr_src_meta_ref': new_base[0]['ref'],
                'pr_sha': new_base[0]['sha'],
                'cntrb_id': cntrb_id,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(self.pull_request_meta_table.insert().values(pr_meta))
            logging.info(f'Added PR Base {result.inserted_primary_key}')

            self.pr_meta_id_inc = int(result.inserted_primary_key[0])
            self.results_counter += 1
        else:
            pr_meta_id_sql = """
                SELECT pr_repo_meta_id FROM pull_request_meta
                WHERE pr_sha='{}'
            """.format(new_base[0]['sha'])

            self.pr_meta_id_inc = int(int(pd.read_sql(pr_meta_id_sql, self.db).iloc[0]['pr_repo_meta_id']))

        if new_base[0]['repo']:
            self.query_pr_repo(new_base[0]['repo'], 'base', self.pr_meta_id_inc)
        else:
            logging.info('No new PR Base data to add')

        logging.info(f'Finished inserting PR Head & Base data for PR with id {pr_id}')

    def query_pr_comments(self, owner, repo, gh_pr_no, pr_id):
        logging.info('Querying PR Comments')

        url = (f'https://api.github.com/repos/{owner}/{repo}/issues/'
              + f'{gh_pr_no}/comments?per_page=100')

        pseudo_key_gh = 'id'
        psuedo_key_augur = 'pr_message_ref_src_comment_id'
        table = 'pull_request_message_ref'
        pr_message_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        pr_messages = []
        try:
            while True:
                r = requests.get(url, headers=self.headers)
                update_gh_rate_limit(self, logging, r)

                j = r.json()

                new_pr_messages = self.check_duplicates(j, pr_message_table_values, pseudo_key_gh)

                if len(new_pr_messages) == 0:
                    logging.info('No new PR Comments to add... Exiting Pagination')
                    break
                else:
                    pr_messages += new_pr_messages

                if 'next' not in r.links:
                    break
                else:
                    url = r.links['next']['url']
        except Exception as e:
            logging.error(f'Caught Exception on url {url}')
            logging.error(str(e))

        for pr_msg_dict in pr_messages:

            if pr_msg_dict['user'] and 'login' in pr_msg_dict['user']:
                cntrb_id = self.find_id_from_login(pr_msg_dict['user']['login'])
            else:
                cntrb_id = 1

            msg = {
                'rgls_id': None,
                'msg_text': pr_msg_dict['body'],
                'msg_timestamp': pr_msg_dict['created_at'],
                'msg_sender_email': None,
                'msg_header': None,
                'pltfrm_id': '25150',
                'cntrb_id': cntrb_id,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(self.message_table.insert().values(msg))
            logging.info(f'Added PR Comment {result.inserted_primary_key}')
            self.msg_id_inc = int(result.inserted_primary_key[0])

            pr_msg_ref = {
                'pull_request_id': pr_id,
                'msg_id': self.msg_id_inc,
                'pr_message_ref_src_comment_id': pr_msg_dict['id'],
                'pr_message_ref_src_node_id': pr_msg_dict['node_id'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(
                self.pull_request_message_ref_table.insert().values(pr_msg_ref)
            )
            logging.info(f'Added PR Message Ref {result.inserted_primary_key}')
            self.pr_msg_ref_id_inc = int(result.inserted_primary_key[0])

            self.results_counter += 1

        logging.info(f'Finished adding PR Message data for PR with id {pr_id}')

    def query_pr_repo(self, pr_repo, pr_repo_type, pr_meta_id):
        logging.info(f'Querying PR {pr_repo_type} repo')

        pseudo_key_gh = 'id'
        psuedo_key_augur = 'pr_src_repo_id'
        table = 'pull_request_repo'
        pr_repo_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        new_pr_repo = self.check_duplicates([pr_repo], pr_repo_table_values, pseudo_key_gh)

        if new_pr_repo:
            if new_pr_repo[0]['owner'] and 'login' in new_pr_repo[0]['owner']:
                cntrb_id = self.find_id_from_login(new_pr_repo[0]['owner']['login'])
            else:
                cntrb_id = 1

            pr_repo = {
                'pr_repo_meta_id': pr_meta_id,
                'pr_repo_head_or_base': pr_repo_type,
                'pr_src_repo_id': new_pr_repo[0]['id'],
                # 'pr_src_node_id': new_pr_repo[0]['node_id'],
                'pr_src_node_id': None,
                'pr_repo_name': new_pr_repo[0]['name'],
                'pr_repo_full_name': new_pr_repo[0]['full_name'],
                'pr_repo_private_bool': new_pr_repo[0]['private'],
                'pr_cntrb_id': cntrb_id,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            result = self.db.execute(
                self.pull_request_repo_table.insert().values(pr_repo)
            )
            logging.info(f'Added PR {pr_repo_type} repo {result.inserted_primary_key}')

            self.results_counter += 1

        logging.info(
            f'Finished adding PR {pr_repo_type} Repo data for PR with id {self.pr_id_inc}'
        )


    def query_contributors(self, entry_info):

        """ Data collection function
        Query the GitHub API for contributors
        """
        logging.info("Querying contributors with given entry info: " + str(entry_info))

        # Url of repo we are querying for
        url = entry_info['github_url']

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
            logging.info("Hitting endpoint: " + url.format(i) + " ...")
            r = requests.get(url=url.format(i), headers=self.headers)
            update_gh_rate_limit(self, logging, r)

            # If it lists the last page then there is more than 1
            if 'last' in r.links and not multiple_pages and not self.finishing_task:
                param = r.links['last']['url'][-6:]
                i = int(param.split('=')[1]) + 1
                logging.info("Multiple pages of request, last page is " + str(i - 1))
                multiple_pages = True
            elif not multiple_pages and not self.finishing_task:
                logging.info("Only 1 page of request\n")
            elif self.finishing_task:
                logging.info("Finishing a previous task, paginating forwards ... excess rate limit requests will be made")

            # The contributors endpoints has issues with getting json from request
            try:
                j = r.json()
            except Exception as e:
                logging.info("Caught exception: " + str(e))
                logging.info("Some kind of issue CHECKTHIS  " + url)
                j = json.loads(json.dumps(j))
            else:
                logging.info("JSON seems ill-formed " + str(r))
                j = json.loads(json.dumps(j))

            if r.status_code == 204:
                j = []

            # Checking contents of requests with what we already have in the db
            new_contributors = self.check_duplicates(j, cntrb_table_values, pseudo_key_gh)
            if len(new_contributors) == 0 and multiple_pages and 'last' in r.links:
                if i - 1 != int(r.links['last']['url'][-6:].split('=')[1]):
                    logging.info("No more pages with unknown contributors, breaking from pagination.")
                    break
            elif len(new_contributors) != 0:
                to_add = [obj for obj in new_contributors if obj not in contributors]
                contributors += to_add

            i = i + 1 if self.finishing_task else i - 1

            if i == 1 and multiple_pages or i < 1 or len(j) == 0:
                logging.info("No more pages to check, breaking from pagination.")
                break

        try:
            logging.info("Count of contributors needing insertion: " + str(len(contributors)))

            for repo_contributor in contributors:

                # Need to hit this single contributor endpoint to get extra data including...
                #   created at
                #   i think that's it
                cntrb_url = ("https://api.github.com/users/" + repo_contributor['login'])
                logging.info("Hitting endpoint: " + cntrb_url)
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

                logging.info("Inserted contributor: " + contributor['login'])

                # Increment our global track of the cntrb id for the possibility of it being used as a FK
                self.cntrb_id_inc = int(result.inserted_primary_key[0])

        except Exception as e:
            logging.info("Caught exception: " + str(e))
            logging.info("Contributor not defined. Please contact the manufacturers of Soylent Green " + url + " ...\n")
            logging.info("Cascading Contributor Anomalie from missing repo contributor data: " + url + " ...\n")
        else:
            if len(contributors) > 2:
                logging.info("Well, that contributor list of len {} with last 3 tuples as: {} just don't except because we hit the else-block yo\n".format(str(len(contributors)), str(contributors[-3:])))

    def get_owner_repo(self, github_url):
        split = github_url.split('/')

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
            logging.info("Hitting endpoint: {} ...".format(cntrb_url))
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

            logging.info("Inserted contributor: " + contributor['login'])

            return self.find_id_from_login(login)

    def check_duplicates(self, new_data, table_values, key):
        need_insertion = []
        for obj in new_data:
            if type(obj) == dict:
                # if table_values.isin([obj[key]]).any().any():
                    # logging.info("Tuple with github's {} key value already exists in our db: {}\n".format(key, str(obj[key])))
                if not table_values.isin([obj[key]]).any().any():
                    need_insertion.append(obj)
        logging.info("[Filtering] Page recieved has {} tuples, while filtering duplicates this was reduced to {} tuples.".format(str(len(new_data)), str(len(need_insertion))))
        return need_insertion

    def mark_new_records(self, new_data, table_values, key):
        """Adds a `to_insert` key to all the records in new_data.
        Sets `to_insert` to `True` for new records and `False` for old records.

        :param new_data: A dict of records
        :type new_data: dict
        :param table_values: A dataframe of records from the DB
        :type table_values: pandas.Dataframe
        :param key: Key that determines the uniqueness of records in both `new_data` & `table_value`
        :type key: str
        """
        for record in new_data:
            if type(record) != dict:
                continue
            if not table_values.isin([record[key]]).any().any():
                record['to_insert'] = True
            else:
                record['to_insert'] = False
