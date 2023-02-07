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
from augur.tasks.github.detect_move.tasks import detect_github_repo_move
from augur.tasks.github.releases.tasks import collect_releases
from augur.tasks.github.repo_info.tasks import collect_repo_info
from augur.tasks.github.pull_requests.files_model.tasks import process_pull_request_files
from augur.tasks.github.pull_requests.commits_model.tasks import process_pull_request_commits
from augur.tasks.git.dependency_tasks.tasks import process_dependency_metrics
from augur.tasks.git.facade_tasks import *
from augur.tasks.db.refresh_materialized_views import *
# from augur.tasks.data_analysis import *
from augur.tasks.init.celery_app import celery_app as celery
from celery.result import allow_join_result
from augur.application.logs import AugurLogger
from augur.application.config import AugurConfig
from augur.application.db.session import DatabaseSession
from augur.application.db.engine import DatabaseEngine
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

"""
@celery.task(bind=True)
def collection_task_wrapper(self,*args,**kwargs):
    task = kwargs.pop('task')

    task(*args,**kwargs)

    return self.request.id
"""

@celery.task
def task_success(repo_git):

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(task_success.__name__)

    logger.info(f"Repo '{repo_git}' succeeded")

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
def task_failed(request,exc,traceback):

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(task_failed.__name__)
    
    with DatabaseSession(logger,engine) as session:
        query = session.query(CollectionStatus).filter(CollectionStatus.core_task_id == request.id)

        collectionRecord = execute_session_query(query,'one')

        print(f"chain: {request.chain}")
        #Make sure any further execution of tasks dependent on this one stops.
        try:
            #Replace the tasks queued ahead of this one in a chain with None.
            request.chain = None
        except AttributeError:
            pass #Task is not part of a chain. Normal so don't log.
        except Exception as e:
            logger.error(f"Could not mutate request chain! \n Error: {e}")
        
        if collectionRecord.core_status == CollectionState.COLLECTING.value:
            # set status to Error in db
            collectionRecord.core_status = CollectionStatus.ERROR
            session.commit()

            # log traceback to error file
            session.logger.error(f"Task {request.id} raised exception: {exc}\n{traceback}")
    
    


#Predefine phases. For new phases edit this and the config to reflect.
#The domain of tasks ran should be very explicit.
def prelim_phase(repo_git):

    logger = logging.getLogger(prelim_phase.__name__)
    job = None
    with DatabaseEngine() as engine, DatabaseSession(logger, engine) as session:
        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')

        job = detect_github_repo_move.si(repo_obj.repo_git)

        

    return job


def repo_collect_phase(repo_git):
    logger = logging.getLogger(repo_collect_phase.__name__)

    #Here the term issues also includes prs. This list is a bunch of chains that run in parallel to process issue data.
    issue_dependent_tasks = []
    #repo_info should run in a group
    repo_info_tasks = []

    np_clustered_array = []

    #A chain is needed for each repo.
    with DatabaseEngine() as engine, DatabaseSession(logger, engine) as session:
        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_git = repo_obj.repo_git

        repo_info_task = collect_repo_info.si(repo_git)#collection_task_wrapper(self)

        primary_repo_jobs = group(
            collect_issues.si(repo_git),
            collect_pull_requests.si(repo_git)
        )

        secondary_repo_jobs = group(
            collect_events.si(repo_git),#*create_grouped_task_load(dataList=first_pass, task=collect_events).tasks,
            collect_github_messages.si(repo_git),#*create_grouped_task_load(dataList=first_pass,task=collect_github_messages).tasks,
            process_pull_request_files.si(repo_git),#*create_grouped_task_load(dataList=first_pass, task=process_pull_request_files).tasks,
            process_pull_request_commits.si(repo_git)#*create_grouped_task_load(dataList=first_pass, task=process_pull_request_commits).tasks
        )

        repo_task_group = group(
            repo_info_task,
            chain(primary_repo_jobs,secondary_repo_jobs,process_contributors.si()),
            chain(generate_facade_chain(logger,repo_git),process_dependency_metrics.si(repo_git)),
            collect_releases.si(repo_git)
        )

        return repo_task_group


DEFINED_PHASES_PER_REPO = [prelim_phase, repo_collect_phase]


class AugurTaskRoutine:
    """class to keep track of various groups of collection tasks as well as how they relate to one another.
    Accessible like a dict, each dict item represents a 'phase' of augur collection executed more or less in parallel.

    Attributes:
        logger (Logger): Get logger from AugurLogger
        jobs_dict (dict): Dict of data collection phases to run
        repos (List[int]): List of repo_ids to run collection on.
        collection_phases (List[str]): List of phases to run in augur collection.
        session: Database session to use
    """
    def __init__(self,session,repos: List[int]=[],collection_phases: List[str]=[]):
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

        
        
        for repo_id in self.repos:

            repo = self.session.query(Repo).filter(Repo.repo_id == repo_id).one()
            repo_git = repo.repo_git

            augur_collection_sequence = []
            for phaseName, job in self.jobs_dict.items():
                self.logger.info(f"Queuing phase {phaseName} for repo {repo_git}")
                
                #Add the phase to the sequence in order as a celery task.
                #The preliminary task creates the larger task chain 
                augur_collection_sequence.append(job(repo_git))

            augur_collection_sequence.append(task_success.si(repo_git))
            #Link all phases in a chain and send to celery
            augur_collection_chain = chain(*augur_collection_sequence)
            task_id = augur_collection_chain.apply_async(link_error=task_failed.s()).task_id

            self.logger.info(f"Setting repo_id {repo_id} to collecting")

            #set status in database to collecting
            repoStatus = repo.collection_status[0]
            repoStatus.core_task_id = task_id
            repoStatus.core_status = CollectionState.COLLECTING.value
            self.session.commit()

@celery.task
def non_repo_domain_tasks():

    from augur.tasks.init.celery_app import engine


    logger = logging.getLogger(non_repo_domain_tasks.__name__)

    logger.info("Executing non-repo domain tasks")

    enabled_phase_names = []
    with DatabaseSession(logger, engine) as session:

        max_repo_count = 500
        days = 30

        config = AugurConfig(logger, session)
        phase_options = config.get_section("Task_Routine")

        #Get list of enabled phases 
        enabled_phase_names = [name for name, phase in phase_options.items() if phase == 1]

    enabled_tasks = []

    enabled_tasks.extend(generate_non_repo_domain_facade_tasks(logger))

    if machine_learning_phase.__name__ in enabled_phase_names:
        enabled_tasks.append(machine_learning_phase.si())

    tasks = chain(
        *enabled_tasks
    )

    tasks.apply_async()



@celery.task
def augur_collection_monitor():     

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(augur_collection_monitor.__name__)

    logger.info("Checking for repos to collect")

    #Get phase options from the config
    with DatabaseSession(logger, engine) as session:

        max_repo_count = 50
        days = 30

        config = AugurConfig(logger, session)
        phase_options = config.get_section("Task_Routine")

        #Get list of enabled phases 
        enabled_phase_names = [name for name, phase in phase_options.items() if phase == 1]
        enabled_phases = [phase for phase in DEFINED_PHASES_PER_REPO if phase.__name__ in enabled_phase_names]
        
        active_repo_count = len(session.query(CollectionStatus).filter(CollectionStatus.core_status == CollectionState.COLLECTING.value).all())

        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        not_erroed = CollectionStatus.core_status != str(CollectionState.ERROR.value)
        not_collecting = CollectionStatus.core_status != str(CollectionState.COLLECTING.value)
        never_collected = CollectionStatus.core_data_last_collected == None
        old_collection = CollectionStatus.core_data_last_collected <= cutoff_date

        limit = max_repo_count-active_repo_count

        repo_status_list = session.query(CollectionStatus).filter(and_(not_erroed, not_collecting, or_(never_collected, old_collection))).limit(limit).all()

        repo_ids = [repo.repo_id for repo in repo_status_list]

        logger.info(f"Starting collection on {len(repo_ids)} repos")

        augur_collection = AugurTaskRoutine(session,repos=repo_ids,collection_phases=enabled_phases)
        augur_collection.start_data_collection()



