#SPDX-License-Identifier: MIT
"""
Analyzes Git repos directly using git
"""

import os
import shutil
import re
import json
import datetime
import pandas as pd
import git
from lockfile import LockFile, AlreadyLocked
from augur.util import logger, get_cache, annotate

# end imports
# (don't remove the above line, it's for a script

class Repo:
    """
    Class to deal with the metadata surrounding a Git repository
    """
    def __init__(self, parent, repo_url):
        self.parent = parent
        self.url = repo_url
        self.folder_name = os.path.splitext(os.path.basename(repo_url))[0]
        self.containing_folder = os.path.join(parent.repo_folder, self.folder_name)
        if not os.path.exists(self.containing_folder):
            os.makedirs(self.containing_folder)
        self.path = os.path.join(self.containing_folder, 'repo')
        self.lockfile_path = os.path.join(self.containing_folder, 'lock')
        self.lock = LockFile(self.lockfile_path)
        self.json_path = os.path.join(self.containing_folder, 'metadata.json')
        self.data = {}
        if os.path.exists(self.json_path):
            with open(self.json_path) as json_file:
                self.data = json.load(json_file)
        self.__git = None

    def __enter__(self):
        """
        Update context
        """
        self.lock.acquire(timeout=0)
        logger.info('Git: Updating %s', self.url)
        if not os.path.exists(self.path):
            logger.debug('Cloning %s', self.url)
            git.Git(self.containing_folder).clone(self.url, self.path)
        else:
            try:
                repo = self.git(is_updater=True)
                logger.debug('Pulling %s', self.url)
                repo.git.pull()
            except Exception as e:
                logger.debug('Re-Cloning %s because %s', self.url, str(e))
                shutil.rmtree(self.path)
                git.Git(self.containing_folder).clone(self.url, self.path)
        return self

    def __exit__(self, type, value, traceback):
        # Save the updated time
        self.data['last_updated'] = str(datetime.datetime.utcnow())
        self.save()
        logger.info('Git: Update completed for %s', self.url)
        self.lock.break_lock()

    def save(self):
        with open(self.json_path, 'w') as f:
            json.dump(self.data, f)

    def git(self, is_updater=False):
        if self.lock.is_locked() and (not self.parent.is_updater and not is_updater):
            raise AlreadyLocked('This repository is being updated, if you can see this message delete {}'.format(self.lockfile_path))
        else:
            if self.__git is None or is_updater:
                self.__git = git.Repo(self.path)
            return self.__git


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
        self.folder = os.path.abspath(storage_folder)
        self.repo_folder = os.path.abspath(os.path.join(self.folder, 'repos'))
        self._csv = csv
        self.__cache = get_cache('augur-git', cache)
        self._repo_urls = list_of_repositories
        self._git_repos = {}
        if not os.path.exists(self.repo_folder):
            os.makedirs(self.repo_folder)
        self._log_location = os.path.join(self.folder, 'git_log.txt')
        self._log = open(self._log_location, 'wb')
        self.is_updater = False

    def get_repo(self, repo_url):
        """
        Create a repo object from the given url

        :param repo_url: URL of the repository
        :return: a Repo obeject
        """
        if repo_url in self._git_repos:
            return self._git_repos[repo_url]
        else:
            repo = Repo(self, repo_url)
            self._git_repos[repo_url] = repo
            return repo

    def update(self):
        """
        Makes sure the storage_folder contains updated versions of all the repos
        """
        lock = LockFile(os.path.join(self.repo_folder, 'update_lock'))
        with lock:
            self.is_updater = True
            for repo_url in self._repo_urls:
                try:
                    with self.get_repo(repo_url) as repo:           
                        logger.info('Git: Calculating metrics for %s', repo.url)    
                        # Do slow functions and rebuild their caches
                        self.lines_changed_minus_whitespace(repo.url, rebuild_cache=True)
                        self.changes_by_author(repo.url, rebuild_cache=True)
                except Exception as e:
                    logger.info('Git: Update failed for %s', repo.url)
                    logger.info('Git: Reason for failure: %s', str(e))
                    pass
                   
            self.is_updater = False

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

    @annotate(tag='downloaded-repos')
    def downloaded_repos(self):
        """
        Get all downloaded repositories and the date they were last updated
        :return: a JSON object with the URL and date of last update for all downloaded repos        
        """
        downloaded = []
        for repo_url in self._repo_urls:
            repo = self.get_repo(repo_url)
            updated = 'never'
            if repo.lock.is_locked():
                updated = 'now'
            else:
                if 'last_updated' in repo.data:
                    updated = repo.data['last_updated']
            downloaded.append({
                'url': repo_url,
                'updated': updated
            })

        return downloaded

    @annotate(tag='lines-changed-minus-whitespace')
    def lines_changed_minus_whitespace(self, repo_url, from_commit=None, df=None, rebuild_cache=False):
        """
        Makes sure the storageFolder contains updated versions of all the repos
        """
        def heavy_lifting():
            nonlocal df
            from_commit = None
            
            repo = self.get_repo(repo_url)
            git_repo = repo.git()
            
            frames = []
            if df is not None:
                frames.append(df)
                from_commit = df['hash'].iloc[-1]
            """
            Run a Git log command that returns each entry into 3 parts:
                1. JSON of the metadata
                2. Commit message
                3. Diffs
            """
            arg_array = ['-p', '-w', '-m', '--full-history', '--reverse', """--pretty=format:'[START ENTRY]%n{%n"hash":"%h",%n"author_name":"%an",%n"author_email":"%ae",%n"author_date":"%ai",%n"committer_name": "%cn",%n"committer_email":"%ce",%n"commit_date":"%ci",%n"parents":"%p"%n}%n#####SPLIT#####%s#####SPLIT#####'"""]
            if from_commit is not None:
                arg_array.append('{}..'.format(from_commit))
            history = git_repo.git.log(*arg_array)
            # Split the message into individual entries
            entries = history.split('[START ENTRY]')[1:]
            for entry in entries:
                splits = entry.split('#####SPLIT#####')
                try:
                    data = json.loads(splits[0])
                except json.JSONDecodeError as err:
                    continue
                data['message'] = splits[1]
                if (len(splits[2]) > 2):
                    diffs = splits[2].split('diff --git')
                    for diff in diffs[1:]:
                        if '+' in diff:
                            file_search = re.search('b(\/.+)', diff)
                            if file_search is not None:
                                filename = file_search.group(1)
                                # Find all the lines that begin with a plus or minus to count added
                                # Minus one to account the file matches
                                additions = len(re.findall('\n\+[ \t]*[^\s]', diff)) - 1
                                deletions = len(re.findall('\n-[ \t]*[^\s]', diff)) - 1
                                data['additions'] = additions
                                data['deletions'] = deletions
                                frames.append(pd.DataFrame(data, index=['hash']))

            
            if len(frames):
                df = pd.concat(frames)
            df['author_affiliation'] = self._csv.classify_emails(df['author_email'])
            df['committer_affiliation'] = self._csv.classify_emails(df['committer_email'])
            return df
        
        results = self.__cache.get(key='lc-{}'.format(repo_url), createfunc=heavy_lifting)
        if rebuild_cache:
            self.__cache.remove_value(key='lc-{}'.format(repo_url))
            new_results = self.lines_changed_minus_whitespace(repo_url, df=results, rebuild_cache=False)
            if len(new_results) > len(results):
                logger.info('Git: Added commits from %s to %s', results['hash'].iloc[-1], new_results['hash'].iloc[-1])
            results = new_results
        return results

    @annotate(tag='lines-changed-by-author')
    def lines_changed_by_author(self, repo_url, freq='M', rebuild_cache=False):
        """
        Makes sure the storageFolder contains updated versions of all the repos
        """
        def heavy_lifting():
            df = self.lines_changed_minus_whitespace(repo_url)
            df['author_date'] = pd.to_datetime(df['author_date'])
            df = df.set_index('author_date')
            df = df.groupby(['author_email', 'author_name', pd.Grouper(freq=freq)]).sum().sort_values(by=['additions'], ascending=False)
            df['affiliation'] = self._csv.classify_emails(df.index.get_level_values('author_email'))
            df.reset_index(inplace=True)
            return df
        if rebuild_cache:
            self.__cache.remove_value(key='cba-{}-{}'.format(freq, repo_url))
        results = self.__cache.get(key='cba-{}-{}'.format(freq, repo_url), createfunc=heavy_lifting)
        return result5
