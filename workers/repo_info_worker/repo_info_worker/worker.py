import logging
import os
import sys
import time
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse

import pandas as pd
import requests
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base


LOG_FORMAT = '%(levelname)s:[%(name)s]: %(message)s'
logging.basicConfig(filename='worker.log', level=logging.INFO, filemode='w', format=LOG_FORMAT)
logger = logging.getLogger('RepoInfoWorker')


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
    """
    result = []
    queue.put("STOP")
    for i in iter(queue.get, 'STOP'):
        result.append(i)
    # time.sleep(.1)
    return result


class GHRepoInfoWorker:
    def __init__(self, config, task=None):
        self._task = task
        self._child = None
        self._queue = Queue()
        self._maintain_queue = Queue()
        self.working_on = None
        self.config = config
        self.db = None
        self.table = None
        self.API_KEY = self.config['key']
        self.tool_source = 'GitHub Repo Info Worker'
        self.tool_version = '0.0.1'
        self.data_source = 'GitHub API'
        self.results_counter = 0
        self.headers = {'Authorization': f'token {self.API_KEY}',
                        'Accept': 'application/vnd.github.vixen-preview+json'}

        url = 'https://api.github.com'
        response = requests.get(url, headers=self.headers)
        self.rate_limit = int(response.headers['X-RateLimit-Remaining'])

        specs = {
            "id": self.config['id'],
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["repo_info"]
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['database']
        )

        logger.info("Making database connections...")

        dbschema = 'augur_data'
        self.db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        metadata = MetaData()
        helper_metadata = MetaData()

        metadata.reflect(self.db, only=['repo_info'])
        helper_metadata.reflect(self.helper_db)

        Base = automap_base(metadata=metadata)

        Base.prepare()

        self.repo_info_table = Base.classes.repo_info.__table__

        logger.info('Getting max repo_info_id...')
        max_repo_info_id_sql = s.sql.text("""
            SELECT MAX(repo_info_id) AS repo_info_id
            FROM repo_info
        """)
        rs = pd.read_sql(max_repo_info_id_sql, self.db)

        repo_info_start_id = int(rs.iloc[0]['repo_info_id']) if rs.iloc[0]['repo_info_id'] is not None else 1

        if repo_info_start_id == 1:
            self.info_id_inc = repo_info_start_id
        else:
            self.info_id_inc = repo_info_start_id + 1

        try:
            requests.post('http://localhost:{}/api/unstable/workers'.format(
                self.config['broker_port']), json=specs)
        except requests.exceptions.ConnectionError:
            logger.error('Cannot connect to the broker. Quitting...')
            sys.exit('Cannot connect to the broker! Quitting...')

    @property
    def task(self):
        """ Property that is returned when the worker's current task is referenced """
        return self._task

    # @task.setter
    # def task(self, value):
        # repo_id_sql = s.sql.text("""
        #     SELECT repo_id, repo_git FROM repo
        # """)

        # repos = pd.read_sql(repo_id_sql, self.db)

    @task.setter
    def task(self, value):
        git_url = value['given']['git_url']

        repo_url_SQL = s.sql.text("""
            SELECT min(repo_id) AS repo_id
            FROM repo
            WHERE repo_git = :repo_git
        """)

        rs = pd.read_sql(repo_url_SQL, self.db, params={'repo_git': git_url})

        try:
            repo_id = int(rs.iloc[0]['repo_id'])
            if value['job_type'] == 'UPDATE':
                self._queue.put(CollectorTask('TASK', {"git_url": git_url, "repo_id": repo_id}))
            elif value['job_type'] == 'MAINTAIN':
                self._maintain_queue.put(CollectorTask('TASK', {"git_url": git_url, "repo_id": repo_id}))

            if 'focused_task' in value:
                if value['focused_task'] == 1:
                    self.finishing_task = True

        except Exception as e:
            logger.error(f"Error: {e}, or that repo is not in our database: {value}")

        self._task = CollectorTask('TASK', {"git_url": git_url, "repo_id": repo_id})
        self.run()

    def cancel(self):
        """ Delete/cancel current task """
        self._task = None

    def run(self):
        logger.info("Running...")
        if self._child is None:
            self._child = Process(target=self.collect, args=())
            self._child.start()
            # requests.post("http://localhost:{}/api/unstable/add_pids".format(
            #     self.config['broker_port']), json={'pids': [self._child.pid, os.getpid()]})

    def collect(self, repos=None):

        while True:
            time.sleep(4.5)
            if not self._queue.empty():
                message = self._queue.get()
                self.working_on = 'UPDATE'
            elif not self._maintain_queue.empty():
                message = self._maintain_queue.get()
                logger.info(f"Popped off message: {message.entry_info}")
                self.working_on = "MAINTAIN"
            else:
                break

            if message.type == 'EXIT':
                break

            if message.type != 'TASK':
                raise ValueError(f'{message.type} is not a recognized task type')

            if message.type == 'TASK':
                try:
                    self.query_repo_info(message.entry_info['repo_id'],
                                         message.entry_info['git_url'])
                except Exception:
                    logger.exception(f'Worker ran into an error for task {message.entry_info}')
                    self.register_task_failure(message.entry_info['repo_id'],
                                                  message.entry_info['git_url'])


        # if repos == None:
        #     repo_id_sql = s.sql.text("""
        #         SELECT repo_id, repo_git FROM repo
        #     """)

        #     repos = pd.read_sql(repo_id_sql, self.db)

        # for _, row in repos.iterrows():
        #     owner, repo = self.get_owner_repo(row['repo_git'])
        #     print(f'Querying: {owner}/{repo}')
        #     self.query_repo_info(row['repo_id'], owner, repo)

        # print(f'Added repo info for {self.results_counter} repos')


    def get_owner_repo(self, git_url):
        split = git_url.split('/')

        owner = split[-2]
        repo = split[-1]

        if '.git' in repo:
            repo = repo[:-4]

        return owner, repo

    def query_repo_info(self, repo_id, git_url):
        # url = f'https://api.github.com/repos/{owner}/{repo}'
        url = 'https://api.github.com/graphql'

        owner, repo = self.get_owner_repo(git_url)

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
                }
            }
        """ % (owner, repo)

        logger.info(f'Hitting endpoint {url}')
        try:
            # r = requests.get(url, headers=self.headers)
            r = requests.post(url, json={'query': query}, headers=self.headers)
            self.update_rate_limit(r)

            j = r.json()
            if 'errors' in j:
                logger.error(f"[GitHub API]: {j['errors'][0]['type']}: {j['errors'][0]['message']}")
                self.register_task_failure(repo_id, git_url)
                return

            j = j['data']['repository']
        except requests.exceptions.ConnectionError:
            logger.error('Could not connect to api.github.com')
        except Exception as e:
            logger.exception(f'Caught Exception: {e}')

        committers_count = self.query_committers_count(owner, repo)
        commit_count = self.query_commit_count(owner, repo)

        logger.info(f'Inserting repo info for repo with id:{repo_id}, owner:{owner}, name:{repo}')

        rep_inf = {
            'repo_info_id': self.info_id_inc,
            'repo_id': repo_id,
            'last_updated': j['updatedAt'],
            'issues_enabled': j['hasIssuesEnabled'],
            'open_issues': j['issues']['totalCount'] if j['issues'] else None,
            'pull_requests_enabled': None,
            'wiki_enabled': j['hasWikiEnabled'],
            'pages_enabled': None,
            'fork_count': j['forkCount'],
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
            'commit_count': commit_count,
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
        logger.info(f"Primary Key inserted into repo_info table: {result.inserted_primary_key}")
        self.results_counter += 1

        logger.info(f"Inserted info for {owner}/{repo}")

        self.info_id_inc += 1

        self.register_task_completion(repo_id, git_url)

    def query_committers_count(self, owner, repo):
        logger.info('Querying committers count')
        url = f'https://api.github.com/repos/{owner}/{repo}/contributors?per_page=100'
        committers = 0

        try:
            while True:
                r = requests.get(url, headers=self.headers)
                self.update_rate_limit(r)
                committers += len(r.json())

                if 'next' not in r.links:
                    break
                else:
                    url = r.links['next']['url']
        except Exception:
            logger.exceptioin('An error occured while querying contributor count')

        return committers

    def query_commit_count(self, owner, repo):
        logger.info('Querying commit count')
        commits_url = f'https://api.github.com/repos/{owner}/{repo}/commits'
        r = requests.get(commits_url, headers=self.headers)
        self.update_rate_limit(r)

        first_commit_sha = None
        last_commit_sha = r.json()[0]['sha']

        if 'last' in r.links:
            r = requests.get(r.links['last']['url'], headers=self.headers)
            self.update_rate_limit(r)

            first_commit_sha = r.json()[-1]['sha']

        else:
            first_commit_sha = r.json()[-1]['sha']

        compare_url = (f'https://api.github.com/repos/{owner}/{repo}/'
                    + f'compare/{first_commit_sha}...{last_commit_sha}')
        r = requests.get(compare_url, headers=self.headers)
        self.update_rate_limit(r)

        return r.json()['total_commits'] + 1



    def update_rate_limit(self, response):
        try:
            self.rate_limit = int(response.headers['X-RateLimit-Remaining'])
            logger.info("[Rate Limit]: Recieved rate limit from headers")
        except:
            self.rate_limit -= 1
            logger.info("[Rate Limit]: Headers did not work, had to decrement")
        logger.info(f"[Rate Limit]: Updated rate limit, you have: {self.rate_limit} requests remaining")
        if self.rate_limit <= 0:
            reset_time = response.headers['X-RateLimit-Reset']
            time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
            logger.info(f"[Rate Limit]: Rate limit exceeded, waiting {time_diff.total_seconds()} seconds")
            time.sleep(time_diff.total_seconds())
            self.rate_limit = int(response.headers['X-RateLimit-Limit'])

    def register_task_completion(self, repo_id, git_url):
        task_completed = {
            'worker_id': self.config['id'],
            'job_type': self.working_on,
            'repo_id': repo_id,
            'git_url': git_url
        }

        logger.info(f"Telling broker we completed task: {task_completed}")
        logger.info(f"This task inserted {self.results_counter} tuples\n")

        try:
            requests.post('http://localhost:{}/api/unstable/completed_task'.format(
                self.config['broker_port']), json=task_completed)
        except requests.exceptions.ConnectionError:
            logger.info("Broker is booting and cannot accept the worker's message currently")
        self.results_counter = 0

    def register_task_failure(self, repo_id, git_url):
        task_failed = {
            'worker_id': self.config['id'],
            'job_type': self.working_on,
            'repo_id': repo_id,
            'git_url': git_url
        }

        logger.error('Task failed')
        logger.error('Informing broker about Task Failure')
        logger.info(f'This task inserted {self.results_counter} tuples\n')

        try:
            requests.post('http://localhost:{}/api/unstable/task_error'.format(
                          self.config['broker_port']), json=task_failed)
        except requests.exceptions.ConnectionError:
            logger.error('Could not send task failure message to the broker')
        except Exception:
            logger.exception('An error occured while informing broker about task failure')
