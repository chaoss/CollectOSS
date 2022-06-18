from typing import Any, Union, Optional
from dataclasses import dataclass
from enforce_typing import enforce_types

import json
from celery import group, chain, chord, signature
from celery.utils.log import get_task_logger


import time
import traceback
import logging
import sys

import sqlalchemy as s

from .main import app
from .main import redis_conn

from .db_models import PullRequests, Message, PullRequestReviews, PullRequestLabels, PullRequestReviewers, PullRequestEvents, PullRequestMeta, PullRequestAssignees, PullRequestReviewMessageRef, SQLAlchemy, Issues, IssueEvents

from .github_paginator import GithubPaginator
from .worker_base import TaskSession

from workers.facade_worker.facade_worker import facade00mainprogram

from augur_new.util import data_parse


config_path = '../augur/augur.config.json'


with open(config_path, 'r') as f:
    config = json.load(f)


@app.task
def facade_commits_model( message: str):

    logger = get_task_logger(facade_commits_model.name)
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

@app.task
def facade_grab_contribs():
    logger = get_task_logger(facade_grab_contribs.name)
    session = FacadeSession(logger)

    #Give analysis the github interface so that it can make API calls
    analysis(session.cfg, multithreaded, session=session)



@app.task
def facade_resolve_contribs():
    logger = get_task_logger(facade_resolve_contribs.name)
    session = FacadeSession(logger)
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
        insert_facade_contributors(session,repo[0],multithreaded=multithreaded)
        session.logger.info(f"Processing repo contributors for repo: {repo}")
