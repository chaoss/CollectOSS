import datetime
from github import Github

class GHData:
    def __init__(self, username, password):
        self.github_api = Github(username, password)

    def user(username='', start_date=None, end_date='now'):
        if username is '':
            user = self.github_api.get_user()
        else:
            user = self.github_api.get_user(username)
        return user