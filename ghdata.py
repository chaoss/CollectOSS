import datetime
from github import Github, GithubException

class GHData:
    def __init__(self, username, password=None):
        try:
            self.github_api = Github(username, password)
        except e:
            if e is GithubException.BadCredentialsException:
                print('Bad credentials.')

    def user(self, username=None, start=None, end=None):
        if (username):
            user = self.github_api.get_user(username)
        else:
            user = self.github_api.get_user()
        return user