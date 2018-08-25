"""
Data source that uses the LibrariesIO dependency data
"""

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from augur import logger
from augur.util import annotate

# end imports
# (don't remove the above line, it's for a script)

class LibrariesIO(object):
    """Handles interaction with https://libraries.io/api to get dependency data"""
    def __init__(self, api_key, githubapi):
        self.API_KEY = api_key
        self.__githubapi = githubapi.api

    #####################################
    ###    DIVERSITY AND INCLUSION    ###
    #####################################


    #####################################
    ### GROWTH, MATURITY, AND DECLINE ###
    #####################################


    #####################################
    ###            RISK               ###
    #####################################


    #####################################
    ###            VALUE              ###
    #####################################


    #####################################
    ###           ACTIVITY            ###
    #####################################


    #####################################
    ###         EXPERIMENTAL          ###
    #####################################

    @annotate(tag='dependencies')
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

    @annotate(tag='dependency-stats')
    def dependency_stats(self, owner, repo):
        """
        Finds the number of dependencies, dependant projects, and dependent repos by scrapping it off of the libraries.io website

        :param owner: GitHub username of the owner of the repo
        :param repo: Repository name
        :return: Dict that contains the results 
        """
        root_dir = self.__githubapi.get_repo((owner + "/" + repo)).get_dir_contents("/")

        platform = None

        for file in root_dir:
            if file.name == "Gemfile":
                platform = 'rubygems'
            if file.name == "package.json":
                platform = 'npm'
            if file.name == 'setup.py':
                platform = 'pypi'

        if platform == None:
            return {'Stats' : 'null'}

        url = "https://libraries.io/{platform}/{repo}/".format(platform=platform, repo=repo)

        resp = requests.get(url)

        if resp.status_code == 404:                
            return {'Stats' : 'null'}

        soup = BeautifulSoup(resp.text, "html.parser")

        infotable = soup.body.div.next_sibling.next_sibling.div.div.next_sibling.next_sibling.dl.next_sibling.next_sibling.next_sibling.next_sibling

        data =[]
        for child in infotable.children:
            if child.string == '\n':
                pass
            if child.string == None:
                if child.a != None:
                    data.append(child.a.string)
            else:
                data.append(child.string)
                
        data_new = []
        for item in data:
            data_new.append(item.strip('\n'))
        data_new = list(filter(None, data_new))

        data_new = dict(zip(*[iter(data_new)]*2))

        final_data = {'dependencies' : data_new['Dependencies'], 'dependent_projects' : data_new['Dependent projects'], 'dependent_repositories' : data_new['Dependent repositories']}

        return final_data

    @annotate(tag='dependents')
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
            print('You need to set the LibrariesIO API key in augur.cfg or the environment variable AUGUR_LIBRARIESIO_API_KEY')

        if projectsRequest.status_code != 200:
            return projectsRequest.json()
        else:
            project = projectsRequest.json()[0]['name']
            platform = projectsRequest.json()[0]['platform']
            dependentsUrl = "https://libraries.io/api/{platform}/{repo}/dependents".format(platform=platform, repo=repo)
            dependentsRequest = requests.get(dependentsUrl, params={"api_key": self.API_KEY})
            return dependentsRequest

    