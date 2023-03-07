from __future__ import annotations
from typing import List
import time
import logging
import json
import os
from enum import Enum
import math
import numpy as np
#from celery.result import AsyncResult
from celery import signature
from celery import group, chain, chord, signature
from sqlalchemy import or_, and_


from augur.tasks.github import *
if os.environ.get('AUGUR_DOCKER_DEPLOY') != "1":
    from augur.tasks.data_analysis import *
from augur.tasks.github.detect_move.tasks import detect_github_repo_move_core, detect_github_repo_move_secondary
from augur.tasks.github.releases.tasks import collect_releases
from augur.tasks.github.repo_info.tasks import collect_repo_info
from augur.tasks.github.pull_requests.files_model.tasks import process_pull_request_files
from augur.tasks.github.pull_requests.commits_model.tasks import process_pull_request_commits
from augur.tasks.git.dependency_tasks.tasks import process_ossf_scorecard_metrics

from augur.tasks.git.facade_tasks import *
from augur.tasks.db.refresh_materialized_views import *
# from augur.tasks.data_analysis import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.config import AugurConfig
from augur.application.db.session import DatabaseSession
from logging import Logger
from enum import Enum
from augur.tasks.util.redis_list import RedisList
from augur.application.db.models import CollectionStatus, Repo
from augur.tasks.util.collection_util import *

CELERY_GROUP_TYPE = type(group())
CELERY_CHAIN_TYPE = type(chain())



#Predefine phases. For new phases edit this and the config to reflect.
#The domain of tasks ran should be very explicit.
def prelim_phase(repo_git):

    logger = logging.getLogger(prelim_phase.__name__)

    return detect_github_repo_move_core.si(repo_git)

def prelim_phase_secondary(repo_git):
    logger = logging.getLogger(prelim_phase.__name__)

    return detect_github_repo_move_secondary.si(repo_git)


def primary_repo_collect_phase(repo_git):
    logger = logging.getLogger(primary_repo_collect_phase.__name__)

    #Here the term issues also includes prs. This list is a bunch of chains that run in parallel to process issue data.
    issue_dependent_tasks = []
    #repo_info should run in a group
    repo_info_tasks = []

    np_clustered_array = []

    #A chain is needed for each repo.
    repo_info_task = collect_repo_info.si(repo_git)#collection_task_wrapper(self)

    primary_repo_jobs = group(
        collect_issues.si(repo_git),
        collect_pull_requests.si(repo_git)
    )

    secondary_repo_jobs = group(
        collect_events.si(repo_git),#*create_grouped_task_load(dataList=first_pass, task=collect_events).tasks,
        collect_github_messages.si(repo_git),#*create_grouped_task_load(dataList=first_pass,task=collect_github_messages).tasks,
    )

    repo_task_group = group(
        repo_info_task,
        chain(primary_repo_jobs,secondary_repo_jobs,process_contributors.si()),
        #facade_phase(logger,repo_git),
        process_ossf_scorecard_metrics.si(repo_git),
        collect_releases.si(repo_git)
    )

    return repo_task_group


def secondary_repo_collect_phase(repo_git):
    logger = logging.getLogger(secondary_repo_collect_phase.__name__)

    repo_task_group = group(
        process_pull_request_files.si(repo_git),
        process_pull_request_commits.si(repo_git),
        chain(collect_pull_request_reviews.si(repo_git), collect_pull_request_review_comments.si(repo_git))
    )

    return repo_task_group




@celery.task
def non_repo_domain_tasks():

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(non_repo_domain_tasks.__name__)

    logger.info("Executing non-repo domain tasks")

    enabled_phase_names = []
    with DatabaseSession(logger, engine) as session:

        enabled_phase_names = get_enabled_phase_names_from_config(session.logger, session)

        #Disable augur from running these tasks more than once unless requested
        query = s.sql.text("""
            UPDATE augur_operations.config
            SET value=0
            WHERE section_name='Task_Routine'
            AND setting_name='machine_learning_phase'
        """)

        session.execute_sql(query)

    enabled_tasks = []

    enabled_tasks.extend(generate_non_repo_domain_facade_tasks(logger))

    if machine_learning_phase.__name__ in enabled_phase_names:
        enabled_tasks.extend(machine_learning_phase())

    tasks = chain(
        *enabled_tasks,
        refresh_materialized_views.si()
    )

    tasks.apply_async()




def start_primary_collection(session,max_repo,days):

    #Get list of enabled phases 
    enabled_phase_names = get_enabled_phase_names_from_config(session.logger, session)

    #Primary collection hook.
    primary_enabled_phases = []

    #Primary jobs
    if prelim_phase.__name__ in enabled_phase_names:
        primary_enabled_phases.append(prelim_phase)
    
    if primary_repo_collect_phase.__name__ in enabled_phase_names:
        primary_enabled_phases.append(primary_repo_collect_phase)

    #task success is scheduled no matter what the config says.
    def core_task_success_gen(repo_git):
        return core_task_success.si(repo_git)
    
    primary_enabled_phases.append(core_task_success_gen)
    
    active_repo_count = len(session.query(CollectionStatus).filter(CollectionStatus.core_status == CollectionState.COLLECTING.value).all())

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    not_erroed = CollectionStatus.core_status != str(CollectionState.ERROR.value)
    not_collecting = CollectionStatus.core_status != str(CollectionState.COLLECTING.value)
    never_collected = CollectionStatus.core_data_last_collected == None
    old_collection = CollectionStatus.core_data_last_collected <= cutoff_date

    limit = max_repo-active_repo_count

    #Get repos for primary collection hook
    repo_git_identifiers = get_collection_status_repo_git_from_filter(session,and_(not_erroed, not_collecting, or_(never_collected, old_collection)),limit)

    session.logger.info(f"Starting primary collection on {len(repo_git_identifiers)} repos")
    if len(repo_git_identifiers) == 0:
        return

    session.logger.info(f"Primary collection starting for: {tuple(repo_git_identifiers)}")

    primary_augur_collection = AugurTaskRoutine(session,repos=repo_git_identifiers,collection_phases=primary_enabled_phases)

    #Start data collection and update the collectionStatus with the task_ids
    for repo_git, task_id in primary_augur_collection.start_data_collection():
        
        repo = session.query(Repo).filter(Repo.repo_git == repo_git).one()

        #set status in database to collecting
        repoStatus = repo.collection_status[0]
        repoStatus.core_task_id = task_id
        #repoStatus.secondary_task_id = task_id
        repoStatus.core_status = CollectionState.COLLECTING.value
        session.commit()

def start_secondary_collection(session,max_repo,days):

    #Get list of enabled phases 
    enabled_phase_names = get_enabled_phase_names_from_config(session.logger, session)

    #Deal with secondary collection
    secondary_enabled_phases = []

    if prelim_phase.__name__ in enabled_phase_names:
        secondary_enabled_phases.append(prelim_phase_secondary)

    if secondary_repo_collect_phase.__name__ in enabled_phase_names:
        secondary_enabled_phases.append(secondary_repo_collect_phase)

    def secondary_task_success_gen(repo_git):
        return secondary_task_success.si(repo_git)

    secondary_enabled_phases.append(secondary_task_success_gen)

    active_repo_count = len(session.query(CollectionStatus).filter(CollectionStatus.secondary_status == CollectionState.COLLECTING.value).all())

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    not_erroed = CollectionStatus.secondary_status != str(CollectionState.ERROR.value)
    not_collecting = CollectionStatus.secondary_status != str(CollectionState.COLLECTING.value)
    never_collected = CollectionStatus.secondary_data_last_collected == None
    old_collection = CollectionStatus.secondary_data_last_collected <= cutoff_date
    primary_collected = CollectionStatus.core_status == str(CollectionState.SUCCESS.value)

    limit = max_repo-active_repo_count

    repo_git_identifiers = get_collection_status_repo_git_from_filter(session,and_(primary_collected,not_erroed, not_collecting, or_(never_collected, old_collection)),limit)

    session.logger.info(f"Starting secondary collection on {len(repo_git_identifiers)} repos")
    if len(repo_git_identifiers) == 0:
        return

    session.logger.info(f"Secondary collection starting for: {tuple(repo_git_identifiers)}")

    secondary_augur_collection = AugurTaskRoutine(session,repos=repo_git_identifiers,collection_phases=secondary_enabled_phases)

    #Start data collection and update the collectionStatus with the task_ids
    for repo_git, task_id in secondary_augur_collection.start_data_collection():
        
        repo = session.query(Repo).filter(Repo.repo_git == repo_git).one()

        #set status in database to collecting
        repoStatus = repo.collection_status[0]
        repoStatus.secondary_task_id = task_id
        repoStatus.secondary_status = CollectionState.COLLECTING.value
        session.commit()

def start_facade_collection(session,max_repo,days):

    #Get list of enabled phases 
    enabled_phase_names = get_enabled_phase_names_from_config(session.logger, session)

    #Deal with secondary collection
    facade_enabled_phases = []

    if facade_phase.__name__ in enabled_phase_names:
        facade_enabled_phases.append(facade_phase)

    def facade_task_success_gen(repo_git):
        return facade_task_success.si(repo_git)

    facade_enabled_phases.append(facade_task_success_gen)

    active_repo_count = len(session.query(CollectionStatus).filter(CollectionStatus.facade_task_id != None).all())

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    not_erroed = CollectionStatus.facade_status != str(CollectionState.ERROR.value)
    not_collecting = CollectionStatus.facade_task_id == None
    never_collected = CollectionStatus.facade_data_last_collected == None
    old_collection = CollectionStatus.facade_data_last_collected <= cutoff_date

    limit = max_repo-active_repo_count

    repo_git_identifiers = get_collection_status_repo_git_from_filter(session,and_(not_erroed, not_collecting, or_(never_collected, old_collection)),limit)

    session.logger.info(f"Starting facade collection on {len(repo_git_identifiers)} repos")
    if len(repo_git_identifiers) == 0:
        return

    session.logger.info(f"Facade collection starting for: {tuple(repo_git_identifiers)}")

    facade_augur_collection = AugurTaskRoutine(session,repos=repo_git_identifiers,collection_phases=facade_enabled_phases)

    #Start data collection and update the collectionStatus with the task_ids
    for repo_git, task_id in facade_augur_collection.start_data_collection():
        
        repo = session.query(Repo).filter(Repo.repo_git == repo_git).one()

        #set status in database to collecting
        repoStatus = repo.collection_status[0]
        repoStatus.facade_task_id = task_id
        session.commit()

@celery.task
def augur_collection_monitor():     

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(augur_collection_monitor.__name__)

    logger.info("Checking for repos to collect")

    with DatabaseSession(logger, engine) as session:

        start_primary_collection(session, max_repo=50, days=30)
        
        start_secondary_collection(session, max_repo=30, days=30)

        start_facade_collection(session, max_repo=30, days=30)



