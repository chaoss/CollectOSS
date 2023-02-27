"""Defines the GithubRandomKeyAuth class"""

from augur.tasks.util.random_key_auth import RandomKeyAuth
from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler
from augur.application.db.session import DatabaseSession


class GithubRandomKeyAuth(RandomKeyAuth):
    """Defines a github specific RandomKeyAuth class so 
    github collections can have a class randomly selects an api key for each request    
    """

    def __init__(self, session: DatabaseSession, logger):
        """Creates a GithubRandomKeyAuth object and initializes the RandomKeyAuth parent class"""

    
        # gets the github api keys from the database via the GithubApiKeyHandler
        github_api_keys = GithubApiKeyHandler(session).keys

        if not github_api_keys:
            print("Failed to find github api keys. This is usually because your key has expired")

        # defines the structure of the github api key
        header_name = "Authorization"
        key_format = "token {0}"

        super().__init__(github_api_keys, header_name, session.logger, key_format)