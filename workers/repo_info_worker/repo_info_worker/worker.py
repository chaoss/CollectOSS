import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from workers.standard_methods import register_task_completion, register_task_failure, connect_to_broker, update_gh_rate_limit, record_model_process

class GHRepoInfoWorker:
    def __init__(self, config, task=None):
        self._task = task
        self._child = None
        self._queue = Queue()
        self.working_on = None
        self.config = config
        LOG_FORMAT = '%(levelname)s:[%(name)s]: %(message)s'
        logging.basicConfig(filename='worker_{}.log'.format(self.config['id'].split('.')[len(self.config['id'].split('.')) - 1]), filemode='w', level=logging.INFO, format=LOG_FORMAT)
        logging.info('Worker (PID: {}) initializing...'.format(str(os.getpid())))
        # logger = logging.getLogger('RepoInfoWorker')
        self.db = None
        self.table = None
        self.API_KEY = self.config['key']
        self.tool_source = 'GitHub Repo Info Worker'
        self.tool_version = '0.0.1'
        self.data_source = 'GitHub API'
        self.results_counter = 0
        self.finishing_task = False
        self.info_id_inc = None

        self.specs = {
            "id": self.config['id'],
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["github_url"]],
                    "models":["repo_info"]
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['database']
        )

        logging.info("Making database connections...")

        dbschema = 'augur_data'
        self.db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        metadata = MetaData()
        helper_metadata = MetaData()

        metadata.reflect(self.db, only=['repo_info'])
        helper_metadata.reflect(self.helper_db, only=['worker_history', 'worker_job', 'worker_oauth'])

        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)

        Base.prepare()
        HelperBase.prepare()

        self.repo_info_table = Base.classes.repo_info.__table__

        self.history_table = HelperBase.classes.worker_history.__table__
        self.job_table = HelperBase.classes.worker_job.__table__

        maxHistorySQL = s.sql.text("""
            SELECT max(history_id) AS history_id
            FROM worker_history
        """)
        rs = pd.read_sql(maxHistorySQL, self.helper_db, params={})
        self.history_id = int(rs.iloc[0]["history_id"]) if rs.iloc[0]["history_id"] is not None else 25150

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = self.history_id if self.finishing_task else self.history_id + 1

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

    @property
    def task(self):
        """ Property that is returned when the worker's current task is referenced """
        return self._task

    @task.setter
    def task(self, value):
        """ entry point for the broker to add a task to the queue
        Adds this task to the queue, and calls method to process queue
        """
        
        if value['job_type'] == "UPDATE" or value['job_type'] == "MAINTAIN":
            self._queue.put(value)

        if 'focused_task' in value:
            if value['focused_task'] == 1:
                logging.info("Focused task is ON\n")
                self.finishing_task = True
            else:
                self.finishing_task = False
                logging.info("Focused task is OFF\n")
        else:
            self.finishing_task = False
            logging.info("focused task is OFF\n")
        
        self._task = value
        self.run()

    def cancel(self):
        """ Delete/cancel current task """
        self._task = None

    def run(self):
        logging.info("Running...")
        self._child = Process(target=self.collect, args=())
        self._child.start()

    def collect(self, repos=None):

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

            """ Query all repos with repo url of given task """
            repoUrlSQL = s.sql.text("""
                SELECT min(repo_id) as repo_id FROM repo WHERE repo_git = '{}'
                """.format(message['given']['github_url']))
            repo_id = int(pd.read_sql(repoUrlSQL, self.db, params={}).iloc[0]['repo_id'])

            try:
                self.repo_info_model(message, repo_id)
            except Exception:
                raise ValueError('Worker ran into an error for task {}'.format(message))

    def get_owner_repo(self, github_url):
        split = github_url.split('/')

        owner = split[-2]
        repo = split[-1]

        if '.git' in repo:
            repo = repo[:-4]

        return owner, repo

    def repo_info_model(self, task, repo_id):

        github_url = task['given']['github_url']

        logging.info("Beginning filling the repo_info model for repo: " + github_url + "\n")
        record_model_process(self, logging, repo_id, 'repo_info')

        owner, repo = self.get_owner_repo(github_url)

        url = 'https://api.github.com/graphql'

        query = """
            {
                repository(owner:"%s", name:"%s"){
                    updatedAt
                    hasIssuesEnabled
                    issues(states:OPEN) {
                        totalCount
                    }
                    hasWikiEnabled
                    forkCount
                    defaultBranchRef {
                        name
                    }
                    watchers {
                        totalCount
                    }
                    id
                    licenseInfo {
                        name
                        url
                    }
                    stargazers {
                        totalCount
                    }
                    codeOfConduct {
                        name
                        url
                    }
                    issue_count: issues {
                        totalCount
                    }
                    issues_closed: issues(states:CLOSED) {
                        totalCount
                    }
                    pr_count: pullRequests {
                        totalCount
                    }
                    pr_open: pullRequests(states: OPEN) {
                        totalCount
                    }
                    pr_closed: pullRequests(states: CLOSED) {
                        totalCount
                    }
                    pr_merged: pullRequests(states: MERGED) {
                        totalCount
                    }
                    ref(qualifiedName: "master") {
                        target {
                            ... on Commit {
                                history(first: 0){
                                    totalCount
                                }
                            }
                        }
                    }
                }
            }
        """ % (owner, repo)

        logging.info(f'Hitting endpoint {url}')
        try:
            r = requests.post(url, json={'query': query}, headers=self.headers)
            update_gh_rate_limit(self, logging, r)
            j = r.json()
            if 'errors' in j:
                register_task_failure(self, logging, task, repo_id, ValueError(f"[GitHub API]: {j['errors'][0]['type']}: {j['errors'][0]['message']}"))
                return

            j = j['data']['repository']
        except requests.exceptions.ConnectionError as e:
            register_task_failure(self, logging, task, repo_id, e)
            return
        except Exception as e:
            register_task_failure(self, logging, task, repo_id, e)
            return

        committers_count = self.query_committers_count(owner, repo)
        # commit_count = self.query_commit_count(owner, repo)

        logging.info(f'Inserting repo info for repo with id:{repo_id}, owner:{owner}, name:{repo}')
        # logging.info("1 {}\n\n\n".format(j))
        # logging.info("2 {}\n\n\n".format(j['ref']))
        # logging.info("3 {}\n\n\n".format(j['ref']['target']))
        # logging.info("4 {}\n\n\n".format(j['ref']['target']['history']))
        rep_inf = {
            'repo_id': repo_id,
            'last_updated': j['updatedAt'] if 'updatedAt' in j else None,
            'issues_enabled': j['hasIssuesEnabled'] if 'hasIssuesEnabled' in j else None,
            'open_issues': j['issues']['totalCount'] if j['issues'] else None,
            'pull_requests_enabled': None,
            'wiki_enabled': j['hasWikiEnabled'] if 'hasWikiEnabled' in j else None,
            'pages_enabled': None,
            'fork_count': j['forkCount'] if 'forkCount' in j else None,
            'default_branch': j['defaultBranchRef']['name'] if j['defaultBranchRef'] else None,
            'watchers_count': j['watchers']['totalCount'] if j['watchers'] else None,
            'UUID': None,
            'license': j['licenseInfo']['name'] if j['licenseInfo'] else None,
            'stars_count': j['stargazers']['totalCount'] if j['stargazers'] else None,
            'committers_count': committers_count,
            'issue_contributors_count': None,
            'changelog_file': None,
            'contributing_file': None,
            'license_file': j['licenseInfo']['url'] if j['licenseInfo'] else None,
            'code_of_conduct_file': j['codeOfConduct']['url'] if j['codeOfConduct'] else None,
            'security_issue_file': None,
            'security_audit_file': None,
            'status': None,
            'keywords': None,
            'commit_count': j['ref']['target']['history']['totalCount'] if j['ref'] else None,
            'issues_count': j['issue_count']['totalCount'] if j['issue_count'] else None,
            'issues_closed': j['issues_closed']['totalCount'] if j['issues_closed'] else None,
            'pull_request_count': j['pr_count']['totalCount'] if j['pr_count'] else None,
            'pull_requests_open': j['pr_open']['totalCount'] if j['pr_open'] else None,
            'pull_requests_closed': j['pr_closed']['totalCount'] if j['pr_closed'] else None,
            'pull_requests_merged': j['pr_merged']['totalCount'] if j['pr_merged'] else None,
            'tool_source': self.tool_source,
            'tool_version': self.tool_version,
            'data_source': self.data_source,
            'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        result = self.db.execute(self.repo_info_table.insert().values(rep_inf))
        logging.info(f"Primary Key inserted into repo_info table: {result.inserted_primary_key}")
        self.results_counter += 1

        logging.info(f"Inserted info for {owner}/{repo}")

        #Register this task as completed
        register_task_completion(self, logging.getLogger(), task, repo_id, "repo_info")

    def query_committers_count(self, owner, repo):
        logging.info('Querying committers count')
        url = f'https://api.github.com/repos/{owner}/{repo}/contributors?per_page=100'
        committers = 0

        try:
            while True:
                r = requests.get(url, headers=self.headers)
                update_gh_rate_limit(self, logging, r)
                committers += len(r.json())

                if 'next' not in r.links:
                    break
                else:
                    url = r.links['next']['url']
        except Exception:
            logging.exception('An error occured while querying contributor count')

        return committers

    # def query_commit_count(self, owner, repo):
    #     logging.info('Querying commit count')
    #     commits_url = f'https://api.github.com/repos/{owner}/{repo}/commits'
    #     r = requests.get(commits_url, headers=self.headers)
    #     update_gh_rate_limit(self, logging, r)

    #     first_commit_sha = None
    #     last_commit_sha = r.json()[0]['sha']

    #     if 'last' in r.links:
    #         r = requests.get(r.links['last']['url'], headers=self.headers)
    #         update_gh_rate_limit(self, logging, r)

    #         first_commit_sha = r.json()[-1]['sha']

    #     else:
    #         first_commit_sha = r.json()[-1]['sha']

    #     compare_url = (f'https://api.github.com/repos/{owner}/{repo}/'
    #                 + f'compare/{first_commit_sha}...{last_commit_sha}')
    #     r = requests.get(compare_url, headers=self.headers)
    #     update_gh_rate_limit(self, logging, r)

    #     return r.json()['total_commits'] + 1

