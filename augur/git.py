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
    def __init__(self, list_of_repositories, storage_folder, csv, cache=None):
        """
        Creates a new GitHub instance

        :param listOfRepositories: List of URLs to Git repos to analyze
        :param storageFolder: Folder to download the repositories to
        """
        self._csv = csv
        self.__cache = cache
        self._repo_urls = list_of_repositories
        self._repos = {}
        self._folder = os.path.abspath(storage_folder)
        self._repo_folder = os.path.abspath(os.path.join(self._folder, 'repos'))
        if not os.path.exists(self._repo_folder):
            os.makedirs(self._repo_folder)
        self._log_location = os.path.join(self._folder, 'git_log.txt')
        self._log = open(self._log_location, 'wb')
        self.downloaded_repos()


    def get_repo_object(self, repo_url):
        """
        Returns a repo object given a string

        :param listOfRepositories: List of URLs to Git repos to analyze
        :param storageFolder: Folder to download the repositories to
        """
        if repo_url in self._repos:
            return self._repos[repo_url]
        else:
            try:
                folder_name = os.path.splitext(os.path.basename(repo_url))[0]
                repo_path = os.path.join(self._repo_folder, folder_name)
                self._repos[repo_url] = git.Repo(repo_path)
                return self._repos[repo_url]
            except:
                raise ValueError("{} is not in the list_of_repositories".format(repo_url))

    def update(self):
        """
        Makes sure the storage_folder contains updated versions of all the repos
        """
        for repo_url in self._repo_urls:
            logger.info('Git: Updating %s', repo_url)
            folder_name = os.path.splitext(os.path.basename(repo_url))[0]
            repo_path = os.path.join(self._repo_folder, folder_name)
            if not os.path.exists(repo_path):
                logger.debug('Cloning %s', repo_url)
                git.Git(self._repo_folder).clone(repo_url, repo_path)
                repo = git.Repo(repo_path)
                self._repos[repo_url] = repo
            else:
                try:
                    repo = git.Repo(repo_path)
                    logger.debug('Pulling %s', repo_url)
                    repo.git.pull()
                except Exception as e:
                    logger.debug('Re-Cloning %s because %s', repo_url, str(e))
                    shutil.rmtree(repo_path)
                    git.Git(self._repo_folder).clone(repo_url)
                    repo = git.Repo(repo_path)
                self._repos[repo_url] = repo
            logger.info('Git: Update completed for %s', repo_url)

    def downloaded_repos(self):
        urls = []
        for entry in os.scandir(self._folder):
            if entry.is_dir():
                try:
                    repo = git.Repo(os.path.join(self._folder, entry.name))
                    repo_url = repo.remotes.origin.url
                    urls.append(repo_url)
                    if not repo_url in self._repos:
                        self._repos[repo_url] = repo
                except:
                    continue
        return urls


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

    def changes_by_author(self, repo_url):
        """
        Makes sure the storageFolder contains updated versions of all the repos
        """
        df = self.lines_changed_minus_whitespace(repo_url)
        df = df.groupby(['author_email', 'author_name']).sum().sort_values(by=['additions'], ascending=False)
        df['affiliation'] = self._csv.classify_emails(df.index.get_level_values('author_email'))
        df.reset_index(inplace=True)
        return df