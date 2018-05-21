#SPDX-License-Identifier: MIT
"""
Analyzes Git repos directly using dulwich
"""

import os
import shutil

import pandas as pd
from dulwich.repo import Repo
from dulwich import porcelain as git
from augur import logger

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
        if not os.path.exists(self.__folder):
            os.makedirs(self.__folder)
        self.__log_location = os.path.join(self.__folder, 'git_log.txt')
        self.__log = open(self.__log_location, 'wb')
        self.sync()

    def get_repo_object(self, repo_url):
        """
        Returns a repo object given a string

        :param listOfRepositories: List of URLs to Git repos to analyze
        :param storageFolder: Folder to download the repositories to
        """
        if repo_url in self.__repos:
            return self.__repos[repo_url]
        else:
            try:
                folder_name = os.path.splitext(os.path.basename(repo_url))[0]
                repo_path = os.path.join(self.__folder, folder_name)
                self.__repos[repo_url] = Repo(repo_path)
                return self.__repos[repo_url]
            except:
                raise ValueError("{} is not in the list_of_repositories".format(repo_url))

    def sync(self):
        """
        Makes sure the storage_folder contains updated versions of all the repos
        """
        lockfile_path = os.path.join(self.__folder, 'lock')
        if not os.path.exists(lockfile_path):
            lockfile = open(lockfile_path, 'w')
            for repo_url in self.__repo_urls:
                logger.info('Git: Updating %s', repo_url)
                folder_name = os.path.splitext(os.path.basename(repo_url))[0]
                repo_path = os.path.join(self.__folder, folder_name)
                if not os.path.exists(repo_path):
                    logger.debug('Cloning %s', repo_url)
                    git.clone(repo_url, repo_path, outstream=self.__log, errstream=self.__log)
                repo = Repo(repo_path)
                try:
                    logger.debug('Pulling %s', repo_url)
                    git.pull(repo, remote_location=repo_url, outstream=self.__log, errstream=self.__log)
                except Exception as e:
                    logger.debug('Re-Cloning %s because %s', repo_url, str(e))
                    shutil.rmtree(repo_path)
                    git.clone(repo_url, repo_path, outstream=self.__log, errstream=self.__log)
                    repo = Repo(repo_path)
                self.__repos[repo_url] = repo
            lockfile.close()
            os.remove(lockfile_path)

    def lines_changed_minus_whitespace(self, repo_url):
        """
        Makes sure the storageFolder contains updated versions of all the repos
        """
        repo = self.get_repo_object(repo_url)
        return repo
