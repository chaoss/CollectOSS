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
from facade_worker.facade01config import Config#increment_db, update_db, migrate_database_config, database_connection, get_setting, update_status, log_activity          
from facade_worker.facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author   
from facade_worker.facade03analyzecommit import analyze_commit
from facade_worker.facade04postanalysiscleanup import git_repo_cleanup
from facade_worker.facade05repofetch import git_repo_initialize, check_for_repo_updates, force_repo_updates, force_repo_analysis, git_repo_updates
from facade_worker.facade06analyze import analysis
from facade_worker.facade07rebuildcache import nuke_affiliations, fill_empty_affiliations, invalidate_caches, rebuild_unknown_affiliation_and_web_caches

#from contributor_interfaceable.facade08contributorinterfaceable import ContributorInterfaceable

from contributor_interfaceable.contributor_interface import *

from workers.util import read_config
from workers.worker_base import Worker


logger = get_task_logger(__name__)

class FacadeSession(TaskSession):
    def __init__(self,logger,config={},platform='github'):
        session.cfg = Config(self.logger)

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




html = html.parser.HTMLParser()

#TODO: Make this a celery task.
def commits_model( message):

    session = FacadeSession(logger)
    # Figure out what we need to do
    limited_run = session.limited_run
    delete_marked_repos = session.delete_marked_repos
    pull_repos = session.pull_repos
    clone_repos = session.clone_repos
    check_updates = session.check_updates
    force_updates = session.force_updates
    run_analysis = session.run_analysis
    force_analysis = session.force_analysis
    nuke_stored_affiliations = session.nuke_stored_affiliations
    fix_affiliations = session.fix_affiliations
    force_invalidate_caches = session.force_invalidate_caches
    rebuild_caches = session.rebuild_caches
     #if abs((datetime.datetime.strptime(session.cfg.get_setting('aliases_processed')[:-3], 
        # '%Y-%m-%d %I:%M:%S.%f') - datetime.datetime.now()).total_seconds()) // 3600 > int(session.cfg.get_setting(
        #   'update_frequency')) else 0
    force_invalidate_caches = session.force_invalidate_caches
    create_xlsx_summary_files = session.create_xlsx_summary_files
    multithreaded = session.multithreaded

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
            session.cfg.log_activity('Info','Option set: delete marked repos.')

        elif opt[0] == '-c':
            clone_repos = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: clone new repos.')

        elif opt[0] == '-u':
            check_updates = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: checking for repo updates')

        elif opt[0] == '-U':
            force_updates = 1
            session.cfg.log_activity('Info','Option set: forcing repo updates')

        elif opt[0] == '-p':
            pull_repos = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: update repos.')

        elif opt[0] == '-a':
            run_analysis = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: running analysis.')

        elif opt[0] == '-A':
            force_analysis = 1
            run_analysis = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: forcing analysis.')

        elif opt[0] == '-m':
            multithreaded = 0
            session.cfg.log_activity('Info','Option set: disabling multithreading.')

        elif opt[0] == '-n':
            nuke_stored_affiliations = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: nuking all affiliations')

        elif opt[0] == '-f':
            fix_affiliations = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: fixing affiliations.')

        elif opt[0] == '-I':
            force_invalidate_caches = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: Invalidate caches.')

        elif opt[0] == '-r':
            rebuild_caches = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: rebuilding caches.')

        elif opt[0] == '-x':
            create_xlsx_summary_files = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: creating Excel summary files.')

    # Get the location of the directory where git repos are stored
    repo_base_directory = session.cfg.repo_base_directory

    # Determine if it's safe to start the script
    current_status = session.cfg.get_setting('utility_status')

    if current_status != 'Idle':
        session.cfg.log_activity('Error','Something is already running, aborting maintenance '
            'and analysis.\nIt is unsafe to continue.')
        # sys.exit(1)

    if len(repo_base_directory) == 0:
        session.cfg.log_activity('Error','No base directory. It is unsafe to continue.')
        session.cfg.update_status('Failed: No base directory')
        sys.exit(1)

    # Begin working

    start_time = time.time()
    session.cfg.log_activity('Quiet','Running facade-worker')

    if not limited_run or (limited_run and delete_marked_repos):
        git_repo_cleanup(session.cfg)

    if not limited_run or (limited_run and clone_repos):
        git_repo_initialize(session.cfg)

    if not limited_run or (limited_run and check_updates):
        check_for_repo_updates(session.cfg)

    if force_updates:
        force_repo_updates(session.cfg)

    if not limited_run or (limited_run and pull_repos):
        git_repo_updates(session.cfg)

    if force_analysis:
        force_repo_analysis(session.cfg)

    #Give analysis the github interface so that it can make API calls
    if not limited_run or (limited_run and run_analysis):
        analysis(session.cfg, multithreaded, session=session)

    ### moved up by spg on 12/1/2021
    #Interface with the contributor worker and inserts relevant data by repo
    session.cfg.update_status('Updating Contributors')
    session.cfg.log_activity('Info', 'Updating Contributors with commits')
    query = ("SELECT repo_id FROM repo");

    session.cfg.cursor.execute(query)

    all_repos = list(session.cfg.cursor)

    #pdb.set_trace()
    #breakpoint()
    for repo in all_repos:
        session.logger.info(f"Processing repo {repo}")
        insert_facade_contributors(repo[0],multithreaded=multithreaded)
        session.logger.info(f"Processing repo contributors for repo: {repo}")

    ### end moved up

    if nuke_stored_affiliations:
        nuke_affiliations(session.cfg)

    if not limited_run or (limited_run and fix_affiliations):
        fill_empty_affiliations(session.cfg)

    if force_invalidate_caches:
        invalidate_caches(session.cfg)

    if not limited_run or (limited_run and rebuild_caches):
        rebuild_unknown_affiliation_and_web_caches(session.cfg)

    if not limited_run or (limited_run and create_xlsx_summary_files):

        session.cfg.log_activity('Info','Creating summary Excel files')

        # from excel_generators import *

        session.cfg.log_activity('Info','Creating summary Excel files (complete)')


    # All done
    session.cfg.update_status('Idle')
    session.cfg.log_activity('Quiet','facade-worker.py completed')
    
    elapsed_time = time.time() - start_time

    print('\nCompleted in %s\n' % datetime.timedelta(seconds=int(elapsed_time)))

    session.cfg.cursor.close()
    session.cfg.cursor_people.close()
    session.cfg.db.close()
    session.cfg.db_people.close()
