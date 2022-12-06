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

#define an error callback for chains in facade collection so facade doesn't make the program crash
#if it does.
@celery.task
def facade_error_handler(request,exc,traceback):
    logger = logging.getLogger(facade_error_handler.__name__)

    logger.error(f"Task {request.id} raised exception: {exc}! \n {traceback}")

    print(f"chain: {request.chain}")
    #Make sure any further execution of tasks dependent on this one stops.
    try:
        #Replace the tasks queued ahead of this one in a chain with None.
        request.chain = None
    except AttributeError:
        pass #Task is not part of a chain. Normal so don't log.
    except Exception as e:
        logger.error(f"Could not mutate request chain! \n Error: {e}")


#Predefine facade collection with tasks
@celery.task
def facade_analysis_init_facade_task():
    logger = logging.getLogger(facade_analysis_init_facade_task.__name__)
    with FacadeSession(logger) as session:
        session.update_status('Running analysis')
        session.log_activity('Info',f"Beginning analysis.")

@celery.task
def grab_comitter_list_facade_task(repo_id,platform="github"):
    logger = logging.getLogger(grab_comitter_list_facade_task.__name__)

    try:
        grab_committer_list(GithubTaskSession(logger), repo_id,platform)
    except Exception as e:
        logger.error(f"Could not grab committers from github endpoint!\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
        

@celery.task
def trim_commits_facade_task(repo_id):
    logger = logging.getLogger(trim_commits_facade_task.__name__)
    session = FacadeSession(logger)

    def update_analysis_log(repos_id,status):

    # Log a repo's analysis status

        log_message = s.sql.text("""INSERT INTO analysis_log (repos_id,status)
            VALUES (:repo_id,:status)""").bindparams(repo_id=repos_id,status=status)

        try:
            session.execute_sql(log_message)
        except:
            pass



    session.inc_repos_processed()
    update_analysis_log(repo_id,"Beginning analysis.")
    # First we check to see if the previous analysis didn't complete

    get_status = s.sql.text("""SELECT working_commit FROM working_commits WHERE repos_id=:repo_id
        """).bindparams(repo_id=repo_id)

    try:
        working_commits = session.fetchall_data_from_sql_text(get_status)
    except:
        working_commits = []

    # If there's a commit still there, the previous run was interrupted and
    # the commit data may be incomplete. It should be trimmed, just in case.
    for commit in working_commits:
        trim_commit(session, repo_id,commit['working_commit'])

        # Remove the working commit.
        remove_commit = s.sql.text("""DELETE FROM working_commits
            WHERE repos_id = :repo_id AND 
            working_commit = :commit""").bindparams(repo_id=repo_id,commit=commit['working_commit'])
        session.execute_sql(remove_commit)
        session.log_activity('Debug',f"Removed working commit: {commit['working_commit']}")

@celery.task
def trim_commits_post_analysis_facade_task(repo_id,commits):
    logger = logging.getLogger(trim_commits_post_analysis_facade_task.__name__)

    session = FacadeSession(logger)
    def update_analysis_log(repos_id,status):

        # Log a repo's analysis status

        log_message = s.sql.text("""INSERT INTO analysis_log (repos_id,status)
            VALUES (:repo_id,:status)""").bindparams(repo_id=repos_id,status=status)

        
        session.execute_sql(log_message)
    

    update_analysis_log(repo_id,'Data collection complete')

    update_analysis_log(repo_id,'Beginning to trim commits')

    session.log_activity('Debug',f"Commits to be trimmed from repo {repo_id}: {len(commits)}")
    
    for commit in commits:
        trim_commit(session,repo_id,commit)
    
    set_complete = s.sql.text("""UPDATE repo SET repo_status='Complete' WHERE repo_id=:repo_id and repo_status != 'Empty'
        """).bindparams(repo_id=repo_id)
    
    session.execute_sql(set_complete)

    update_analysis_log(repo_id,'Commit trimming complete')

    update_analysis_log(repo_id,'Complete')

@celery.task
def facade_analysis_end_facade_task():
    logger = logging.getLogger(facade_analysis_end_facade_task.__name__)
    FacadeSession(logger).log_activity('Info','Running analysis (complete)')



@celery.task
def facade_start_contrib_analysis_task():
    logger = logging.getLogger(facade_start_contrib_analysis_task.__name__)
    session = FacadeSession(logger)
    session.update_status('Updating Contributors')
    session.log_activity('Info', 'Updating Contributors with commits')


#enable celery multithreading
@celery.task
def analyze_commits_in_parallel(queue: list, repo_id: int, repo_location: str, multithreaded: bool)-> None:
    """Take a large list of commit data to analyze and store in the database. Meant to be run in parallel with other instances of this task.
    """

    ### Local helper functions ###
    #create new session for celery thread.
    logger = logging.getLogger(analyze_commits_in_parallel.__name__)
    session = FacadeSession(logger)

    def update_analysis_log(repos_id,status):

        # Log a repo's analysis status

        log_message = s.sql.text("""INSERT INTO analysis_log (repos_id,status)
            VALUES (:repo_id,:status)""").bindparams(repo_id=repos_id,status=status)

        try:
            session.execute_sql(log_message)
        except:
            pass
    
    
    # Start the main analysis

    update_analysis_log(repo_id,'Collecting data')



    for analyzeCommit in queue:    

        analyze_commit(session, repo_id, repo_location, analyzeCommit)

@celery.task
def nuke_affiliations_facade_task():
    logger = logging.getLogger(nuke_affiliations_facade_task.__name__)
    session = FacadeSession(logger)

    nuke_affiliations(session)

@celery.task
def fill_empty_affiliations_facade_task():
    logger = logging.getLogger(fill_empty_affiliations_facade_task.__name__)
    with FacadeSession(logger) as session:
        fill_empty_affiliations(session)

@celery.task
def invalidate_caches_facade_task():
    logger = logging.getLogger(invalidate_caches_facade_task.__name__)

    with FacadeSession(logger) as session:
        invalidate_caches(session)

@celery.task
def rebuild_unknown_affiliation_and_web_caches_facade_task():
    logger = logging.getLogger(rebuild_unknown_affiliation_and_web_caches_facade_task.__name__)
    
    with FacadeSession(logger) as session:
        rebuild_unknown_affiliation_and_web_caches(session)



def generate_analysis_sequence(logger):
    """Run the analysis by looping over all active repos. For each repo, we retrieve
    the list of commits which lead to HEAD. If any are missing from the database,
    they are filled in. Then we check to see if any commits in the database are
    not in the list of parents, and prune them out.

    We also keep track of the last commit to be processed, so that if the analysis
    is interrupted (possibly leading to partial data in the database for the
    commit being analyzed at the time) we can recover.
    """
    analysis_sequence = []

    with FacadeSession(logger) as session:
        repo_list = s.sql.text("""SELECT repo_id,repo_group_id,repo_path,repo_name FROM repo """)
        repos = session.fetchall_data_from_sql_text(repo_list)

        start_date = session.get_setting('start_date')

        analysis_sequence.append(facade_analysis_init_facade_task.si().on_error(facade_error_handler.s()))
        for repo in repos:
            session.logger.info(f"Generating sequence for repo {repo['repo_id']}")
            analysis_sequence.append(grab_comitter_list_facade_task.si(repo['repo_id']).on_error(facade_error_handler.s()))

            analysis_sequence.append(trim_commits_facade_task.si(repo['repo_id']).on_error(facade_error_handler.s()))


            #Get the huge list of commits to process.
            repo_loc = (f"{session.repo_base_directory}{repo['repo_group_id']}/{repo['repo_path']}{repo['repo_name']}/.git")
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

            find_existing = s.sql.text("""SELECT DISTINCT cmt_commit_hash FROM commits WHERE repo_id=:repo_id
                """).bindparams(repo_id=repo['repo_id'])

            #session.cfg.cursor.execute(find_existing, (repo[0], ))

            try:
                for commit in session.fetchall_data_from_sql_text(find_existing):#list(session.cfg.cursor):
                    existing_commits.add(commit['cmt_commit_hash'])
            except:
                session.log_activity('Info', 'list(cfg.cursor) returned an error')

            # Find missing commits and add them

            missing_commits = parent_commits - existing_commits

            session.log_activity('Debug',f"Commits missing from repo {repo['repo_id']}: {len(missing_commits)}")
            
            if len(missing_commits) > 0:
                #session.log_activity('Info','Type of missing_commits: %s' % type(missing_commits))

                #Split commits into mostly equal queues so each process starts with a workload and there is no
                #    overhead to pass into queue from the parent.            
                contrib_jobs = create_grouped_task_load(repo['repo_id'],repo_loc,True,dataList=list(missing_commits),task=analyze_commits_in_parallel)
                contrib_jobs.link_error(facade_error_handler.s())
                analysis_sequence.append(contrib_jobs)
            
            # Find commits which are out of the analysis range

            trimmed_commits = existing_commits - parent_commits
            analysis_sequence.append(trim_commits_post_analysis_facade_task.si(repo['repo_id'],list(trimmed_commits)).on_error(facade_error_handler.s()))
        
        analysis_sequence.append(facade_analysis_end_facade_task.si().on_error(facade_error_handler.s()))
    
    #print(f"Analysis sequence: {analysis_sequence}")
    return analysis_sequence



def generate_contributor_sequence(logger):
    
    contributor_sequence = []
    with FacadeSession(logger) as session:
        
        #contributor_sequence.append(facade_start_contrib_analysis_task.si())
        query = s.sql.text("""SELECT repo_id FROM repo""")

        all_repos = session.fetchall_data_from_sql_text(query)
        #pdb.set_trace()
        #breakpoint()
        for repo in all_repos:
            contributor_sequence.append(insert_facade_contributors.si(repo['repo_id']))

    contrib_group = group(contributor_sequence)
    contrib_group.link_error(facade_error_handler.s())
    return chain(facade_start_contrib_analysis_task.si(),)




def generate_facade_chain(logger):
    #raise NotImplemented

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

        facade_sequence = []

        if not limited_run or (limited_run and delete_marked_repos):
            git_repo_cleanup(session)

        if not limited_run or (limited_run and clone_repos):
            git_repo_initialize(session)

        if not limited_run or (limited_run and check_updates):
            check_for_repo_updates(session)

        if force_updates:
            force_repo_updates(session)#facade_sequence.append(force_repo_updates_facade_task.si())

        if not limited_run or (limited_run and pull_repos):
            git_repo_updates(session)#facade_sequence.append(git_repo_updates_facade_task.si())

        if force_analysis:
            force_repo_analysis(session)#facade_sequence.append(force_repo_analysis_facade_task.si())

        #Generate commit analysis task order.
        facade_sequence.extend(generate_analysis_sequence(logger))

        #Generate contributor analysis task group.
        facade_sequence.append(generate_contributor_sequence(logger))

        if nuke_stored_affiliations:
            facade_sequence.append(nuke_affiliations_facade_task.si().on_error(facade_error_handler.s()))#nuke_affiliations(session.cfg)

        #session.logger.info(session.cfg)
        if not limited_run or (limited_run and fix_affiliations):
            facade_sequence.append(fill_empty_affiliations_facade_task.si().on_error(facade_error_handler.s()))#fill_empty_affiliations(session)

        if force_invalidate_caches:
            facade_sequence.append(invalidate_caches_facade_task.si().on_error(facade_error_handler.s()))#invalidate_caches(session.cfg)

        if not limited_run or (limited_run and rebuild_caches):
            facade_sequence.append(rebuild_unknown_affiliation_and_web_caches_facade_task.si().on_error(facade_error_handler.s()))#rebuild_unknown_affiliation_and_web_caches(session.cfg)
        
        return chain(*facade_sequence)

