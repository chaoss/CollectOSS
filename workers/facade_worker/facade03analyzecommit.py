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
# if platform.python_implementation() == 'PyPy':
# 	import pymysql
# else:
# 	import MySQLdb


def analyze_commit(cfg, repo_id, repo_loc, commit, multithreaded):

# This function analyzes a given commit, counting the additions, removals, and
# whitespace changes. It collects all of the metadata about the commit, and
# stashes it in the database.  A new database connection is opened each time in
# case we are running in multithreaded mode, since MySQL cursors are not
# currently threadsafe.

### Local helper functions ###

	def check_swapped_emails(name,email):

	# Sometimes people mix up their name and email in their git settings

		if name.find('@') >= 0 and email.find('@') == -1:
			cfg.log_activity('Debug','Found swapped email/name: %s/%s' % (email,name))
			return email,name
		else:
			return name,email

	def strip_extra_amp(email):

	# Some repos have multiple ampersands, which really messes up domain pattern
	# matching. This extra info is not used, so we discard it.

		if email.count('@') > 1:
			cfg.log_activity('Debug','Found extra @: %s' % email)
			return email[:email.find('@',email.find('@')+1)]
		else:
			return email

	def discover_alias(email):

	# Match aliases with their canonical email
		fetch_canonical = ("SELECT canonical_email "
			"FROM contributors_aliases "
			"WHERE alias_email=%s "
			"AND cntrb_active = 1")

		cursor_people_local.execute(fetch_canonical, (email, ))
		db_people_local.commit()

		canonical = list(cursor_people_local)

		if canonical:
			for email in canonical:
				return email[0]
		else:
			return email

	def store_commit(repos_id,commit,filename,
		author_name,author_email,author_date,
		committer_name,committer_email,committer_date,
		added,removed, whitespace):

	# Fix some common issues in git commit logs and store data.

		# Sometimes git is misconfigured and name/email get swapped
		author_name, author_email = check_swapped_emails(author_name,author_email)
		committer_name,committer_email = check_swapped_emails(committer_name,committer_email)

		# Some systems append extra info after a second @
		author_email = strip_extra_amp(author_email)
		committer_email = strip_extra_amp(committer_email)

		store = ("INSERT INTO commits (repo_id,cmt_commit_hash,cmt_filename,"
			"cmt_author_name,cmt_author_raw_email,cmt_author_email,cmt_author_date,"
			"cmt_committer_name,cmt_committer_raw_email,cmt_committer_email,cmt_committer_date,"
			"cmt_added,cmt_removed,cmt_whitespace, tool_source, tool_version, data_source, data_collection_date) "
			"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s)")

		cursor_local.execute(store, (
			repos_id,commit,filename,
			author_name,author_email,discover_alias(author_email),author_date,
			committer_name,committer_email,discover_alias(committer_email),committer_date,
			added,removed,whitespace, cfg.tool_source, cfg.tool_version, cfg.data_source, datetime.datetime.now()))

		db_local.commit()

		cfg.log_activity('Debug','Stored commit: %s' % commit)

		# store = ("INSERT INTO contributors (repo_id,cmt_commit_hash,cmt_filename,"
		# 	"cmt_author_name,cmt_author_raw_email,cmt_author_email,cmt_author_date,"
		# 	"cmt_committer_name,cmt_committer_raw_email,cmt_committer_email,cmt_committer_date,"
		# 	"cmt_added,cmt_removed,cmt_whitespace) "
		# 	"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")


		# cursor_local.execute(store, (
		# 	None, #cntrb_login
		# 	author_email, #login
		# 	#email
		# 	#comany
		# 	,#created_at
		# 	,#type
		# 	,#fake
		# 	,#deleted
		# 	,#long
		# 	,#lat
		# 	,#countrycode
		# 	,#state
		# 	,#city

		# 	author_name,discover_alias(author_email),author_date,
		# 	committer_name,committer_email,discover_alias(committer_email),committer_date,
		# 	added,removed,whitespace))

		# db_local.commit()

		

### The real function starts here ###

	header = True
	filename = ''
	filename = ''
	added = 0
	removed = 0
	whitespace = 0


	try:
		config = configparser.ConfigParser()
		config.read(os.path.join(os.path.dirname(__file__),'db.cfg'))

		# Read in the general connection info

		db_user = config['main_database']['user']
		db_pass = config['main_database']['pass']
		db_name = config['main_database']['name']
		db_host = config['main_database']['host']

		# Read in the people connection info

		db_user_people = config['people_database']['user']
		db_pass_people = config['people_database']['pass']
		db_name_people = config['people_database']['name']
		db_host_people = config['people_database']['host']

	except:
		# If the config import fails, check if there's an older style db.py

		db_user,db_pass,db_name,db_host,db_user_people,db_pass_people,db_name_people,db_host_people = cfg.migrate_database_config()


	# Set up new threadsafe database connections if multithreading. Otherwise
	# use the gloabl database connections so we don't incur a performance
	# penalty.

	if multithreaded:
		db_local,cursor_local = cfg.database_connection(
			db_host,
			db_user,
			db_pass,
			db_name, False, True)

		db_people_local,cursor_people_local = cfg.database_connection(
			db_host_people,
			db_user_people,
			db_pass_people,
			db_name_people, True, True)

	else:
		db_local = cfg.db
		cursor_local = cfg.cursor

		db_people_local = cfg.db_people
		cursor_people_local = cfg.cursor_people

	# Read the git log

	git_log = subprocess.Popen(["git --git-dir %s log -p -M %s -n1 "
		"--pretty=format:'"
		"author_name: %%an%%nauthor_email: %%ae%%nauthor_date:%%ai%%n"
		"committer_name: %%cn%%ncommitter_email: %%ce%%ncommitter_date: %%ci%%n"
		"parents: %%p%%nEndPatch' "
		% (repo_loc,commit)], stdout=subprocess.PIPE, shell=True)

	# Stash the commit we're going to analyze so we can back it out if something
	# goes wrong later.
	store_working_commit = ("INSERT INTO working_commits "
		"(repos_id,working_commit) VALUES (%s,%s)")

	cursor_local.execute(store_working_commit, (repo_id,commit))
	db_local.commit()

	cfg.log_activity('Debug','Stored working commit and analyzing : %s' % commit)

	for line in git_log.stdout.read().decode("utf-8",errors="ignore").split(os.linesep):
		if len(line) > 0:

			if line.find('author_name:') == 0:
				author_name = line[13:]
				continue

			if line.find('author_email:') == 0:
				author_email = line[14:]
				continue

			if line.find('author_date:') == 0:
				author_date = line[12:22]
				continue

			if line.find('committer_name:') == 0:
				committer_name = line[16:]
				continue

			if line.find('committer_email:') == 0:
				committer_email = line[17:]
				continue

			if line.find('committer_date:') == 0:
				committer_date = line[16:26]
				continue

			if line.find('parents:') == 0:
				if len(line[9:].split(' ')) == 2:

					# We found a merge commit, which won't have a filename
					filename = '(Merge commit)';

					added = 0
					removed = 0
					whitespace = 0
				continue

			if line.find('--- a/') == 0:
				if filename == '(Deleted) ':
					filename = filename + line[6:]
				continue

			if line.find('+++ b/') == 0:
				if not filename.find('(Deleted) ') == 0:
					filename = line[6:]
				continue

			if line.find('rename to ') == 0:
				filename = line[10:]
				continue

			if line.find('deleted file ') == 0:
				filename = '(Deleted) '
				continue

			if line.find('diff --git') == 0:

				# Git only displays the beginning of a file in a patch, not
				# the end. We need some kludgery to discern where one starts
				# and one ends. This is the last line always separating
				# files in commits. But we only want to do it for the second
				# time onward, since the first time we hit this line it'll be
				# right after parsing the header and there won't be any useful
				# information contained in it.

				if not header:

					store_commit(repo_id,commit,filename,
						author_name,author_email,author_date,
						committer_name,committer_email,committer_date,
						added,removed,whitespace)

				header = False

				# Reset stats and prepare for the next section
				whitespaceCheck = []
				resetRemovals = True
				filename = ''
				added = 0
				removed = 0
				whitespace = 0
				continue

			# Count additions and removals and look for whitespace changes
			if not header:
				if line[0] == '+':

					# First check if this is a whitespace change
					if len(line.strip()) == 1:
						# Line with zero length
						whitespace += 1

					else:
						# Compare against removals, detect whitespace changes
						whitespaceChange = False

						for check in whitespaceCheck:

							# Mark matches of non-trivial length
							if line[1:].strip() == check and len(line[1:].strip()) > 8:
								whitespaceChange = True

						if whitespaceChange:
							# One removal was whitespace, back it out
							removed -= 1
							whitespace += 1
							# Remove the matched line
							whitespaceCheck.remove(check)

						else:
							# Did not trigger whitespace criteria
							added += 1

					# Once we hit an addition, next removal line will be new.
					# At that point, start a new collection for checking.
					resetRemovals = True

				if line[0] == '-':
					removed += 1
					if resetRemovals:
						whitespaceCheck = []
						resetRemovals = False
					# Store the line to check next add lines for a match
					whitespaceCheck.append(line[1:].strip())

	# Store the last stats from the git log
	store_commit(repo_id,commit,filename,
		author_name,author_email,author_date,
		committer_name,committer_email,committer_date,
		added,removed,whitespace)

	# Remove the working commit.
	remove_commit = ("DELETE FROM working_commits "
		"WHERE repos_id = %s AND working_commit = %s")
	cursor_local.execute(remove_commit, (repo_id,commit))
	db_local.commit()

	cfg.log_activity('Debug','Completed and removed working commit: %s' % commit)

	# If multithreading, clean up the local database

	if multithreaded:
		cursor_local.close()
		cursor_people_local.close()
		db_local.close()
		db_people_local.close()

#### Facade main functions ####