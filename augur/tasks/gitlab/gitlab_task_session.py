"""
Defines a GitLab-specific session and manifest object for use in GitLab tasks
"""
from logging import Logger

from augur.tasks.gitlab.gitlab_random_key_auth import GitlabRandomKeyAuth
from augur.application.db.session import DatabaseSession

class GitlabTaskManifest:
    """
    Manifest object that represents the state and common elements of
    the specified task. GitLab version for the GitLab tasks.

    Attributes:
        augur_db: sqlalchemy db object
        key_auth: GitLab specific key auth retrieval collection
        logger: logging object
        platform_id: GitLab specific platform id (github is 1)
    """

    def __init__(self, logger):

        from augur.tasks.init.celery_app import engine

        self.augur_db = DatabaseSession(logger, engine)
        self.key_auth = GitlabRandomKeyAuth(self.augur_db.session, logger)
        self.logger = logger
        self.platform_id = 2

    def __enter__(self):

        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):

        self.augur_db.close()

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

        self.oauths = GitlabRandomKeyAuth(self, logger)
        self.platform_id = 2
        
