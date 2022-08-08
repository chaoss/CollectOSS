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
import traceback
import sys, platform, imp, time, datetime, html.parser, subprocess, os, getopt, xlsxwriter, configparser, logging
from multiprocessing import Process, Queue
from .facade01config import FacadeConfig as FacadeConfig#increment_db, update_db, migrate_database_config, database_connection, get_setting, update_status, log_activity          
from .facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author   
from .facade03analyzecommit import analyze_commit
from .facade04postanalysiscleanup import git_repo_cleanup
from .facade05repofetch import git_repo_initialize, check_for_repo_updates, force_repo_updates, force_repo_analysis, git_repo_updates
#from .facade06analyze import analysis moved to facade_tasks.py
from .facade07rebuildcache import nuke_affiliations, fill_empty_affiliations, invalidate_caches, rebuild_unknown_affiliation_and_web_caches

#from contributor_interfaceable.facade08contributorinterfaceable import ContributorInterfaceable

from augur.tasks.git.util.facade_worker.contributor_interfaceable.contributor_interface import *

from augur.tasks.github.util.github_task_session import GithubTaskSession

class FacadeSession(GithubTaskSession):
    def __init__(self,logger,platform='GitHub'):
        self.cfg = FacadeConfig(logger)

        super().__init__(logger=logger)
        # Figure out what we need to do

        self.limited_run = self.cfg.worker_options["limited_run"]
        self.delete_marked_repos = self.cfg.worker_options["delete_marked_repos"]
        self.pull_repos = self.cfg.worker_options["pull_repos"]
        self.clone_repos = self.cfg.worker_options["clone_repos"]
        self.check_updates = self.cfg.worker_options["check_updates"]
        self.force_updates = self.cfg.worker_options["force_updates"]
        self.run_analysis = self.cfg.worker_options["run_analysis"]
        self.force_analysis = self.cfg.worker_options["force_analysis"]
        self.nuke_stored_affiliations = self.cfg.worker_options["nuke_stored_affiliations"]
        self.fix_affiliations = self.cfg.worker_options["fix_affiliations"]
        self.force_invalidate_caches = self.cfg.worker_options["force_invalidate_caches"]
        self.rebuild_caches = self.cfg.worker_options["rebuild_caches"]
        self.multithreaded = self.cfg.worker_options["multithreaded"]
        self.create_xlsx_summary_files = self.cfg.worker_options["create_xlsx_summary_files"]

    def insert_or_update_data(self, query, params=None):

        attempts = 0
        sleep_time_list = [x for x in range(1,11)]
        deadlock_detected = False
        # if there is no data to return then it executes the insert the returns nothing

        while attempts < 10:
            try:
                if params:
                    self.cfg.cursor.execute(query, params)
                else:
                    self.cfg.cursor.execute(query)
                self.cfg.db.commit()
                break
            except OperationalError as e:
                # print(str(e).split("Process")[1].split(";")[0])
                if isinstance(e.orig, DeadlockDetected):
                    deadlock_detected = True
                    sleep_time = random.choice(sleep_time_list)
                    self.logger.debug(f"Deadlock detected on {table.__table__} table...trying again in {round(sleep_time)} seconds: transaction size: {len(data)}")
                    time.sleep(sleep_time)

                    attempts += 1
                    continue
                else:
                    raise OperationalError(f"An OperationalError other than DeadlockDetected occurred: {e}") 

        else:
            self.logger.error(f"Unable to insert data in 10 attempts")
            return

        if deadlock_detected == True:
            self.logger.error(f"Made it through even though Deadlock was detected")
                    
            return

        




html = html.parser.HTMLParser()

