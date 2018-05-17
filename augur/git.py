#SPDX-License-Identifier: MIT
"""
Analyzes Git repos directly using dulwich
"""

import os
import shutil

import pandas as pd
from dulwich.repo import Repo
from dulwich import porcelain as git

# end imports
# (don't remove the above line, it's for a script)

class Git(object):
    """
    Analyzes Git repos directly using dulwich
    """
    def __init__(self, list_of_repositories, storage_folder):
        """
        Creates a new GitHub instance

        :param listOfRepositories: List of URLs to Git repos to analyze
        :param storageFolder: Folder to download the repositories to
        """
        self.__repo_urls = list_of_repositories
        self.__repos = {}
        self.__folder = os.path.abspath(storage_folder)
        self.sync()

    def get_repo_object(self, repo_url):
        """
        Returns a repo object given a string

        :param listOfRepositories: List of URLs to Git repos to analyze
        :param storageFolder: Folder to download the repositories to
        """
        if hasattr(self.__repos, repo_url):
            return self.__repos[repo_url]
        else:
            raise ValueError("{} is not in the list_of_repositories".format(repo_url))

    def sync(self):
        """
        Makes sure the storage_folder contains updated versions of all the repos
        """
        for repo_url in self.__repo_urls:
            folder_name = os.path.splitext(os.path.basename(repo_url))[0]
            repo_path = os.path.join(self.__folder, folder_name)
            if not os.path.exists(repo_path):
                git.clone(repo_url, repo_path)
            repo = Repo(repo_path)
            try:
                git.pull(repo)
            except:
                shutil.rmtree(repo_path)
                git.clone(repo_url, repo_path)
                repo = Repo(repo_path)
            self.__repos[repo_url] = repo

    def lines_changed_minus_whitespace(self):
        """
        Makes sure the storageFolder contains updated versions of all the repos
        """
        return []
