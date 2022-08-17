import sys
import json
import time
import traceback
import logging
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
import multiprocessing
import numpy as np
from celery import group, chain, chord, signature
from celery.utils.log import get_task_logger
from celery.result import allow_join_result
from celery.signals import after_setup_logger
from datetime import timedelta
import sqlalchemy as s


from augur.tasks.git.util.facade_worker.facade_worker.facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author
from augur.tasks.git.util.facade_worker.facade_worker.facade03analyzecommit import analyze_commit
from augur.tasks.github.facade_github.tasks import *

from augur.tasks.util.worker_util import create_grouped_task_load

from augur.tasks.init.celery_app import celery_app as celery


from augur.application.db import data_parse
from augur.tasks.util.AugurUUID import GithubUUID, UnresolvableUUID
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, Issue, IssueEvent, IssueLabel, IssueAssignee, PullRequestMessageRef, IssueMessageRef, Contributor, Repo

from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.github.util.gh_graphql_entities import PullRequest
from augur.tasks.github.util.github_task_session import *

from augur.application.logs import TaskLogConfig


#Have one log file for facade_tasks
# facadeLogger = logging.getLogger(__name__)



#TODO: split out the github platform specific stuff from facade

# """
#     You can prevent Celery from configuring any loggers at all by connecting 
#     the setup_logging signal. This allows you to completely override the 
#     logging configuration with your own.
# """
# logger = logging.getLogger(__name__)
# config = AugurConfig(logger)
# logs_directory = config.get_value("Logging", "logs_directory")
# DISABLE_LOG_TO_FILE = False
# if logs_directory is None:
#     DISABLE_LOG_TO_FILE = True




#enable celery multithreading
@celery.task
def analyze_commits_in_parallel(queue, repo_id, repo_location, multithreaded):
    #create new cfg for celery thread.
    logger = logging.getLogger(analyze_commits_in_parallel.__name__)
    cfg = FacadeConfig(logger)

    for analyzeCommit in queue:    

        analyze_commit(cfg, repo_id, repo_location, analyzeCommit, multithreaded)


# if platform.python_implementation() == 'PyPy':
#   import pymysql
# else:
#   import MySQLdb

def analysis(cfg, multithreaded, session=None, processes=6):

# Run the analysis by looping over all active repos. For each repo, we retrieve
# the list of commits which lead to HEAD. If any are missing from the database,
# they are filled in. Then we check to see if any commits in the database are
# not in the list of parents, and prune them out.
#
# We also keep track of the last commit to be processed, so that if the analysis
# is interrupted (possibly leading to partial data in the database for the
# commit being analyzed at the time) we can recover.

### Local helper functions ###

    def update_analysis_log(repos_id,status):

    # Log a repo's analysis status

        log_message = ("INSERT INTO analysis_log (repos_id,status) "
            "VALUES (%s,%s)")

        try:
            cfg.cursor.execute(log_message, (repos_id,status))
            cfg.db.commit()
        except:
            pass

### The real function starts here ###

    cfg.update_status('Running analysis')
    cfg.log_activity('Info',f"Beginning analysis.")

    start_date = cfg.get_setting('start_date')

    repo_list = "SELECT repo_id,repo_group_id,repo_path,repo_name FROM repo WHERE repo_status='Analyze'"
    cfg.cursor.execute(repo_list)
    repos = list(cfg.cursor)


    for repo in repos:

        
        #Add committers for repo if session
        if session != None:
            grab_committer_list(session,repo[0])

        update_analysis_log(repo[0],"Beginning analysis.")
        cfg.log_activity('Verbose','Analyzing repo: %s (%s)' % (repo[0],repo[3]))

        cfg.inc_repos_processed()

        # First we check to see if the previous analysis didn't complete

        get_status = ("SELECT working_commit FROM working_commits WHERE repos_id=%s")

        cfg.cursor.execute(get_status, (repo[0], ))
        try:
            working_commits = list(cfg.cursor)
        except:
            working_commits = []
        #cfg.cursor.fetchone()[1]

        # If there's a commit still there, the previous run was interrupted and
        # the commit data may be incomplete. It should be trimmed, just in case.
        for commit in working_commits:
            trim_commit(cfg, repo[0],commit[0])

            # Remove the working commit.
            remove_commit = ("DELETE FROM working_commits "
                "WHERE repos_id = %s AND working_commit = %s")
            cfg.cursor.execute(remove_commit, (repo[0],commit[0]))
            cfg.db.commit()

            cfg.log_activity('Debug','Removed working commit: %s' % commit[0])

        # Start the main analysis

        update_analysis_log(repo[0],'Collecting data')

        repo_loc = ('%s%s/%s%s/.git' % (cfg.repo_base_directory,
            repo[1], repo[2],
            repo[3]))
        # Grab the parents of HEAD

        parents = subprocess.Popen(["git --git-dir %s log --ignore-missing "
            "--pretty=format:'%%H' --since=%s" % (repo_loc,start_date)],
            stdout=subprocess.PIPE, shell=True)

        parent_commits = set(parents.stdout.read().decode("utf-8",errors="ignore").split(os.linesep))

        # If there are no commits in the range, we still get a blank entry in
        # the set. Remove it, as it messes with the calculations

        if '' in parent_commits:
            parent_commits.remove('')

        # Grab the existing commits from the database

        existing_commits = set()

        find_existing = ("SELECT DISTINCT cmt_commit_hash FROM commits WHERE repo_id=%s")

        cfg.cursor.execute(find_existing, (repo[0], ))

        try:
            for commit in list(cfg.cursor):
                existing_commits.add(commit[0])
        except:
            cfg.log_activity('Info', 'list(cfg.cursor) returned an error')

        # Find missing commits and add them

        missing_commits = parent_commits - existing_commits

        cfg.log_activity('Debug','Commits missing from repo %s: %s' %
            (repo[0],len(missing_commits)))

        ## TODO: Verify if the multithreaded approach here is optimal for postgresql

        if len(missing_commits) > 0:

            

            #cfg.log_activity('Info','Type of missing_commits: %s' % type(missing_commits))
            
            #Split commits into mostly equal queues so each process starts with a workload and there is no
            #    overhead to pass into queue from the parent.            
            #Each task generates their own cfg as celery cannot serialize this data
            contrib_jobs = create_grouped_task_load(repo[0],repo_loc,multithreaded,processes=processes,dataList=missing_commits,task=analyze_commits_in_parallel)

            print(contrib_jobs)

            group_result = contrib_jobs.apply_async()
            #Context manager needed for joining back to parent process properly.
            with allow_join_result():
                group_result.join()
                
            
        elif len(missing_commits) > 0:
            for commit in missing_commits:
                analyze_commit(cfg, repo[0], repo_loc, commit, multithreaded)


        update_analysis_log(repo[0],'Data collection complete')

        update_analysis_log(repo[0],'Beginning to trim commits')

        # Find commits which are out of the analysis range

        trimmed_commits = existing_commits - parent_commits

        cfg.log_activity('Debug','Commits to be trimmed from repo %s: %s' %
            (repo[0],len(trimmed_commits)))

        for commit in trimmed_commits:

            trim_commit(cfg, repo[0],commit)

        set_complete = "UPDATE repo SET repo_status='Complete' WHERE repo_id=%s and repo_status != 'Empty'"
        try:
            cfg.cursor.execute(set_complete, (repo[0], ))
        except:
            pass

        update_analysis_log(repo[0],'Commit trimming complete')

        update_analysis_log(repo[0],'Complete')

    cfg.log_activity('Info','Running analysis (complete)')


def facade_init(session):
    

    
    
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


#TODO: turn this into a dynamic chain with the various platform resolution tasks in a list.
@celery.task
def facade_commits_model(github_contrib_resolition=True):

    logger = logging.getLogger(facade_commits_model.__name__)
    with FacadeSession(logger) as session:
        
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

        facade_init(session)

        start_time = time.time()
        session.cfg.log_activity('Quiet','Running facade-worker')

        if not limited_run or (limited_run and delete_marked_repos):
            git_repo_cleanup(session.cfg)

        if not limited_run or (limited_run and clone_repos):
            git_repo_initialize(session.cfg)

        if not limited_run or (limited_run and check_updates):
            check_for_repo_updates(session)

        if force_updates:
            force_repo_updates(session.cfg)

        if not limited_run or (limited_run and pull_repos):
            git_repo_updates(session.cfg)

        if force_analysis:
            force_repo_analysis(session.cfg)

        
        #Give analysis the github interface so that it can make API calls
        #if not limited_run or (limited_run and run_analysis):
        analysis(session.cfg, multithreaded, session=session)
        
        if github_contrib_resolition:
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


        ### end moved up

        if nuke_stored_affiliations:
            nuke_affiliations(session.cfg)

        session.logger.info(session.cfg)
        if not limited_run or (limited_run and fix_affiliations):
            fill_empty_affiliations(session)

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

        print('\nCompleted in %s\n' % timedelta(seconds=int(elapsed_time)))

        session.cfg.cursor.close()
        #session.cfg.cursor_people.close()
        session.cfg.db.close()
        #session.cfg.db_people.close()

