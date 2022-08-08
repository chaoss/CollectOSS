from augur.tasks.util.random_key_auth import RandomKeyAuth
from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler


class GithubRandomKeyAuth(RandomKeyAuth):

    # optionally takes a session and config
    def __init__(self, session):

        github_api_keys = GithubApiKeyHandler(session).keys
        
        super().__init__(github_api_keys)