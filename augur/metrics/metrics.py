import sqlalchemy as s
from augur.util import logger

from .commits import create_commit_metrics, create_commit_routes
from .contributors import create_contributor_metrics, create_contributor_routes
from .experimental import create_experimental_metrics, create_experimental_routes
from .insights import create_insight_metrics, create_insight_routes
from .issues import create_issue_metrics, create_issue_routes
from .messages import create_message_metrics, create_message_routes
from .platforms import create_platform_metrics, create_platform_routes
from .pull_requests import create_pull_request_metrics, create_pull_request_routes
from .repo_meta import create_repo_meta_metrics, create_repo_meta_routes

class MetricDefinitions():
    """docstring for MetricDefinitions"""
    def __init__(self, app):
        self.app = app

        self.user = self.app.read_config('Database', 'user', 'AUGUR_DB_USER', 'augur')
        self.password = self.app.read_config('Database', 'password', 'AUGUR_DB_PASS', 'password')
        self.host = self.app.read_config('Database', 'host', 'AUGUR_DB_HOST', '127.0.0.1')
        self.port = self.app.read_config('Database', 'port', 'AUGUR_DB_PORT', '5433')
        self.dbname = self.app.read_config('Database', 'database', 'AUGUR_DB_NAME', 'augur')
        self.schema = self.app.read_config('Database', 'schema', 'AUGUR_DB_SCHEMA', 'augur_data')

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.user, self.password, self.host, self.port, self.dbname
        )

        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(self.schema)})

        spdx_schema = 'spdx'
        self.spdx_db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={},{}'.format(spdx_schema, self.schema)})

        logger.debug('Augur DB: Connecting to {} schema of {}:{}/{} as {}'.format(self.schema, self.host, self.port, self.dbname, self.user))

        create_commit_metrics(self)
        create_contributor_metrics(self)
        create_experimental_metrics(self)
        create_insight_metrics(self)
        create_issue_metrics(self)
        create_message_metrics(self)
        create_platform_metrics(self)
        create_pull_request_metrics(self)
        create_repo_meta_metrics(self)


    def create_routes(self, server):
        create_commit_routes(server)
        create_contributor_routes(server)
        create_experimental_routes(server)
        create_insight_routes(server)
        create_issue_routes(server)
        create_message_routes(server)
        create_platform_routes(server)
        create_pull_request_routes(server)
        create_repo_meta_routes(server)