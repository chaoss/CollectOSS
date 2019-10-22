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
from multiprocessing import Process, Queue

from facade_worker.facade01config import Config#increment_db, update_db, migrate_database_config, database_connection, get_setting, update_status, log_activity          
from facade_worker.facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author   
from facade_worker.facade03analyzecommit import analyze_commit
from facade_worker.facade04postanalysiscleanup import git_repo_cleanup
from facade_worker.facade05repofetch import git_repo_initialize, check_for_repo_updates, force_repo_updates, force_repo_analysis, git_repo_updates
from facade_worker.facade06analyze import analysis
from facade_worker.facade07rebuildcache import nuke_affiliations, fill_empty_affiliations, invalidate_caches, rebuild_unknown_affiliation_and_web_caches
import logging
# if platform.python_implementation() == 'PyPy':
#   import pymysql
# else:
#   import MySQLdb
# ## End Imports

html = html.parser.HTMLParser()

class CollectorTask:
    """ Worker's perception of a task in its queue
    Holds a message type (EXIT, TASK, etc) so the worker knows how to process the queue entry
    and the github_url given that it will be collecting data for
    """
    def __init__(self, message_type='TASK', entry_info=None):
        self.type = message_type
        self.entry_info = entry_info

class FacadeWorker:
    def __init__(self, config, task=None):
        self.config = config
        logging.basicConfig(filename='worker_{}.log'.format(self.config['id'].split('.')[len(self.config['id'].split('.')) - 1]), filemode='w', level=logging.INFO)
        
        print('Worker (PID: {}) initializing...'.format(os.getpid()))
        logging.info('Worker (PID: {}) initializing...'.format(os.getpid()))
        
        self._task = task
        self._child = None
        self._queue = Queue()
        self._maintain_queue = Queue()
        self.cfg = Config()
        
        ### The real program starts here ###

        # Set up the database
        json = self.cfg.read_config("Database", use_main_config=1)#self.cfg.migrate_database_config("Credentials")
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

        #   print(("Current database version: %s\nUpstream database version %s\n" %
        #       (current_db, upstream_db)))

        #   self.cfg.update_db(current_db);

        self.commit_model()

    @property
    def task(self):
        """ Property that is returned when the worker's current task is referenced
        """
        return self._task
    
    @task.setter
    def task(self, value):
        """ entry point for the broker to add a task to the queue
        Adds this task to the queue, and calls method to process queue
        """
        rg_id = value['given']['repo_group_id']

        """ Query all repos """
        # repoUrlSQL = s.sql.text("""
        #     SELECT repo_id,repo_group_id,repo_git FROM repo WHERE repo_group_id = '{}'
        #     """.format(rg_id))
        # rs = pd.read_sql(repoUrlSQL, self.db, params={})
        try:
            if value['job_type'] == "UPDATE":
                self._queue.put(CollectorTask(message_type='TASK', entry_info=value))
            elif value['job_type'] == "MAINTAIN":
                self._maintain_queue.put(CollectorTask(message_type='TASK', entry_info=value))

        except Exception as e:
            logging.info("error: {}".format(e))
        
        self._task = CollectorTask(message_type='TASK', entry_info={"task": value, "repo_id": repo_id})
        self.run()

    def cancel(self):
        """ Delete/cancel current task
        """
        self._task = None

    def run(self):
        """ Kicks off the processing of the queue if it is not already being processed
        Gets run whenever a new task is added
        """
        logging.info("Running...")
        if self._child is None:
            self._child = Process(target=self.collect, args=())
            self._child.start()
            
    def collect(self):
        """ Function to process each entry in the worker's task queue
        Determines what action to take based off the message type
        """
        while True:
            time.sleep(0.5)
            if not self._queue.empty():
                message = self._queue.get()
                logging.info("Popped off message: {}".format(message.entry_info))
                self.working_on = "UPDATE"
            else:
                if not self._maintain_queue.empty():
                    message = self._maintain_queue.get()
                    logging.info("Popped off message: {}".format(message.entry_info))
                    self.working_on = "MAINTAIN"
                else:
                    break

            if message.type == 'EXIT':
                break

            if message.type != 'TASK':
                raise ValueError(f'{message.type} is not a recognized task type')

            if message.type == 'TASK':
                try:
                    git_url = message.entry_info['task']['given']['git_url']
                    self.query_issues({'git_url': git_url, 'repo_id': message.entry_info['repo_id']})
                except Exception as e:
                    logging.info("Worker ran into an error for task: {}\n".format(message.entry_info['task']))
                    logging.info("Error encountered: " + repr(e) + "\n")
                    logging.info("Notifying broker and logging task failure in database...\n")
                    message.entry_info['task']['worker_id'] = self.config['id']
                    requests.post("http://{}:{}/api/unstable/task_error".format(
                        self.config['broker_host'],self.config['broker_port']), json=message.entry_info['task'])
                    # Add to history table
                    task_history = {
                        "repo_id": message.entry_info['repo_id'],
                        "worker": self.config['id'],
                        "job_model": message.entry_info['task']['models'][0],
                        "oauth_id": self.config['zombie_id'],
                        "timestamp": datetime.datetime.now(),
                        "status": "Error",
                        "total_results": self.results_counter
                    }
                    self.helper_db.execute(self.history_table.update().where(self.history_table.c.history_id==self.history_id).values(task_history))

                    logging.info("Recorded job error for: " + str(message.entry_info['task']) + "\n")

                    # Update job process table
                    updated_job = {
                        "since_id_str": message.entry_info['repo_id'],
                        "last_count": self.results_counter,
                        "last_run": datetime.datetime.now(),
                        "analysis_state": 0
                    }
                    self.helper_db.execute(self.job_table.update().where(self.job_table.c.job_model==message.entry_info['task']['models'][0]).values(updated_job))
                    logging.info("Updated job process for model: " + message.entry_info['task']['models'][0] + "\n")

                    # Reset results counter for next task
                    self.results_counter = 0
                    pass

    def commit_model(self):

        # Figure out what we need to do
        limited_run = self.cfg.read_config("Facade",name="limited_run",use_main_config=1,default=0)
        delete_marked_repos = self.cfg.read_config("Facade",name="delete_marked_repos",use_main_config=1, default=0)
        pull_repos = self.cfg.read_config("Facade",name="pull_repos",use_main_config=1,default=0)
        clone_repos = self.cfg.read_config("Facade",name="clone_repos",use_main_config=1,default=1)
        check_updates = self.cfg.read_config("Facade",name="check_updates",use_main_config=1,default=0)
        force_updates = self.cfg.read_config("Facade",name="force_updates",use_main_config=1,default=0)
        run_analysis = self.cfg.read_config("Facade",name="run_analysis",use_main_config=1,default=0)
        force_analysis = self.cfg.read_config("Facade",name="force_analysis",use_main_config=1,default=0)
        nuke_stored_affiliations = self.cfg.read_config("Facade",name="nuke_stored_affiliations",use_main_config=1, default=0)
        fix_affiliations = self.cfg.read_config("Facade",name="fix_affiliations",use_main_config=1,default=1)
        force_invalidate_caches = self.cfg.read_config("Facade",name="force_invalidate_caches",use_main_config=1, default=0)
        rebuild_caches = self.cfg.read_config("Facade",name="rebuild_caches",use_main_config=1,default=1) #if abs((datetime.datetime.strptime(self.cfg.get_setting('aliases_processed')[:-3], 
            # '%Y-%m-%d %I:%M:%S.%f') - datetime.datetime.now()).total_seconds()) // 3600 > int(self.cfg.get_setting(
            #   'update_frequency')) else 0
        force_invalidate_caches = self.cfg.read_config("Facade",name="force_invalidate_caches",use_main_config=1,default=0)
        create_xlsx_summary_files = self.cfg.read_config("Facade",name="create_xlsx_summary_files",use_main_config=1,default=0)
        multithreaded = self.cfg.read_config("Facade",name="multithreaded",use_main_config=1,default=1)

        opts,args = getopt.getopt(sys.argv[1:],'hdpcuUaAmnfIrx')
        for opt in opts:
            if opt[0] == '-h':
                print("\nfacade-worker.py does everything by default except invalidating caches\n"
                        "and forcing updates, unless invoked with one of the following options.\n"
                        "In those cases, it will only do what you have selected.\n\n"
                        "Options:\n"
                        "   -d  Delete marked repos\n"
                        "   -c  Run 'git clone' on new repos\n"
                        "   -u  Check if any repos should be marked for updating\n"
                        "   -U  Force all repos to be marked for updating\n"
                        "   -p  Run 'git pull' on repos\n"
                        "   -a  Analyze git repos\n"
                        "   -A  Force all repos to be analyzed\n"
                        "   -m  Disable multithreaded mode (but why?)\n"
                        "   -n  Nuke stored affiliations (if mappings modified by hand)\n"
                        "   -f  Fill empty affiliations\n"
                        "   -I  Invalidate caches\n"
                        "   -r  Rebuild unknown affiliation and web caches\n"
                        "   -x  Create Excel summary files\n\n")
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
        self.cfg.log_activity('Quiet','Running facade-worker')

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
