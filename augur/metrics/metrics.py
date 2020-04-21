from augur.util import logger

from .commit import create_commit_metrics, create_commit_routes
from .contributor import create_contributor_metrics, create_contributor_routes
from .experimental import create_experimental_metrics, create_experimental_routes
from .insight import create_insight_metrics, create_insight_routes
from .issue import create_issue_metrics, create_issue_routes
from .message import create_message_metrics, create_message_routes
from .platform import create_platform_metrics, create_platform_routes
from .pull_request import create_pull_request_metrics, create_pull_request_routes
from .repo_meta import create_repo_meta_metrics, create_repo_meta_routes
from .util import create_util_metrics, create_util_routes

class MetricDefinitions():
    def __init__(self, app):
        self.projects = None
        self.database = app.database
        self.spdx_db = app.spdx_db

        # TODO: not hardcode this
        create_commit_metrics(self)
        create_contributor_metrics(self)
        create_experimental_metrics(self)
        create_insight_metrics(self)
        create_issue_metrics(self)
        create_message_metrics(self)
        create_platform_metrics(self)
        create_pull_request_metrics(self)
        create_repo_meta_metrics(self)
        create_util_metrics(self)

    def create_routes(self, server):
        # TODO: not hardcode this
        create_commit_routes(server)
        create_contributor_routes(server)
        create_experimental_routes(server)
        create_insight_routes(server)
        create_issue_routes(server)
        create_message_routes(server)
        create_platform_routes(server)
        create_pull_request_routes(server)
        create_repo_meta_routes(server)
        create_util_routes(server)
