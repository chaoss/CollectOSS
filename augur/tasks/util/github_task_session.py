import os
import sqlalchemy as s
import time
import sys

from augur.tasks.util.api_key_handler import ApiKeyHandler
from augur.tasks.util.random_key_auth import RandomKeyAuth
from augur.application.db.session import DatabaseSession


class GithubTaskSession(DatabaseSession):

    def __init__(self, logger=None, platform: str ='GitHub'):

        super().__init__(logger)

        api_key_handler = ApiKeyHandler()
        github_api_keys = api_key_handler.get_github_keys()

        self.oauths = RandomKeyAuth(github_api_keys)
        
