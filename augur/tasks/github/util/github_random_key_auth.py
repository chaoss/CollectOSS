"""Defines the GithubRandomKeyAuth class"""

from augur.tasks.util.random_key_auth import RandomKeyAuth
from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler


class GithubRandomKeyAuth(RandomKeyAuth):
    """Defines a github specific RandomKeyAuth class so 
    github collections can have a class randomly selects an api key for each request    
    """

    def __init__(self, session):
        """Creates a GithubRandomKeyAuth object and initializes the RandomKeyAuth parent class"""

        # gets the github api keys from the database via the GithubApiKeyHandler
        github_api_keys = GithubApiKeyHandler(session).keys

        # defines the structure of the github api key
        header_name = "Authorization"
        key_format = "token {0}"

        super().__init__(github_api_keys, header_name, key_format)