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
from augur.tasks.github.repo_info.tasks import collect_repo_info
from augur.tasks.github.pull_requests.files_model.tasks import process_pull_request_files
from augur.tasks.github.pull_requests.commits_model.tasks import process_pull_request_commits
from augur.tasks.git.dependency_tasks.tasks import process_ossf_scorecard_metrics
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
        collect_github_messages.si(repo_git), #*create_grouped_task_load(dataList=first_pass,task=collect_github_messages).tasks,
        collect_github_repo_clones_data.si(repo_git),
    )

    repo_task_group = group(
        repo_info_task,
        chain(primary_repo_jobs | issue_pr_task_update_weight_util.s(repo_git=repo_git),secondary_repo_jobs,process_contributors.si()),
        #facade_phase(logger,repo_git),
        
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
        process_ossf_scorecard_metrics.si(repo_git),
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

    active_repo_count = len(session.query(CollectionStatus).filter(CollectionStatus.core_status == CollectionState.COLLECTING.value).all())

    not_erroed = CollectionStatus.core_status != str(CollectionState.ERROR.value)
    not_collecting = CollectionStatus.core_status != str(CollectionState.COLLECTING.value)

    limit = max_repo-active_repo_count

    #Split users that have new repos into four lists and randomize order
    query = s.sql.text("""
        SELECT  
        user_id
        FROM augur_operations.user_groups 
        JOIN augur_operations.user_repos ON augur_operations.user_groups.group_id = augur_operations.user_repos.group_id
        JOIN augur_data.repo ON augur_operations.user_repos.repo_id = augur_data.repo.repo_id
        JOIN augur_operations.collection_status ON augur_operations.user_repos.repo_id = augur_operations.collection_status.repo_id
        WHERE core_status='Pending'
        GROUP BY user_id
    """)

    user_list = session.execute_sql(query).fetchall()
    random.shuffle(user_list)

    #Extract the user id from the randomized list and split into four chunks
    split_user_list = split_list_into_chunks([row[0] for row in user_list], 4)

    session.logger.info(f"User_list: {split_user_list}")
    for quarter_list in split_user_list:
        if limit <= 0:
            return

        repo_query = s.sql.text("""
            SELECT
	        repo.repo_id
            FROM augur_operations.user_groups 
            JOIN augur_operations.user_repos ON augur_operations.user_groups.group_id = augur_operations.user_repos.group_id
            JOIN augur_data.repo ON augur_operations.user_repos.repo_id = augur_data.repo.repo_id
            JOIN augur_operations.collection_status ON augur_operations.user_repos.repo_id = augur_operations.collection_status.repo_id
            WHERE user_id IN :list_of_user_ids
            ORDER BY core_weight
        """).bindparams(list_of_user_ids=tuple(quarter_list))

        valid_repos = session.execute_sql(repo_query).fetchall()
        valid_repo_git_ids = [repo[0] for repo in valid_repos]

        session.logger.info(f"valid repo git ids: {tuple(valid_repo_git_ids)}")
        never_collected = CollectionStatus.core_data_last_collected == None
        make_sure_valid_repo = CollectionStatus.repo_id.in_(list(valid_repo_git_ids))


        core_order = CollectionStatus.core_weight

        #Get repos for primary collection hook
        collection_size = start_block_of_repos(
            session.logger, session,
            and_(not_erroed, not_collecting,never_collected,make_sure_valid_repo),
            limit, primary_enabled_phases, repos_type="new", sort=core_order
        )
        
        limit -= collection_size

    #Now start old repos if there is space to do so.
    query = s.sql.text("""
        SELECT  
        user_id
        FROM augur_operations.users
    """)

    user_list = session.execute_sql(query).fetchall()
    random.shuffle(user_list)

    #Extract the user id from the randomized list and split into four chunks
    split_user_list = split_list_into_chunks([row[0] for row in user_list], 4)

    for quarter_list in split_user_list:
        if limit > 0:
            repo_query = s.sql.text("""
                SELECT
	            repo.repo_id
                FROM augur_operations.user_groups 
                JOIN augur_operations.user_repos ON augur_operations.user_groups.group_id = augur_operations.user_repos.group_id
                JOIN augur_data.repo ON augur_operations.user_repos.repo_id = augur_data.repo.repo_id
                JOIN augur_operations.collection_status ON augur_operations.user_repos.repo_id = augur_operations.collection_status.repo_id
                WHERE user_id IN :list_of_user_ids
                ORDER BY core_weight
            """).bindparams(list_of_user_ids=tuple(quarter_list))

            valid_repos = session.execute_sql(repo_query).fetchall()
            valid_repo_git_ids = [repo[0] for repo in valid_repos]


            #only start repos older than the specified amount of days
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_until_collect_again)

            collected_before = CollectionStatus.core_data_last_collected != None
            make_sure_valid_repo = CollectionStatus.repo_id.in_(list(valid_repo_git_ids))
            old_enough = CollectionStatus.core_data_last_collected <= cutoff_date

            collection_size = start_block_of_repos(
                session.logger, session,
                and_(not_erroed, not_collecting,collected_before,old_enough,make_sure_valid_repo),
                limit, primary_enabled_phases, repos_type="old", sort=core_order
            )

            limit -= collection_size
        else:
            return


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

    active_repo_count = len(session.query(CollectionStatus).filter(CollectionStatus.secondary_status == CollectionState.COLLECTING.value).all())

    not_erroed = CollectionStatus.secondary_status != str(CollectionState.ERROR.value)
    not_collecting = CollectionStatus.secondary_status != str(CollectionState.COLLECTING.value)
    primary_collected = CollectionStatus.core_status == str(CollectionState.SUCCESS.value)
    never_collected = CollectionStatus.secondary_data_last_collected == None

    limit = max_repo-active_repo_count

    secondary_order = CollectionStatus.secondary_weight

    collection_size = start_block_of_repos(
        session.logger, session, 
        and_(primary_collected,not_erroed, not_collecting,never_collected), 
        limit, secondary_enabled_phases,
        repos_type="new",
        hook="secondary",
        sort=secondary_order
    )

    limit -= collection_size

    if limit > 0:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_until_collect_again)

        collected_before = CollectionStatus.secondary_data_last_collected != None
        old_enough = CollectionStatus.core_data_last_collected <= cutoff_date

        start_block_of_repos(
            session.logger, session, 
            and_(primary_collected,not_erroed, not_collecting,collected_before,old_enough), 
            limit, secondary_enabled_phases,
            repos_type="old",
            hook="secondary",
            sort=secondary_order
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
    not_erroed = CollectionStatus.facade_status != str(CollectionState.ERROR.value)
    not_pending = CollectionStatus.facade_status != str(CollectionState.PENDING.value)
    not_failed_clone = CollectionStatus.facade_status != str(CollectionState.FAILED_CLONE.value)
    not_collecting = CollectionStatus.facade_status != str(CollectionState.COLLECTING.value)
    not_initializing = CollectionStatus.facade_status != str(CollectionState.INITIALIZING.value)
    never_collected = CollectionStatus.facade_data_last_collected == None

    limit = max_repo

    facade_order = CollectionStatus.facade_weight

    collection_size = start_block_of_repos(
        session.logger, session,
        and_(not_pending,not_failed_clone,not_erroed, not_collecting, not_initializing,never_collected),
        limit, facade_enabled_phases,
        repos_type="new",
        hook="facade",
        sort=facade_order
    )

    limit -= collection_size

    if limit > 0:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_until_collect_again)

        collected_before = CollectionStatus.facade_data_last_collected != None
        old_enough = CollectionStatus.core_data_last_collected <= cutoff_date

        start_block_of_repos(
            session.logger, session,
            and_(not_pending,not_failed_clone,not_erroed, not_collecting, not_initializing,collected_before,old_enough),
            limit, facade_enabled_phases,
            repos_type="old",
            hook="facade",
            sort=facade_order
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
            pass#start_secondary_collection(session, max_repo=10)

        if facade_phase.__name__ in enabled_phase_names:
            pass#start_facade_collection(session, max_repo=30)
           


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

@celery.task
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