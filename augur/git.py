#SPDX-License-Identifier: MIT
"""
Analyzes Git repos directly using dulwich
"""

import os
import shutil
import re
import json
import pandas as pd
import git
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
                self.__repos[repo_url] = git.Repo(repo_path)
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
                    git.Git(self.__folder).clone(repo_url, repo_path)
                    repo = git.Repo(repo_path)
                    self.__repos[repo_url] = repo
                else:
                    try:
                        repo = git.Repo(repo_path)
                        logger.debug('Pulling %s', repo_url)
                        repo.git.pull()
                    except Exception as e:
                        logger.debug('Re-Cloning %s because %s', repo_url, str(e))
                        shutil.rmtree(repo_path)
                        git.Git(self.__folder).clone(repo_url)
                        repo = git.Repo(repo_path)
                    self.__repos[repo_url] = repo
            lockfile.close()
            os.remove(lockfile_path)

    def lines_changed_minus_whitespace(self, repo_url):
        """
        Makes sure the storageFolder contains updated versions of all the repos
        """
        repo = self.get_repo_object(repo_url)
        df = pd.DataFrame()
        history = repo.git.log('--ignore-space-at-eol', '--ignore-blank-lines', '-b', '-p', '-U0', """--pretty=format:'[START ENTRY]%n{%n"hash":"%h",%n"author_name":"%an",%n"author_email":"%ae",%n"author_date":"%ai",%n"committer_name": "%cn",%n"committer_email":"%ce",%n"commit_date":"%ci",%n"parents":"%p"%n}%n#####SPLIT#####%s#####SPLIT#####'""")
        frames = []
        for entry in history.split('[START ENTRY]')[1:]:
            splits = entry.split('#####SPLIT#####')
            try:
                data = json.loads(splits[0])
            except json.JSONDecodeError as err:
                print(err)
                print(splits[0])
                continue
            data['message'] = splits[1]
            if (len(splits[2]) > 2):
                diffs = splits[2].split('diff --git')
                for diff in diffs[1:]:
                    filename = re.search('b(\/.+)', diff).group(1)
                    # Find all the lines that begin with a plus or minus to count added
                    additions = len(re.findall('\n\+[^\+\n]', diff))
                    deletions = len(re.findall('\n-[^-\n]', diff))
                    data['additions'] = additions
                    data['deletions'] = deletions
                    frames.append(pd.DataFrame(data, index=['hash']))
        df = pd.concat(frames)
        return df