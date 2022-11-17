"""Defines the GithubRandomKeyAuth class"""

from augur.tasks.util.random_key_auth import RandomKeyAuth
from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler
from augur.application.db.session import DatabaseSession
from augur.tasks.init.celery_app import engine


class GithubRandomKeyAuth(RandomKeyAuth):
    """Defines a github specific RandomKeyAuth class so 
    github collections can have a class randomly selects an api key for each request    
    """

    def __init__(self, session: DatabaseSession):
        """Creates a GithubRandomKeyAuth object and initializes the RandomKeyAuth parent class"""

        attempts = 0
        while attempts <= 3:

            # gets the github api keys from the database via the GithubApiKeyHandler
            github_api_keys = GithubApiKeyHandler(session).keys

            if github_api_keys:
                break

            print("Failed to get github api keys trying up to 3 times")
            attempts += 1


        # defines the structure of the github api key
        header_name = "Authorization"
        key_format = "token {0}"

        super().__init__(github_api_keys, header_name, session.logger, key_format)