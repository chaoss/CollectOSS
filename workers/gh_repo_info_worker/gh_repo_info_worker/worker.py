from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
import logging
import time
from datetime import datetime

logging.basicConfig(filename='worker.log', level=logging.INFO, filemode='w')


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
            "id": "com.augurlabs.core.gh_repo_info",
            "location": "http://localhost:51237",
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["repo_info"]
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['name']
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
        # helper_metadata.reflect(self.helper_db)

        Base = automap_base(metadata=metadata)

        Base.prepare()

        self.repo_info_table = Base.classes.repo_info.__table__

        logging.info('Getting max repo_info_id...')
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

        # requests.post('http://localhost:5000/api/unstable/workers', json=specs)

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

    def cancel(self):
        """ Delete/cancel current task """
        self._task = None

    def run(self):
        logging.info("Running...")
        self._child = Process(target=self.collect, args=())
        self._child.start()

    def collect(self, repos=None):

        if repos == None:
            repo_id_sql = s.sql.text("""
                SELECT repo_id, repo_git FROM repo
            """)

            repos = pd.read_sql(repo_id_sql, self.db)

        for _, row in repos.iterrows():
            owner, repo = self.get_owner_repo(row['repo_git'])
            self.query_repo_info(row['repo_id'], owner, repo)


    def get_owner_repo(self, git_url):
        split = git_url.split('/')

        owner = split[-2]
        repo = split[-1]

        if '.git' in repo:
            repo = repo[:-4]

        return owner, repo

    def query_repo_info(self, repo_id, owner, repo):
        # url = f'https://api.github.com/repos/{owner}/{repo}'
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
                }
            }
        """ % (owner, repo)

        logging.info(f'Hitting endpoint {url}')
        try:
            # r = requests.get(url, headers=self.headers)
            r = requests.post(url, json={'query': query}, headers=self.headers)
            self.update_rate_limit(r)
            j = r.json()['data']['repository']
        except Exception as e:
            logging.error('Caught Exception:', str(e))

        logging.info(f'Inserting repo info for repo with id:{repo_id}, owner:{owner}, name:{repo}')

        rep_inf = {
            'repo_info_id': self.info_id_inc,
            'repo_id': repo_id,
            'last_updated': j['updatedAt'],
            'issues_enabled': j['hasIssuesEnabled'],
            'open_issues': j['issues']['totalCount'],
            'pull_requests_enabled': None,
            'wiki_enabled': j['hasWikiEnabled'],
            'pages_enabled': None,
            'fork_count': j['forkCount'],
            'default_branch': j['defaultBranchRef']['name'],
            'watchers_count': j['watchers']['totalCount'],
            'UUID': None,
            'license': j['licenseInfo']['name'] if j['licenseInfo'] else None,
            'stars_count': j['stargazers']['totalCount'],
            'committers_count': None,
            'issue_contributors_count': None,
            'changelog_file': None,
            'contributing_file': None,
            'license_file': j['licenseInfo']['url'] if j['licenseInfo'] else None,
            'code_of_conduct_file': j['codeOfConduct']['url'] if j['codeOfConduct'] else None,
            'security_issue_file': None,
            'security_audit_file': None,
            'status': None,
            'keywords': None,
            'tool_source': self.tool_source,
            'tool_version': self.tool_version,
            'data_source': self.data_source,
            'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        result = self.db.execute(self.repo_info_table.insert().values(rep_inf))
        logging.info(f"Primary Key inserted into repo_info table: {result.inserted_primary_key}")
        self.results_counter += 1

        logging.info(f"Inserted info for {owner}/{repo}")

        self.info_id_inc += 1



    def update_rate_limit(self, response):
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
