"""Defines the GitlabRandomKeyAuth class"""

from augur.tasks.util.random_key_auth import RandomKeyAuth
from augur.tasks.gitlab.gitlab_api_key_handler import GitlabApiKeyHandler
from augur.application.db.session import DatabaseSession


class GitlabRandomKeyAuth(RandomKeyAuth):
    """Defines a github specific RandomKeyAuth class so 
    github collections can have a class randomly selects an api key for each request    
    """

    def __init__(self, session: DatabaseSession, logger):
        """Creates a GitlabRandomKeyAuth object and initializes the RandomKeyAuth parent class"""

    
        # gets the gitlab api keys from the database via the GitlabApiKeyHandler
        gitlab_api_keys = GitlabApiKeyHandler(session).keys

        if not gitlab_api_keys:
            print("Failed to find github api keys. This is usually because your key has expired")

        header_name = "Authorization"
        key_format = "Bearer {0}"

        super().__init__(gitlab_api_keys, header_name, session.logger, key_format)