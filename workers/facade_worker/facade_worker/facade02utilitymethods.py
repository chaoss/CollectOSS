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

def update_repo_log(cfg, repos_id,status):

# Log a repo's fetch status
	cfg.log_activity("Info","{} {}".format(status, repos_id))
	log_message = ("INSERT INTO repos_fetch_log (repos_id,status) "
		"VALUES (%s,%s)")
	try:
		cfg.cursor.execute(log_message, (repos_id, status))
		cfg.db.commit()
	except:
		pass

def trim_commit(cfg, repo_id,commit):

# Quickly remove a given commit

	remove_commit = ("DELETE FROM commits "
		"WHERE repo_id=%s "
		"AND cmt_commit_hash=%s")

	try:
		cfg.cursor.execute(remove_commit, (repo_id, commit))
		cfg.db.commit()
	except:
		cfg.log_activity('Info','Cursor was closed, making another connection to db')
		db_user = read_config('Database', 'user', 'AUGUR_DB_USER', 'augur')
		db_pass = read_config('Database', 'password', 'AUGUR_DB_PASSWORD', 'augur')
		db_name = read_config('Database', 'name', 'AUGUR_DB_NAME', 'augur')
		db_host = read_config('Database', 'host', 'AUGUR_DB_HOST', 'localhost')
		db_port = read_config('Database', 'port', 'AUGUR_DB_PORT', 5432)
		db_user_people = db_user
		db_pass_people = db_pass
		db_name_people = db_name
		db_host_people = db_host
		db_port_people = db_port

		db,cursor = cfg.database_connection(
			db_host,
			db_user,
			db_pass,
			db_name,
			db_port, False, False)

		db_people,cursor_people = cfg.database_connection(
			db_host_people,
			db_user_people,
			db_pass_people,
			db_name_people,
			db_port_people, True, False)

		cfg.cursor.execute(remove_commit, (repo_id, commit))
		cfg.db.commit()

	cfg.log_activity('Debug','Trimmed commit: %s' % commit)

def store_working_author(cfg, email):

# Store the working author during affiliation discovery, in case it is
# interrupted and needs to be trimmed.

	store = ("UPDATE settings "
		"SET value = %s "
		"WHERE setting = 'working_author'")

	cfg.cursor.execute(store, (email, ))
	cfg.db.commit()

	cfg.log_activity('Debug','Stored working author: %s' % email)

def trim_author(cfg, email):

# Remove the affiliations associated with an email. Used when an analysis is
# interrupted during affiliation layering, and the data will be corrupt.

	trim = ("UPDATE commits "
		"SET cmt_author_affiliation = NULL "
		"WHERE cmt_author_email = %s")

	cfg.cursor.execute(trim, (email, ))
	cfg.db.commit()

	trim = ("UPDATE commits "
		"SET cmt_committer_affiliation = NULL "
		"WHERE cmt_committer_email = %s")

	cfg.cursor.execute(trim, (email, ))
	cfg.db.commit()

	store_working_author(cfg, 'done')

	cfg.log_activity('Debug','Trimmed working author: %s' % email)

