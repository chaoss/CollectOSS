"""
Defines a GitLab-specific session and manifest object for use in GitLab tasks
"""
from logging import Logger

from augur.tasks.gitlab.gitlab_random_key_auth import GitlabRandomKeyAuth
from augur.application.db.session import DatabaseSession
from augur.application.db import get_engine

class GitlabTaskSession(DatabaseSession):
    """ORM session used in gitlab tasks.
        This class adds the platform_id and the gitlab key authentication class,
        to the already existing DatabaseSession so there is a central location to access
        api keys and a single platform_id reference

    Attributes:
        oauths (GitlabRandomKeyAuth): Class that handles randomly assigning gitlab api keys to httpx requests
        platform_id (int): The id that refers to the Gitlab platform
    """

    def __init__(self, logger: Logger, engine=None):

        super().__init__(logger, engine=engine)

        self.oauths = GitlabRandomKeyAuth(logger)
        self.platform_id = 2
        
