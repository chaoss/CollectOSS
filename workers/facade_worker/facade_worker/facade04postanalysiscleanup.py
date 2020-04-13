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

def git_repo_cleanup(cfg):

# Clean up any git repos that are pending deletion

	cfg.update_status('Purging deleted repos')
	cfg.log_activity('Info','Processing deletions')

	query = "SELECT repo_id,repo_group_id,repo_path,repo_name FROM repo WHERE repo_status='Delete'"
	cfg.cursor.execute(query)

	delete_repos = list(cfg.cursor)

	for row in delete_repos:

		# Remove the files on disk

		cmd = ("rm -rf %s%s/%s%s"
			% (cfg.repo_base_directory,row[1],row[2],row[3]))

		return_code = subprocess.Popen([cmd],shell=True).wait()

		# Remove the analysis data

		remove_commits = "DELETE FROM commits WHERE repo_id=%s"
		cfg.cursor.execute(remove_commits, (row[0], ))

		optimize_table = "OPTIMIZE TABLE commits"
		cfg.cursor.execute(optimize_table)
		cfg.db.commit()

		# Remove cached repo data

		remove_dm_repo_weekly = "DELETE FROM dm_repo_weekly WHERE repo_id=%s"
		cfg.cursor.execute(remove_dm_repo_weekly, (row[0], ))
		cfg.db.commit()

		optimize_table = "OPTIMIZE TABLE dm_repo_weekly"
		cfg.cursor.execute(optimize_table)
		cfg.db.commit()

		remove_dm_repo_monthly = "DELETE FROM dm_repo_monthly WHERE repo_id=%s"
		cfg.cursor.execute(remove_dm_repo_monthly, (row[0], ))
		cfg.db.commit()

		optimize_table = "OPTIMIZE TABLE dm_repo_monthly"
		cfg.cursor.execute(optimize_table)
		cfg.db.commit()

		remove_dm_repo_annual = "DELETE FROM dm_repo_annual WHERE repo_id=%s"
		cfg.cursor.execute(remove_dm_repo_annual, (row[0], ))
		cfg.db.commit()

		optimize_table = "OPTIMIZE TABLE dm_repo_annual"
		cfg.cursor.execute(optimize_table)
		cfg.db.commit()

		# Set project to be recached if just removing a repo

		set_project_recache = ("UPDATE projects SET recache=TRUE "
			"WHERE id=%s")
		cfg.cursor.execute(set_project_recache,(row[1], ))
		cfg.db.commit()

		# Remove the entry from the repos table

		query = "DELETE FROM repo WHERE repo_id=%s"
		cfg.cursor.execute(query, (row[0], ))
		cfg.db.commit()

		log_activity('Verbose','Deleted repo %s' % row[0])

		cleanup = '%s/%s%s' % (row[1],row[2],row[3])

		# Remove any working commits

		remove_working_commits = "DELETE FROM working_commits WHERE repos_id=%s"
		cfg.cursor.execute(remove_working_commits, (row[0], ))
		cfg.db.commit()

		# Remove the repo from the logs

		remove_logs = ("DELETE FROM repos_fetch_log WHERE repos_id = %s")

		cfg.cursor.execute(remove_logs, (row[0], ))
		cfg.db.commit()

		optimize_table = "OPTIMIZE TABLE repos_fetch_log"
		cfg.cursor.execute(optimize_table)
		cfg.db.commit()

		# Attempt to cleanup any empty parent directories

		while (cleanup.find('/',0) > 0):
			cleanup = cleanup[:cleanup.rfind('/',0)]

			cmd = "rmdir %s%s" % (cfg.repo_base_directory,cleanup)
			subprocess.Popen([cmd],shell=True).wait()
			log_activity('Verbose','Attempted %s' % cmd)

		update_repo_log(row[0],'Deleted')

	# Clean up deleted projects

	get_deleted_projects = "SELECT repo_group_id FROM repo_groups WHERE rg_name='(Queued for removal)'"
	cfg.cursor.execute(get_deleted_projects)

	deleted_projects = list(cfg.cursor)

	for project in deleted_projects:

		# Remove cached data for projects which were marked for deletion

		clear_annual_cache = ("DELETE FROM dm_repo_group_annual WHERE "
			"repo_group_id=%s")
		cfg.cursor.execute(clear_annual_cache, (project[0], ))
		cfg.db.commit()

		optimize_table = "OPTIMIZE TABLE dm_repo_group_annual"
		cfg.cursor.execute(optimize_table)
		cfg.db.commit()

		clear_monthly_cache = ("DELETE FROM dm_repo_group_monthly WHERE "
			"repo_group_id=%s")
		cfg.cursor.execute(clear_monthly_cache, (project[0], ))
		cfg.db.commit()

		optimize_table = "OPTIMIZE TABLE dm_repo_group_monthly"
		cfg.cursor.execute(optimize_table)
		cfg.db.commit()

		clear_weekly_cache = ("DELETE FROM dm_repo_group_weekly WHERE "
			"repo_group_id=%s")
		cfg.cursor.execute(clear_weekly_cache, (project[0], ))
		cfg.db.commit()

		optimize_table = "OPTIMIZE TABLE dm_repo_group_weekly"
		cfg.cursor.execute(optimize_table)
		cfg.db.commit()

		clear_unknown_cache = ("DELETE FROM unknown_cache WHERE "
			"projects_id=%s")
		cfg.cursor.execute(clear_unknown_cache, (project[0], ))
		cfg.db.commit()

		optimize_table = "OPTIMIZE TABLE dm_repo_group_weekly"
		cfg.cursor.execute(optimize_table)
		cfg.db.commit()

		# Remove any projects which were also marked for deletion

		remove_project = "DELETE FROM repo_groups WHERE repo_group_id=%s"
		cfg.cursor.execute(remove_project, (project[0], ))
		cfg.db.commit()

	cfg.log_activity('Info','Processing deletions (complete)')