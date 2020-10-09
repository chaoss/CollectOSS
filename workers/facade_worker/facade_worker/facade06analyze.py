#!/usr/bin/env python3

# Copyright 2016-2018 Brian Warner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier:  Apache-2.0

# Git repo maintenance
#
# This script is responsible for cloning new repos and keeping existing repos up
# to date. It can be run as often as you want (and will detect when it's
# already running, so as not to spawn parallel processes), but once or twice per
# day should be more than sufficient. Each time it runs, it updates the repo
# and checks for any parents of HEAD that aren't already accounted for in the
# repos. It also rebuilds analysis data, checks any changed affiliations and
# aliases, and caches data for display.
import sys
import platform
import imp
import time
import datetime
import html.parser
import subprocess
import os
import getopt
import xlsxwriter
import configparser
from facade_worker.facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author
from facade_worker.facade03analyzecommit import analyze_commit

# if platform.python_implementation() == 'PyPy':
#   import pymysql
# else:
#   import MySQLdb

def analysis(cfg, multithreaded):

# Run the analysis by looping over all active repos. For each repo, we retrieve
# the list of commits which lead to HEAD. If any are missing from the database,
# they are filled in. Then we check to see if any commits in the database are
# not in the list of parents, and prune them out.
#
# We also keep track of the last commit to be processed, so that if the analysis
# is interrupted (possibly leading to partial data in the database for the
# commit being analyzed at the time) we can recover.

### Local helper functions ###

    def update_analysis_log(repos_id,status):

    # Log a repo's analysis status

        log_message = ("INSERT INTO analysis_log (repos_id,status) "
            "VALUES (%s,%s)")

        try:
            cfg.cursor.execute(log_message, (repos_id,status))
            cfg.db.commit()
        except:
            pass

### The real function starts here ###

    cfg.update_status('Running analysis')
    cfg.log_activity('Info','Beginning analysis')

    start_date = cfg.get_setting('start_date')

    repo_list = "SELECT repo_id,repo_group_id,repo_path,repo_name FROM repo WHERE repo_status='Analyze'"
    cfg.cursor.execute(repo_list)
    repos = list(cfg.cursor)


    for repo in repos:
        update_analysis_log(repo[0],'Beginning analysis')
        cfg.log_activity('Verbose','Analyzing repo: %s (%s)' % (repo[0],repo[3]))

        cfg.inc_repos_processed()

        # First we check to see if the previous analysis didn't complete

        get_status = ("SELECT working_commit FROM working_commits WHERE repos_id=%s")

        cfg.cursor.execute(get_status, (repo[0], ))
        working_commits = list(cfg.cursor)
        #cfg.cursor.fetchone()[1]

        # If there's a commit still there, the previous run was interrupted and
        # the commit data may be incomplete. It should be trimmed, just in case.
        for commit in working_commits:
            trim_commit(cfg, repo[0],commit[0])

            # Remove the working commit.
            remove_commit = ("DELETE FROM working_commits "
                "WHERE repos_id = %s AND working_commit = %s")
            cfg.cursor.execute(remove_commit, (repo[0],commit[0]))
            cfg.db.commit()

            cfg.log_activity('Debug','Removed working commit: %s' % commit[0])

        # Start the main analysis

        update_analysis_log(repo[0],'Collecting data')

        repo_loc = ('%s%s/%s%s/.git' % (cfg.repo_base_directory,
            repo[1], repo[2],
            repo[3]))
        # Grab the parents of HEAD

        parents = subprocess.Popen(["git --git-dir %s log --ignore-missing "
            "--pretty=format:'%%H' --since=%s" % (repo_loc,start_date)],
            stdout=subprocess.PIPE, shell=True)

        parent_commits = set(parents.stdout.read().decode("utf-8",errors="ignore").split(os.linesep))

        # If there are no commits in the range, we still get a blank entry in
        # the set. Remove it, as it messes with the calculations

        if '' in parent_commits:
            parent_commits.remove('')

        # Grab the existing commits from the database

        existing_commits = set()

        find_existing = ("SELECT DISTINCT cmt_commit_hash FROM commits WHERE repo_id=%s")

        cfg.cursor.execute(find_existing, (repo[0], ))

        for commit in list(cfg.cursor):
            existing_commits.add(commit[0])

        # Find missing commits and add them

        missing_commits = parent_commits - existing_commits

        cfg.log_activity('Debug','Commits missing from repo %s: %s' %
            (repo[0],len(missing_commits)))

## TODO: Verify if the multithreaded approach here is optimal for postgresql

        if multithreaded:

            from multiprocessing import Pool

            pool = Pool()

            for commit in missing_commits:

                result = pool.apply_async(analyze_commit(cfg, repo[0], repo_loc, commit, multithreaded))

            pool.close()
            pool.join()

        else:
            for commit in missing_commits:
                analyze_commit(cfg, repo[0], repo_loc, commit, multithreaded)

        update_analysis_log(repo[0],'Data collection complete')

        update_analysis_log(repo[0],'Beginning to trim commits')

        # Find commits which are out of the analysis range

        trimmed_commits = existing_commits - parent_commits

        cfg.log_activity('Debug','Commits to be trimmed from repo %s: %s' %
            (repo[0],len(trimmed_commits)))

        for commit in trimmed_commits:

            trim_commit(cfg, repo[0],commit)

        set_complete = "UPDATE repo SET repo_status='Complete' WHERE repo_id=%s and repo_status != 'Empty'"
        try:
            cfg.cursor.execute(set_complete, (repo[0], ))
        except:
            pass

        update_analysis_log(repo[0],'Commit trimming complete')

        update_analysis_log(repo[0],'Complete')

    cfg.log_activity('Info','Running analysis (complete)')

