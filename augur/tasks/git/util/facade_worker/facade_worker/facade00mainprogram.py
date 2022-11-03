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
from __future__ import annotations
import traceback
import sys, platform, imp, time, datetime, html.parser, subprocess, os, getopt, xlsxwriter, configparser, logging
from multiprocessing import Process, Queue
from .facade01config import FacadeSession as FacadeSession#increment_db, update_db, migrate_database_config, database_connection, get_setting, update_status, log_activity          
from .facade02utilitymethods import trim_commit, store_working_author, trim_author   
from .facade03analyzecommit import analyze_commit
from .facade04postanalysiscleanup import git_repo_cleanup
from .facade05repofetch import git_repo_initialize, check_for_repo_updates, force_repo_updates, force_repo_analysis, git_repo_updates
#.facade06analyze analysis moved to facade_tasks.py - IM 10/12/22
from .facade07rebuildcache import nuke_affiliations, fill_empty_affiliations, invalidate_caches, rebuild_unknown_affiliation_and_web_caches

#from contributor_interfaceable.facade08contributorinterfaceable import ContributorInterfaceable

from augur.tasks.github.facade_github.contributor_interfaceable.contributor_interface import *

from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.init.celery_app import engine
from logging import Logger
from sqlalchemy.sql.elements import TextClause



html = html.parser.HTMLParser()

