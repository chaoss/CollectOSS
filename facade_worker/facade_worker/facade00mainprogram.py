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
from .facade01config import Config as FacadeConfig#increment_db, update_db, migrate_database_config, database_connection, get_setting, update_status, log_activity          
from .facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author   
from .facade03analyzecommit import analyze_commit
from .facade04postanalysiscleanup import git_repo_cleanup
from .facade05repofetch import git_repo_initialize, check_for_repo_updates, force_repo_updates, force_repo_analysis, git_repo_updates
#from .facade06analyze import analysis moved to facade_tasks.py
from .facade07rebuildcache import nuke_affiliations, fill_empty_affiliations, invalidate_caches, rebuild_unknown_affiliation_and_web_caches

#from contributor_interfaceable.facade08contributorinterfaceable import ContributorInterfaceable

from facade_worker.contributor_interfaceable.contributor_interface import *

from util.worker_util import read_config
from tasks.task_session import GithubTaskSession

class FacadeSession(GithubTaskSession):
    def __init__(self,logger,config={},platform='GitHub'):
        self.cfg = FacadeConfig(logger)

        super().__init__(logger,config,platform)
        # Figure out what we need to do
        self.limited_run = self.augur_config.get_value("Facade", "limited_run")
        self.delete_marked_repos = self.augur_config.get_value("Facade", "delete_marked_repos")
        self.pull_repos = self.augur_config.get_value("Facade", "pull_repos")
        self.clone_repos = self.augur_config.get_value("Facade", "clone_repos")
        self.check_updates = self.augur_config.get_value("Facade", "check_updates")
        self.force_updates = self.augur_config.get_value("Facade", "force_updates")
        self.run_analysis = self.augur_config.get_value("Facade", "run_analysis")
        self.force_analysis = self.augur_config.get_value("Facade", "force_analysis")
        self.nuke_stored_affiliations = self.augur_config.get_value("Facade", "nuke_stored_affiliations")
        self.fix_affiliations = self.augur_config.get_value("Facade", "fix_affiliations")
        self.force_invalidate_caches = self.augur_config.get_value("Facade", "force_invalidate_caches")
        self.rebuild_caches = self.augur_config.get_value("Facade", "rebuild_caches")
        self.multithreaded = self.augur_config.get_value("Facade", "multithreaded")
        self.create_xlsx_summary_files = self.augur_config.get_value("Facade", "create_xlsx_summary_files")




html = html.parser.HTMLParser()

