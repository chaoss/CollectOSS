from __future__ import annotations
from typing import List
import time
import logging
import os
from enum import Enum
import math
import numpy as np
import datetime
import random
#from celery.result import AsyncResult
from celery import signature
from celery import group, chain, chord, signature
from sqlalchemy import or_, and_,tuple_, update


from augur.tasks.github import *
if os.environ.get('AUGUR_DOCKER_DEPLOY') != "1":
    from augur.tasks.data_analysis import *
from augur.tasks.github.detect_move.tasks import detect_github_repo_move_core, detect_github_repo_move_secondary
from augur.tasks.github.releases.tasks import collect_releases
from augur.tasks.github.repo_info.tasks import collect_repo_info, collect_linux_badge_info
from augur.tasks.github.pull_requests.files_model.tasks import process_pull_request_files
from augur.tasks.github.pull_requests.commits_model.tasks import process_pull_request_commits
from augur.tasks.git.dependency_tasks.tasks import process_ossf_dependency_metrics
from augur.tasks.github.traffic.tasks import collect_github_repo_clones_data
from augur.tasks.git.facade_tasks import *
from augur.tasks.db.refresh_materialized_views import *
# from augur.tasks.data_analysis import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.session import DatabaseSession
from logging import Logger
from enum import Enum
from augur.tasks.util.redis_list import RedisList
from augur.application.db.models import CollectionStatus, Repo
from augur.tasks.util.collection_util import *
from augur.tasks.git.util.facade_worker.facade_worker.utilitymethods import get_facade_weight_time_factor

CELERY_GROUP_TYPE = type(group())
CELERY_CHAIN_TYPE = type(chain())



"""
    Predefine phases. For new phases edit this and the config to reflect.
    The domain of tasks ran should be very explicit.

    A phase in this context is a function that takes a repo_git and returns a message
    for the celery worker to process.
"""

#Prelim phases are used to detect if where the repo has hosted has moved or not.
def prelim_phase(repo_git):

    logger = logging.getLogger(prelim_phase.__name__)

    return detect_github_repo_move_core.si(repo_git)

def prelim_phase_secondary(repo_git):
    logger = logging.getLogger(prelim_phase.__name__)

    return detect_github_repo_move_secondary.si(repo_git)


#This is the phase that defines the message for core augur collection
#A chain is needed for each repo.
def primary_repo_collect_phase(repo_git):
    logger = logging.getLogger(primary_repo_collect_phase.__name__)


    #Define primary group of jobs for the primary collect phase: issues and pull requests.
    primary_repo_jobs = group(
        collect_issues.si(repo_git),
        collect_pull_requests.si(repo_git)
    )

    #Define secondary group that can't run until after primary jobs have finished.
    secondary_repo_jobs = group(
        collect_events.si(repo_git),#*create_grouped_task_load(dataList=first_pass, task=collect_events).tasks,
        collect_github_messages.si(repo_git), #*create_grouped_task_load(dataList=first_pass,task=collect_github_messages).tasks,
        collect_github_repo_clones_data.si(repo_git),
    )

    #Other tasks that don't need other tasks to run before they do just put in final group.
    repo_task_group = group(
        collect_repo_info.si(repo_git),
        chain(primary_repo_jobs | issue_pr_task_update_weight_util.s(repo_git=repo_git),secondary_repo_jobs,process_contributors.si()),
        #facade_phase(logger,repo_git),
        collect_linux_badge_info.si(repo_git),
        collect_releases.si(repo_git),
        grab_comitters.si(repo_git)
    )

    return repo_task_group


#This phase creates the message for secondary collection tasks.
#These are less important and have their own worker.
def secondary_repo_collect_phase(repo_git):
    logger = logging.getLogger(secondary_repo_collect_phase.__name__)

    repo_task_group = group(
        process_pull_request_files.si(repo_git),
        process_pull_request_commits.si(repo_git),
        process_ossf_dependency_metrics.si(repo_git),
        chain(collect_pull_request_reviews.si(repo_git), collect_pull_request_review_comments.si(repo_git))
    )

    return repo_task_group




#This is a periodic task that runs less often to handle less important collection tasks such as 
#refreshing the materialized views.
@celery.task
def non_repo_domain_tasks():

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(non_repo_domain_tasks.__name__)

    logger.info("Executing non-repo domain tasks")

    enabled_phase_names = []
    with DatabaseSession(logger, engine) as session:

        enabled_phase_names = get_enabled_phase_names_from_config(session.logger, session)

    enabled_tasks = []

    enabled_tasks.extend(generate_non_repo_domain_facade_tasks(logger))

    if machine_learning_phase.__name__ in enabled_phase_names:
        #enabled_tasks.extend(machine_learning_phase())
        from augur.tasks.data_analysis.contributor_breadth_worker.contributor_breadth_worker import contributor_breadth_model
        enabled_tasks.append(contributor_breadth_model.si())

    tasks = chain(
        *enabled_tasks,
    )

    tasks.apply_async()



    """
        The below functions define augur's collection hooks.
        Each collection hook schedules tasks for a number of repos
    """
def start_primary_collection(session,max_repo, days_until_collect_again = 1):

    #Get list of enabled phases 
    enabled_phase_names = get_enabled_phase_names_from_config(session.logger, session)

    #Primary collection hook.
    primary_enabled_phases = []

    #Primary jobs
    if prelim_phase.__name__ in enabled_phase_names:
        primary_enabled_phases.append(prelim_phase)
    
    
    primary_enabled_phases.append(primary_repo_collect_phase)

    #task success is scheduled no matter what the config says.
    def core_task_success_util_gen(repo_git):
        return core_task_success_util.si(repo_git)
    
    primary_enabled_phases.append(core_task_success_util_gen)

    start_repos_by_user(session, max_repo, primary_enabled_phases)

def start_secondary_collection(session,max_repo, days_until_collect_again = 1):

    #Get list of enabled phases 
    enabled_phase_names = get_enabled_phase_names_from_config(session.logger, session)

    #Deal with secondary collection
    secondary_enabled_phases = []

    if prelim_phase.__name__ in enabled_phase_names:
        secondary_enabled_phases.append(prelim_phase_secondary)

    
    secondary_enabled_phases.append(secondary_repo_collect_phase)

    def secondary_task_success_util_gen(repo_git):
        return secondary_task_success_util.si(repo_git)

    secondary_enabled_phases.append(secondary_task_success_util_gen)

    conds = f"augur_operations.collection_status.core_status = '{str(CollectionState.SUCCESS.value)}'"#[CollectionStatus.core_status == str(CollectionState.SUCCESS.value)]
    start_repos_by_user(
        session, max_repo,
        secondary_enabled_phases,hook="secondary",
        additional_conditions=conds
    )

def start_facade_collection(session,max_repo,days_until_collect_again = 1):

    #Deal with secondary collection
    facade_enabled_phases = []
    
    facade_enabled_phases.append(facade_phase)

    def facade_task_success_util_gen(repo_git):
        return facade_task_success_util.si(repo_git)

    facade_enabled_phases.append(facade_task_success_util_gen)

    def facade_task_update_weight_util_gen(repo_git):
        return git_update_commit_count_weight.si(repo_git)

    facade_enabled_phases.append(facade_task_update_weight_util_gen)

    #cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    #not_pending = CollectionStatus.facade_status != str(CollectionState.PENDING.value)
    #not_failed_clone = CollectionStatus.facade_status != str(CollectionState.FAILED_CLONE.value)
    #not_initializing = CollectionStatus.facade_status != str(CollectionState.INITIALIZING.value)

    conds = f"augur_operations.collection_status.facade_status != '{str(CollectionState.PENDING.value)}' "#[not_pending,not_failed_clone,not_initializing]
    conds += f"AND augur_operations.collection_status.facade_status != '{str(CollectionState.FAILED_CLONE.value)}' "
    conds += f"AND augur_operations.collection_status.facade_status != '{str(CollectionState.INITIALIZING.value)}'"

    start_repos_by_user(
        session, max_repo,
        facade_enabled_phases,hook="facade",
        new_status=CollectionState.UPDATE.value,additional_conditions=conds
    )

def start_ml_collection(session,max_repo, days_until_collect_again=7):
    ml_enabled_phases = []

    ml_enabled_phases.append(machine_learning_phase)

    def ml_task_success_util_gen(repo_git):
        return ml_task_success_util.si(repo_git)

    ml_enabled_phases.append(ml_task_success_util_gen)

    conds = f"augur_operations.collection_status.secondary_status = '{str(CollectionState.SUCCESS.value)}'"

    start_repos_by_user(
        session,max_repo,
        ml_enabled_phases,hook="ml",additional_conditions=conds
    )


@celery.task
def augur_collection_monitor():     

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(augur_collection_monitor.__name__)

    logger.info("Checking for repos to collect")

    with DatabaseSession(logger, engine) as session:
        #Get list of enabled phases 
        enabled_phase_names = get_enabled_phase_names_from_config(session.logger, session)

        if primary_repo_collect_phase.__name__ in enabled_phase_names:
            start_primary_collection(session, max_repo=40)
        
        if secondary_repo_collect_phase.__name__ in enabled_phase_names:
            start_secondary_collection(session, max_repo=10)

        if facade_phase.__name__ in enabled_phase_names:
            start_facade_collection(session, max_repo=30)
        
        if machine_learning_phase.__name__ in enabled_phase_names:
            start_ml_collection(session,max_repo=5)

# have a pipe of 180


@celery.task
def augur_collection_update_weights():

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(augur_collection_update_weights.__name__)

    logger.info("Updating stale collection weights")

    with DatabaseSession(logger,engine) as session:

        core_weight_update_repos = session.query(CollectionStatus).filter(CollectionStatus.core_weight != None).all()

        for status in core_weight_update_repos:
            repo = Repo.get_by_id(session, status.repo_id)

            repo_git = repo.repo_git
            status = repo.collection_status[0]
            raw_count = status.issue_pr_sum

            issue_pr_task_update_weight_util([int(raw_count)],repo_git=repo_git,session=session)
    
        facade_not_pending = CollectionStatus.facade_status != CollectionState.PENDING.value
        facade_not_failed = CollectionStatus.facade_status != CollectionState.FAILED_CLONE.value
        facade_weight_not_null = CollectionStatus.facade_weight != None

        facade_weight_update_repos = session.query(CollectionStatus).filter(and_(facade_not_pending,facade_not_failed,facade_weight_not_null)).all()

        for status in facade_weight_update_repos:
            repo = Repo.get_by_id(session, status.repo_id)

            commit_count = status.commit_sum
            date_factor = get_facade_weight_time_factor(session, repo.repo_git)
            weight = commit_count - date_factor

            update_query = (
                update(CollectionStatus)
                .where(CollectionStatus.repo_id == status.repo_id)
                .values(facade_weight=weight)
            )

            session.execute(update_query)
            session.commit()
            #git_update_commit_count_weight(repo_git)

#Retry this task for every issue so that repos that were added manually get the chance to be added to the collection_status table.
@celery.task(autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=300, retry_jitter=True, max_retries=None)
def create_collection_status_records():
    from augur.tasks.init.celery_app import engine
    logger = logging.getLogger(create_collection_status_records.__name__)

    with DatabaseSession(logger,engine) as session:
        query = s.sql.text("""
        SELECT repo_id FROM repo WHERE repo_id NOT IN (SELECT repo_id FROM augur_operations.collection_status)
        """)

        repo = session.execute_sql(query).first()

        while repo is not None:
            CollectionStatus.insert(session,repo[0])
            repo = session.execute_sql(query).first()
    
    #Check for new repos every seven minutes to be out of step with the clone_repos task
    create_collection_status_records.si().apply_async(countdown=60*7)