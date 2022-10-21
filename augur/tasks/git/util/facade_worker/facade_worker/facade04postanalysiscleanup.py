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
import sqlalchemy as s

def git_repo_cleanup(session):

# Clean up any git repos that are pending deletion

	session.update_status('Purging deleted repos')
	#session.logger.info("Processing deletions")
	session.log_activity('Info','Processing deletions')


	query = s.sql.text("""SELECT repo_id,repo_group_id,repo_path,repo_name FROM repo WHERE repo_status='Delete'""")

	delete_repos = session.fetchall_data_from_sql_text(query)

	for row in delete_repos:

		# Remove the files on disk

		cmd = ("rm -rf %s%s/%s%s"
			% (session.repo_base_directory,row['repo_group_id'],row['repo_path'],row['repo_name']))

		return_code = subprocess.Popen([cmd],shell=True).wait()

		# Remove the analysis data

		remove_commits = s.sql.text("""DELETE FROM commits WHERE repo_id=:repo_id
			""").bindparams(repo_id=row['repo_id'])
		session.execute_sql(remove_commits) 

		optimize_table = s.sql.text("""OPTIMIZE TABLE commits""")
		session.execute_sql(optimize_table)

		# Remove cached repo data

		remove_dm_repo_weekly = s.sql.text("""DELETE FROM dm_repo_weekly WHERE repo_id=:repo_id
			""").bindparams(repo_id=row['repo_id'])
		session.execute_sql(remove_dm_repo_weekly)

		optimize_table = s.sql.text("""OPTIMIZE TABLE dm_repo_weekly""")
		session.execute_sql(optimize_table)

		remove_dm_repo_monthly = s.sql.text("""DELETE FROM dm_repo_monthly WHERE repo_id=:repo_id
			""").bindparams(repo_id=row['repo_id'])
		session.execute_sql(remove_dm_repo_monthly)

		optimize_table = s.sql.text("""OPTIMIZE TABLE dm_repo_monthly""")
		session.execute_sql(optimize_table)

		remove_dm_repo_annual = s.sql.text("""DELETE FROM dm_repo_annual WHERE repo_id=:repo_id
			""").bindparams(repo_id=row['repo_id'])
		session.execute_sql(remove_dm_repo_annual)

		optimize_table = s.sql.text("""OPTIMIZE TABLE dm_repo_annual""")
		session.execute_sql(optimize_table)

		# Set project to be recached if just removing a repo

		set_project_recache = s.sql.text("""UPDATE projects SET recache=TRUE
			WHERE id=:repo_group_id""").bindparams(repo_group_id=row['repo_group_id'])
		session.execute_sql(set_project_recache)
		# Remove the entry from the repos table

		query = s.sql.text("""DELETE FROM repo WHERE repo_id=:repo_id
			""").bindparams(repo_id=row['repo_id'])
		session.execute_sql(query)

		#log_activity('Verbose','Deleted repo %s' % row[0])
		#session.logger.debug(f"Deleted repo {row['repo_id']}")
		session.log_activity('Verbose',f"Deleted repo {row['repo_id']}")
		cleanup = '%s/%s%s' % (row['repo_group_id'],row['repo_path'],row['repo_name'])

		# Remove any working commits

		remove_working_commits = s.sql.text("""DELETE FROM working_commits WHERE repos_id=:repo_id
			""").bindparams(repo_id=row['repo_id'])
		session.execute_sql(remove_working_commits)

		# Remove the repo from the logs

		remove_logs = s.sql.text("""DELETE FROM repos_fetch_log WHERE repos_id =:repo_id
			""").bindparams(repo_id=row['repo_id'])

		session.execute_sql(remove_logs)

		optimize_table = s.sql.text("""OPTIMIZE TABLE repos_fetch_log""")
		session.execute_sql(optimize_table)

		# Attempt to cleanup any empty parent directories

		while (cleanup.find('/',0) > 0):
			cleanup = cleanup[:cleanup.rfind('/',0)]

			cmd = "rmdir %s%s" % (session.repo_base_directory,cleanup)
			subprocess.Popen([cmd],shell=True).wait()
			#log_activity('Verbose','Attempted %s' % cmd)
			#session.logger.debug(f"Attempted {cmd}")
			session.log_activity('Verbose',f"Attempted {cmd}")

		#update_repo_log(row[0],'Deleted')
		session.update_repo_log(row['repo_id'],'Deleted')

	# Clean up deleted projects

	get_deleted_projects = s.sql.text("""SELECT repo_group_id FROM repo_groups WHERE rg_name='(Queued for removal)'""")

	deleted_projects = session.fetchall_data_from_sql_text(get_deleted_projects)

	for project in deleted_projects:

		# Remove cached data for projects which were marked for deletion

		clear_annual_cache = s.sql.text("""DELETE FROM dm_repo_group_annual WHERE
			repo_group_id=:repo_group_id""").bindparams(repo_group_id=project['repo_group_id'])
		session.execute_sql(clear_annual_cache)

		optimize_table = s.sql.text("""OPTIMIZE TABLE dm_repo_group_annual""")
		session.execute_sql(optimize_table)

		clear_monthly_cache = s.sql.text("""DELETE FROM dm_repo_group_monthly WHERE
			repo_group_id=:repo_group_id""").bindparams(repo_group_id=project['repo_group_id'])
		session.execute_sql(clear_monthly_cache)

		optimize_table = s.sql.text("""OPTIMIZE TABLE dm_repo_group_monthly""")
		session.execute_sql(optimize_table)

		clear_weekly_cache = s.sql.text("""DELETE FROM dm_repo_group_weekly WHERE
			repo_group_id=:repo_group_id""").bindparams(repo_group_id=project['repo_group_id'])
		session.execute_sql(clear_weekly_cache)

		optimize_table = s.sql.text("""OPTIMIZE TABLE dm_repo_group_weekly""")
		session.execute_sql(optimize_table)

		clear_unknown_cache = s.sql.text("""DELETE FROM unknown_cache WHERE
			projects_id=:repo_group_id""").bindparams(repo_group_id=project['repo_group_id'])
		session.execute_sql(clear_unknown_cache)

		optimize_table = s.sql.text("""OPTIMIZE TABLE dm_repo_group_weekly""")
		session.execute_sql(optimize_table)

		# Remove any projects which were also marked for deletion

		remove_project = s.sql.text("""DELETE FROM repo_groups WHERE repo_group_id=:repo_group_id
			""").bindparams(repo_group_id=project['repo_group_id'])
		session.execute_sql(remove_project)

	
	session.log_activity('Info', 'Processing deletions (complete)')