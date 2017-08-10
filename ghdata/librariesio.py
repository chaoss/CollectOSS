import requests
import pandas as pd
import numpy as np

class LibrariesIO(object):
    """Handles interaction with https://libraries.io/api to get dependency data"""
    def __init__(self, api_key):
        self.API_KEY = api_key

    def dependencies(self, owner, repo):
        """
        Finds the packages that a project depends on

        :param owner: GitHub username of the owner of the repo
        :param repo: Repository name
        :return: Dict that contains the results (https://libraries.io/api#repository-dependencies)
        """
        url = "https://libraries.io/api/github/{owner}/{repo}/dependencies".format(owner=owner, repo=repo)
        r = requests.get(url, params={"api_key": self.API_KEY})
        return r.json()

    def dependents(self, owner, repo):
        """
        Finds the packages depend on this repository

        :param owner: GitHub username of the owner of the repo
        :param repo: Repository name
        :return: Dict that contains the results (https://libraries.io/api#project-dependents)
        """
        projectsUrl = "https://libraries.io/api/github/{owner}/{repo}/projects".format(owner=owner, repo=repo)
        projectsRequest = requests.get(projectsUrl, params={"api_key": self.API_KEY})
        json = projectsRequest.json()

        if projectsRequest.status_code == 400:
            print('You need to set the LibrariesIO API key in ghdata.cfg or the environment variable GHDATA_LIBRARIESIO_API_KEY')

        if projectsRequest.status_code != 200:
            return projectsRequest.json()
        else:
            print(projectsRequest.text)
            project = projectsRequest.json()[0]['name']
            platform = projectsRequest.json()[0]['platform']
            dependentsUrl = "https://libraries.io/api/{platform}/{repo}/dependents".format(platform=platform, repo=repo)
            print(dependentsUrl)
            dependentsRequest = requests.get(dependentsUrl, params={"api_key": self.API_KEY})
            print(dependentsRequest.text)
            return dependentsRequest