from logging import Logger

from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.application.db.session import DatabaseSession
from augur.tasks.init.celery_app import engine


class GithubTaskSession(DatabaseSession):
    """ORM session used in github tasks.
        This class adds the platform_id and the github key authentication class,
        to the already existing DatabaseSession so there is a central location to access
        api keys and a single platform_id reference

    Attributes:
        oauths (GithubRandomKeyAuth): Class that handles randomly assigning github api keys to httpx requests
        platform_id (int): The id that refers to the Github platform
    """

    def __init__(self, logger: Logger, engine=None):

        super().__init__(logger, engine=engine)

        self.oauths = GithubRandomKeyAuth(self)
        self.platform_id = 1
        
