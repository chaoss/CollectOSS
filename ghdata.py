import datetime
from github import Github, GithubException
import records
import requests

class GHData:
    def __init__(self, username, password=None, db_host='127.0.0.1', db_port=3306, db_user='root', db_pass=None, db_name='ghtorrent'):
        try:
            self.github_api = Github(username, password)
        except e:
            if e is GithubException.BadCredentialsException:
                print('Bad credentials.')

    # Gets information about the current user
    def user(self, username=None, start=None, end=None):
        if (username and len(username)):
            user = self.github_api.get_user(username)
        else:
            user = self.github_api.get_user()
        return user