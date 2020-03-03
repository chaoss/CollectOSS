import ast, json, logging, os, sys, time, traceback, requests
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from workers.standard_methods import init_oauths, get_max_id, register_task_completion, register_task_failure, connect_to_broker, update_gh_rate_limit, record_model_process, paginate

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
        logging.info('Worker (PID: {}) initializing...\n'.format(str(os.getpid())))
        self.db = None
        self.table = None
        self.API_KEY = self.config['key']
        self.tool_source = 'GitHub Pull Request Worker'
        self.tool_version = '0.0.1' # See __init__.py
        self.data_source = 'GitHub API'
        self.results_counter = 0
        self.headers = {'Authorization': f'token {self.API_KEY}'}
        self.history_id = None
        self.finishing_task = True

        self.specs = {
            "id": self.config['id'],
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["github_url"]],
                    "models":["pull_requests", 'pull_request_commits']
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'],
            self.config['port'], self.config['database']
        )

        #Database connections
        logging.info("Making database connections...\n")
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
            'pull_request_reviewers', 'pull_request_teams', 'message', 'pull_request_commits'])

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
        self.pull_request_commits_table = Base.classes.pull_request_commits.__table__

        self.history_table = HelperBase.classes.worker_history.__table__
        self.job_table = HelperBase.classes.worker_job.__table__

        logging.info("Querying starting ids info...\n")

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = get_max_id(self, 'worker_history', 'history_id', operations_table=True) + 1
        self.pr_id_inc = get_max_id(self, 'pull_requests', 'pull_request_id')
        self.cntrb_id_inc = get_max_id(self, 'contributors', 'cntrb_id')
        self.msg_id_inc = get_max_id(self, 'message', 'msg_id')
        self.pr_msg_ref_id_inc = get_max_id(self, 'pull_request_message_ref', 'pr_msg_ref_id')
        self.label_id_inc = get_max_id(self, 'pull_request_labels', 'pr_label_id')
        self.event_id_inc = get_max_id(self, 'pull_request_events', 'pr_event_id')
        self.reviewer_id_inc = get_max_id(self, 'pull_request_reviewers', 'pr_reviewer_map_id')
        self.assignee_id_inc = get_max_id(self, 'pull_request_assignees', 'pr_assignee_map_id')
        self.pr_meta_id_inc = get_max_id(self, 'pull_request_meta', 'pr_repo_meta_id')

        # Organize different api keys/oauths available
        init_oauths(self)

        # Send broker hello message
        connect_to_broker(self)

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
            logging.error(f"error: {e}, or that repo is not in our database: {value}\n")

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
        logging.info("Running...\n")
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
                    self.pull_requests_model(message, repo_id)
                if message['models'][0] == 'pull_request_commits':
                    self.pull_request_commits_model(message, repo_id)
            except Exception as e:
                register_task_failure(self, message, repo_id, e)
                pass

    def pull_request_commits_model(self, task_info, repo_id):
        """ Queries the commits related to each pull request already inserted in the db """

        # query existing PRs and the respective url we will append the commits url to
        pr_url_sql = s.sql.text("""
            SELECT DISTINCT pr_url, pull_requests.pull_request_id
            FROM pull_requests, pull_request_meta
            WHERE pr_src_meta_label LIKE '%master'
            --AND pull_request_meta.pr_head_or_base = 'base'
            AND pull_requests.pull_request_id = pull_request_meta.pull_request_id
            AND repo_id = {}
        """.format(repo_id))
        urls = pd.read_sql(pr_url_sql, self.db, params={})

        for pull_request in urls.itertuples(): # for each url of PRs we have inserted
            commits_url = pull_request.pr_url + '/commits?page={}'
            table = 'pull_request_commits'
            table_pkey = 'pr_cmt_id'
            duplicate_col_map = {'pr_cmt_sha': 'sha'}
            update_col_map = {}

            # Use helper paginate function to iterate the commits url and check for dupes
            pr_commits = paginate(self, commits_url, duplicate_col_map, update_col_map, table, table_pkey, 
                where_clause="where pull_request_id = {}".format(pull_request.pull_request_id))

            for pr_commit in pr_commits: # post-pagination, iterate results
                if pr_commit['flag'] == 'need_insertion': # if non-dupe
                    pr_commit_row = {
                        'pull_request_id': pull_request.pull_request_id,
                        'pr_cmt_sha': pr_commit['sha'],
                        'pr_cmt_node_id': pr_commit['node_id'],
                        'pr_cmt_message': pr_commit['commit']['message'],
                        # 'pr_cmt_comments_url': pr_commit['comments_url'],
                        'tool_source': self.tool_source,
                        'tool_version': self.tool_version,
                        'data_source': 'GitHub API',
                    }
                    result = self.db.execute(self.pull_request_commits_table.insert().values(pr_commit_row))
                    logging.info(f"Inserted Pull Request Commit: {result.inserted_primary_key}\n")

        # helper method to sync completion to broker and db
        register_task_completion(self, task_info, repo_id, 'pull_request_commits')

    def pull_requests_model(self, entry_info, repo_id):
        """Pull Request data collection function. Query GitHub API for PhubRs.

        :param entry_info: A dictionary consisiting of 'git_url' and 'repo_id'
        :type entry_info: dict
        """
        github_url = entry_info['given']['github_url']

        logging.info('Beginning collection of Pull Requests...\n')
        logging.info(f'Repo ID: {repo_id}, Git URL: {github_url}\n')
        record_model_process(self, repo_id, 'pull_requests')

        owner, repo = self.get_owner_repo(github_url)

        url = (f'https://api.github.com/repos/{owner}/{repo}/'
               + 'pulls?state=all&direction=asc&per_page=100&page={}')

        # Get pull requests that we already have stored
        #   Set pseudo key (something other than PK) to 
        #   check dupicates with
        table = 'pull_requests'
        table_pkey = 'pull_request_id'
        update_col_map = {'pr_src_state': 'state'} #'updated_at': 'updated_at', 'closed_at': 'closed_at', 'comment_count': 'comments', 
        duplicate_col_map = {'pr_src_id': 'id'}

        #list to hold pull requests needing insertion
        prs = paginate(self, url, duplicate_col_map, update_col_map, table, table_pkey, 
            'WHERE repo_id = {}'.format(repo_id))

        # Discover and remove duplicates before we start inserting
        logging.info("Count of pull requests needing update or insertion: " + str(len(prs)) + "\n")

        for pr_dict in prs:

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

            if pr_dict['flag'] == 'need_insertion':
                logging.info(f'PR {pr_dict["id"]} needs to be inserted\n')

                result = self.db.execute(self.pull_requests_table.insert().values(pr))
                logging.info(f"Added Pull Request: {result.inserted_primary_key}")
                self.pr_id_inc = int(result.inserted_primary_key[0])

            elif pr_dict['flag'] == 'need_update':
                result = self.db.execute(self.pull_requests_table.update().where(
                    self.pull_requests_table.c.pr_src_id==pr_dict['id']).values(pr))
                logging.info("Updated tuple in the pull_requests table with existing pr_src_id: {}".format(
                    pr_dict['id']))
                self.pr_id_inc = pr_dict['pkey']

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

        register_task_completion(self, entry_info, repo_id, 'pull_requests')

    def query_labels(self, labels, pr_id):
        logging.info('Querying PR Labels\n')
        pseudo_key_gh = 'id'
        psuedo_key_augur = 'pr_src_id'
        table = 'pull_request_labels'
        pr_labels_table_values = self.get_table_values({psuedo_key_augur: pseudo_key_gh}, [table])

        new_labels = self.check_duplicates(labels, pr_labels_table_values, pseudo_key_gh)

        if len(new_labels) == 0:
            logging.info('No new labels to add\n')
            return

        logging.info(f'Found {len(new_labels)} labels\n')

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
            logging.info(f"Added PR Label: {result.inserted_primary_key}\n")
            logging.info(f"Inserted PR Labels data for PR with id {pr_id}\n")

            self.results_counter += 1
            self.label_id_inc = int(result.inserted_primary_key[0])

    def query_pr_events(self, owner, repo, gh_pr_no, pr_id):
        logging.info('Querying PR Events\n')

        url = (f'https://api.github.com/repos/{owner}/{repo}/issues/{gh_pr_no}' +
            '/events?per_page=100&page={}')

        # Get pull request events that we already have stored
        #   Set our duplicate and update column map keys (something other than PK) to 
        #   check dupicates/needed column updates with
        table = 'pull_request_events'
        table_pkey = 'pr_event_id'
        update_col_map = {}
        duplicate_col_map = {'issue_event_src_id': 'id'}

        #list to hold contributors needing insertion or update
        pr_events = paginate(self, url, duplicate_col_map, update_col_map, table, table_pkey)
        
        logging.info("Count of pull request events needing insertion: " + str(len(pr_events)) + "\n")

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
            logging.info(f"Added PR Event: {result.inserted_primary_key}\n")

            self.results_counter += 1
            self.event_id_inc = int(result.inserted_primary_key[0])

        logging.info(f"Inserted PR Events data for PR with id {pr_id}\n")

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

        url = (f'https://api.github.com/repos/{owner}/{repo}/issues/{gh_pr_no}' +
            '/comments?per_page=100&page={}')

        # Get pull request comments that we already have stored
        #   Set our duplicate and update column map keys (something other than PK) to 
        #   check dupicates/needed column updates with
        table = 'pull_request_message_ref'
        table_pkey = 'pr_msg_ref_id'
        update_col_map = {}
        duplicate_col_map = {'pr_message_ref_src_comment_id': 'id'}

        #list to hold contributors needing insertion or update
        pr_messages = paginate(self, url, duplicate_col_map, update_col_map, table, table_pkey)
        
        logging.info("Count of pull request comments needing insertion: " + str(len(pr_messages)) + "\n")

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
