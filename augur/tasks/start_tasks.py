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
from augur.tasks.git.dependency_tasks.tasks import process_dependency_metrics
from augur.tasks.git.dependency_libyear_tasks.tasks import process_libyear_dependency_metrics
from augur.tasks.git.facade_tasks import *
from augur.tasks.db.refresh_materialized_views import *
# from augur.tasks.data_analysis import *
from augur.tasks.init.celery_app import celery_app as celery
from celery.result import allow_join_result
from augur.application.logs import AugurLogger
from augur.application.config import AugurConfig
from augur.application.db.session import DatabaseSession
from augur.application.db.util import execute_session_query
from logging import Logger
from enum import Enum
from augur.tasks.util.redis_list import RedisList
from augur.application.db.models import CollectionStatus, Repo

CELERY_GROUP_TYPE = type(group())
CELERY_CHAIN_TYPE = type(chain())


# class syntax
class CollectionState(Enum):
    SUCCESS = "Success"
    PENDING = "Pending"
    ERROR = "Error"
    COLLECTING = "Collecting"
    UPDATE = "Update"
    FAILED_CLONE = "Failed Clone"

"""
@celery.task(bind=True)
def collection_task_wrapper(self,*args,**kwargs):
    task = kwargs.pop('task')

    task(*args,**kwargs)

    return self.request.id
"""

@celery.task
def core_task_success(repo_git):

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(core_task_success.__name__)

    logger.info(f"Repo '{repo_git}' succeeded through core collection")

    with DatabaseSession(logger, engine) as session:

        repo = Repo.get_by_repo_git(session, repo_git)
        if not repo:
            raise Exception(f"Task with repo_git of {repo_git} but could not be found in Repo table")

        collection_status = repo.collection_status[0]

        collection_status.core_status = CollectionState.SUCCESS.value
        collection_status.core_data_last_collected = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        collection_status.core_task_id = None

        session.commit()

@celery.task
def secondary_task_success(repo_git):

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(secondary_task_success.__name__)

    logger.info(f"Repo '{repo_git}' succeeded through secondary collection")

    with DatabaseSession(logger, engine) as session:

        repo = Repo.get_by_repo_git(session, repo_git)
        if not repo:
            raise Exception(f"Task with repo_git of {repo_git} but could not be found in Repo table")

        collection_status = repo.collection_status[0]

        collection_status.secondary_status = CollectionState.SUCCESS.value
        collection_status.secondary_data_last_collected	 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        collection_status.secondary_task_id = None

        session.commit()

@celery.task
def facade_task_success(repo_git):

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(facade_task_success.__name__)

    logger.info(f"Repo '{repo_git}' succeeded through facade task collection")

    with DatabaseSession(logger, engine) as session:

        repo = Repo.get_by_repo_git(session, repo_git)
        if not repo:
            raise Exception(f"Task with repo_git of {repo_git} but could not be found in Repo table")

        collection_status = repo.collection_status[0]

        collection_status.facade_status = CollectionState.SUCCESS.value
        collection_status.facade_data_last_collected = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        collection_status.facade_task_id = None

        session.commit()

@celery.task
def task_failed(request,exc,traceback):

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(task_failed.__name__)

    # log traceback to error file
    logger.error(f"Task {request.id} raised exception: {exc}\n{traceback}")
    
    with DatabaseSession(logger,engine) as session:
        core_id_match = CollectionStatus.core_task_id == request.id
        secondary_id_match = CollectionStatus.secondary_task_id == request.id
        facade_id_match = CollectionStatus.facade_task_id == request.id

        query = session.query(CollectionStatus).filter(or_(core_id_match,secondary_id_match,facade_id_match))

        print(f"chain: {request.chain}")
        #Make sure any further execution of tasks dependent on this one stops.
        try:
            #Replace the tasks queued ahead of this one in a chain with None.
            request.chain = None
        except AttributeError:
            pass #Task is not part of a chain. Normal so don't log.
        except Exception as e:
            logger.error(f"Could not mutate request chain! \n Error: {e}")
        
        try:
            collectionRecord = execute_session_query(query,'one')
        except:
            #Exit if we can't find the record.
            return
        
        if collectionRecord.core_task_id == request.id:
            # set status to Error in db
            collectionRecord.core_status = CollectionStatus.ERROR.value
            collectionRecord.core_task_id = None
        

        if collectionRecord.secondary_task_id == request.id:
            # set status to Error in db
            collectionRecord.secondary_status = CollectionStatus.ERROR.value
            collectionRecord.secondary_task_id = None
            
        
        if collectionRecord.facade_task_id == request.id:
            collectionRecord.facade_status = CollectionStatus.ERROR.value
            collectionRecord.facade_task_id = None
        
        session.commit()
    
    


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
        process_dependency_metrics.si(repo_git),
        process_libyear_dependency_metrics.si(repo_git),
        collect_releases.si(repo_git)
    )

    return repo_task_group


def secondary_repo_collect_phase(repo_git):
    logger = logging.getLogger(secondary_repo_collect_phase.__name__)

    repo_task_group = group(
        process_pull_request_files.si(repo_git),
        process_pull_request_commits.si(repo_git)
    )

    return repo_task_group


class AugurTaskRoutine:
    """class to keep track of various groups of collection tasks as well as how they relate to one another.
    Accessible like a dict, each dict item represents a 'phase' of augur collection executed more or less in parallel.

    Attributes:
        logger (Logger): Get logger from AugurLogger
        jobs_dict (dict): Dict of data collection phases to run
        repos (List[str]): List of repo_ids to run collection on.
        collection_phases (List[str]): List of phases to run in augur collection.
        session: Database session to use
    """
    def __init__(self,session,repos: List[str]=[],collection_phases: List[str]=[]):
        self.logger = AugurLogger("data_collection_jobs").get_logger()
        #self.session = TaskSession(self.logger)
        self.jobs_dict = {}
        self.collection_phases = collection_phases
        #self.disabled_collection_tasks = disabled_collection_tasks
        self.repos = repos
        self.session = session

        #Assemble default phases
        #These will then be able to be overridden through the config.
        for phase in collection_phases:
            self.jobs_dict[phase.__name__] = phase

    #Get and set dict values that correspond to phases of collection
    def __getitem__(self,key: str) -> dict:
        """Return the collection group with the specified key.
        """
        return self.jobs_dict[key]
    
    def __setitem__(self,key: str,newJobs):
        """Create a new collection job group with the name of the key specified.
        """
        self.collection_phases.append(newJobs)
        self.jobs_dict[key] = newJobs

    def start_data_collection(self):
        """Start all task items and return.
        """
        self.logger.info("Starting augur collection")

        self.logger.info(f"Enabled phases: {list(self.jobs_dict.keys())}")
        augur_collection_list = []
        
        for repo_git in self.repos:

            repo = self.session.query(Repo).filter(Repo.repo_git == repo_git).one()
            repo_id = repo.repo_id

            augur_collection_sequence = []
            for phaseName, job in self.jobs_dict.items():
                self.logger.info(f"Queuing phase {phaseName} for repo {repo_git}")
                
                #Add the phase to the sequence in order as a celery task.
                #The preliminary task creates the larger task chain 
                augur_collection_sequence.append(job(repo_git))

            #augur_collection_sequence.append(core_task_success.si(repo_git))
            #Link all phases in a chain and send to celery
            print(augur_collection_sequence)
            augur_collection_chain = chain(*augur_collection_sequence)
            task_id = augur_collection_chain.apply_async(link_error=task_failed.s()).task_id

            self.logger.info(f"Setting repo_id {repo_id} to collecting for repo: {repo_git}")

            #yield the value of the task_id to the calling method so that the proper collectionStatus field can be updated
            yield repo_git, task_id

def get_enabled_phase_names_from_config(logger, session):

    config = AugurConfig(logger, session)
    phase_options = config.get_section("Task_Routine")

    #Get list of enabled phases 
    enabled_phase_names = [name for name, phase in phase_options.items() if phase == 1]

    return enabled_phase_names



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


#Query db for CollectionStatus records that fit the desired condition.
#Used to get CollectionStatus for differant collection hooks
def get_collection_status_repo_git_from_filter(session,filter_condition,limit):
    repo_status_list = session.query(CollectionStatus).filter(filter_condition).limit(limit).all()

    return [status.repo.repo_git for status in repo_status_list]


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



