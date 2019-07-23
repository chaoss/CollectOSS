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
# SPDX-License-Identifier:	Apache-2.0

# Git repo maintenance
#
# This script is responsible for cloning new repos and keeping existing repos up
# to date. It can be run as often as you want (and will detect when it's
# already running, so as not to spawn parallel processes), but once or twice per
# day should be more than sufficient. Each time it runs, it updates the repo
# and checks for any parents of HEAD that aren't already accounted for in the
# repos. It also rebuilds analysis data, checks any changed affiliations and
# aliases, and caches data for display.

import pymysql
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

from facade_worker.facade01config import Config#increment_db, update_db, migrate_database_config, database_connection, get_setting, update_status, log_activity          
from facade_worker.facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author   
from facade_worker.facade03analyzecommit import analyze_commit
from facade_worker.facade04postanalysiscleanup import git_repo_cleanup
from facade_worker.facade05repofetch import git_repo_initialize, check_for_repo_updates, force_repo_updates, force_repo_analysis, git_repo_updates
from facade_worker.facade06analyze import analysis
from facade_worker.facade07rebuildcache import nuke_affiliations, fill_empty_affiliations, invalidate_caches, rebuild_unknown_affiliation_and_web_caches
# if platform.python_implementation() == 'PyPy':
# 	import pymysql
# else:
# 	import MySQLdb
# ## End Imports

html = html.parser.HTMLParser()

class FacadeWorker:
	def __init__(self, config, task=None):
		self.cfg = Config()
		

		### The real program starts here ###

		# Set up the database
		json = self.cfg.read_config("Database", use_main_config=0)#self.cfg.migrate_database_config("Credentials")
		db_user = json['user']
		db_pass = json['password']
		db_name = json['database']
		db_host = json['host']
		db_user_people = json['user']
		db_pass_people = json['password']
		db_name_people = json['database']
		db_host_people = json['host']

		# Open a general-purpose connection
		db,cursor = self.cfg.database_connection(
			db_host,
			db_user,
			db_pass,
			db_name, False, False)

		# Open a connection for the people database
		db_people,cursor_people = self.cfg.database_connection(
			db_host_people,
			db_user_people,
			db_pass_people,
			db_name_people, True, False)

		# Check if the database is current and update it if necessary
		try:
			current_db = int(self.cfg.get_setting('database_version'))
		except:
			# Catch databases which existed before database versioning
			current_db = -1

		#WHAT IS THE UPSTREAM_DB???
		# if current_db < upstream_db:

		# 	print(("Current database version: %s\nUpstream database version %s\n" %
		# 		(current_db, upstream_db)))

		# 	self.cfg.update_db(current_db);

		# Figure out what we need to do
		limited_run = 0
		delete_marked_repos = 0
		pull_repos = 0
		clone_repos = 0
		check_updates = 0
		force_updates = 0
		run_analysis = 0
		force_analysis = 0
		nuke_stored_affiliations = 0
		fix_affiliations = 1
		force_invalidate_caches = 0
		rebuild_caches = 1 #if abs((datetime.datetime.strptime(self.cfg.get_setting('aliases_processed')[:-3], 
			# '%Y-%m-%d %I:%M:%S.%f') - datetime.datetime.now()).total_seconds()) // 3600 > int(self.cfg.get_setting(
			# 	'update_frequency')) else 0
		force_invalidate_caches = 0
		create_xlsx_summary_files = 0
		multithreaded = 1

		opts,args = getopt.getopt(sys.argv[1:],'hdpcuUaAmnfIrx')
		for opt in opts:
			if opt[0] == '-h':
				print("\nfacade-worker.py does everything by default except invalidating caches\n"
						"and forcing updates, unless invoked with one of the following options.\n"
						"In those cases, it will only do what you have selected.\n\n"
						"Options:\n"
						"	-d	Delete marked repos\n"
						"	-c	Run 'git clone' on new repos\n"
						"	-u	Check if any repos should be marked for updating\n"
						"	-U	Force all repos to be marked for updating\n"
						"	-p	Run 'git pull' on repos\n"
						"	-a	Analyze git repos\n"
						"	-A	Force all repos to be analyzed\n"
						"	-m	Disable multithreaded mode (but why?)\n"
						"	-n	Nuke stored affiliations (if mappings modified by hand)\n"
						"	-f	Fill empty affiliations\n"
						"	-I	Invalidate caches\n"
						"	-r	Rebuild unknown affiliation and web caches\n"
						"	-x	Create Excel summary files\n\n")
				sys.exit(0)

			elif opt[0] == '-d':
				delete_marked_repos = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: delete marked repos.')

			elif opt[0] == '-c':
				clone_repos = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: clone new repos.')

			elif opt[0] == '-u':
				check_updates = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: checking for repo updates')

			elif opt[0] == '-U':
				force_updates = 1
				self.cfg.log_activity('Info','Option set: forcing repo updates')

			elif opt[0] == '-p':
				pull_repos = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: update repos.')

			elif opt[0] == '-a':
				run_analysis = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: running analysis.')

			elif opt[0] == '-A':
				force_analysis = 1
				run_analysis = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: forcing analysis.')

			elif opt[0] == '-m':
				multithreaded = 0
				self.cfg.log_activity('Info','Option set: disabling multithreading.')

			elif opt[0] == '-n':
				nuke_stored_affiliations = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: nuking all affiliations')

			elif opt[0] == '-f':
				fix_affiliations = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: fixing affiliations.')

			elif opt[0] == '-I':
				force_invalidate_caches = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: Invalidate caches.')

			elif opt[0] == '-r':
				rebuild_caches = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: rebuilding caches.')

			elif opt[0] == '-x':
				create_xlsx_summary_files = 1
				limited_run = 1
				self.cfg.log_activity('Info','Option set: creating Excel summary files.')

		# Get the location of the directory where git repos are stored
		repo_base_directory = self.cfg.repo_base_directory

		# Determine if it's safe to start the script
		current_status = self.cfg.get_setting('utility_status')

		if current_status != 'Idle':
			self.cfg.log_activity('Error','Something is already running, aborting maintenance '
				'and analysis.\nIt is unsafe to continue.')
			# sys.exit(1)

		if len(repo_base_directory) == 0:
			self.cfg.log_activity('Error','No base directory. It is unsafe to continue.')
			update_status('Failed: No base directory')
			sys.exit(1)

		# Begin working

		start_time = time.time()
		self.cfg.log_activity('Quiet','Running facade-worker.py')

		if not limited_run or (limited_run and delete_marked_repos):
			git_repo_cleanup(self.cfg)

		if not limited_run or (limited_run and clone_repos):
			git_repo_initialize(self.cfg)

		if not limited_run or (limited_run and check_updates):
			check_for_repo_updates(self.cfg)

		if force_updates:
			force_repo_updates(self.cfg)

		if not limited_run or (limited_run and pull_repos):
			git_repo_updates(self.cfg)

		if force_analysis:
			force_repo_analysis(self.cfg)

		if not limited_run or (limited_run and run_analysis):
			analysis(self.cfg, multithreaded)

		if nuke_stored_affiliations:
			nuke_affiliations(self.cfg)

		if not limited_run or (limited_run and fix_affiliations):
			fill_empty_affiliations(self.cfg)

		if force_invalidate_caches:
			invalidate_caches(self.cfg)

		if not limited_run or (limited_run and rebuild_caches):
			rebuild_unknown_affiliation_and_web_caches(self.cfg)

		if not limited_run or (limited_run and create_xlsx_summary_files):

			self.cfg.log_activity('Info','Creating summary Excel files')

			# from excel_generators import *

			self.cfg.log_activity('Info','Creating summary Excel files (complete)')



		# All done

		self.cfg.update_status('Idle')
		self.cfg.log_activity('Quiet','facade-worker.py completed')

		elapsed_time = time.time() - start_time

		print('\nCompleted in %s\n' % datetime.timedelta(seconds=int(elapsed_time)))

		self.cfg.cursor.close()
		self.cfg.cursor_people.close()
		self.cfg.db.close()
		self.cfg.db_people.close()
