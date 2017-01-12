import datetime
from github import Github, GithubException 
import json
import csv
import records
import requests

class GHData:
    def __init__(self, username, password=None, db_host='127.0.0.1', db_port=3306, db_user='root', db_pass=None, db_name='ghtorrent', apionly=False):
        try:
            self.github_api = Github(username, password)
        except e:
            if e is GithubException.BadCredentialsException:
                print('Bad credentials.')
    
    # Concatenates the two list and returns it in the requested format
    def concat(self, GHAPIList=None, GHTorrentList=None):
        result = []
        if (GHAPIList is not None):
            result += GHAPIList
        if (GHTorrentList is not None and self.apionly == False):
            result += GHTorrentList

        return result


    # Gets information about the current user
    def user(self, username=None, start=None, end=None):
        if (username and len(username)):
            user = self.github_api.get_user(username)
        else:
            user = self.github_api.get_user()

        GHAPIList = [user.raw_data]
        return concat(GHAPIList=GHAPIList)