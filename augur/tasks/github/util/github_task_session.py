import os
import sqlalchemy as s
import time
import sys

from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.application.db.session import DatabaseSession


class GithubTaskSession(DatabaseSession):

    def __init__(self, logger):

        # initalizes the super class DatabaseSession with the logger
        super().__init__(logger)

        # creates the key authentication class and passes the session and config
        self.oauths = GithubRandomKeyAuth(self)
        self.platform_id = 1
        
