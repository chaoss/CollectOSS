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
from augur.tasks.init.celery_app import celery_app as celery, engine
from celery.result import allow_join_result
from augur.application.logs import AugurLogger
from augur.application.config import AugurConfig
from augur.application.db.session import DatabaseSession
from augur.tasks.init.celery_app import engine
from augur.application.db.util import execute_session_query
from logging import Logger
from augur.tasks.util.redis_list import RedisList

CELERY_GROUP_TYPE = type(group())
CELERY_CHAIN_TYPE = type(chain())

#Predefine phases. For new phases edit this and the config to reflect.
#The domain of tasks ran should be very explicit.
@celery.task
def prelim_phase():

    logger = logging.getLogger(prelim_phase.__name__)
    
    with DatabaseSession(logger) as session:
        query = session.query(Repo)
        repos = execute_session_query(query, 'all')
        repo_git_list = [repo.repo_git for repo in repos]

        result = create_grouped_task_load(dataList=repo_git_list,task=detect_github_repo_move).apply_async()
        
        with allow_join_result():
            return result.get()

@celery.task
def repo_collect_phase():
    logger = logging.getLogger(repo_collect_phase.__name__)

    #Here the term issues also includes prs. This list is a bunch of chains that run in parallel to process issue data.
    issue_dependent_tasks = []
    #repo_info should run in a group
    repo_info_tasks = []

    np_clustered_array = []

    #A chain is needed for each repo.
    with DatabaseSession(logger) as session:
        query = session.query(Repo)
        repos = execute_session_query(query, 'all')


        all_repo_git_identifiers = [repo.repo_git for repo in repos]
        #Cluster each repo in groups of 80.
        np_clustered_array = np.array_split(all_repo_git_identifiers,math.ceil(len(all_repo_git_identifiers)/80))

        first_pass = np_clustered_array.pop(0).tolist()

        logger.info(f"Scheduling groups of {len(first_pass)}")
        #Pool the tasks for collecting repo info. 
        repo_info_tasks = create_grouped_task_load(dataList=first_pass, task=collect_repo_info).tasks

        #pool the repo collection jobs that should be ran first and have deps. 
        primary_repo_jobs = group(
            *create_grouped_task_load(dataList=first_pass, task=collect_issues).tasks,
            *create_grouped_task_load(dataList=first_pass, task=collect_pull_requests).tasks
        )

        secondary_repo_jobs = group(
            *create_grouped_task_load(dataList=first_pass, task=collect_events).tasks,
            *create_grouped_task_load(dataList=first_pass,task=collect_github_messages).tasks,
            *create_grouped_task_load(dataList=first_pass, task=process_pull_request_files).tasks,
            *create_grouped_task_load(dataList=first_pass, task=process_pull_request_commits).tasks
        )
        

        repo_task_group = group(
            *repo_info_tasks,
            chain(primary_repo_jobs,secondary_repo_jobs,process_contributors.si()),
            chain(generate_facade_chain(logger,first_pass),create_grouped_task_load(dataList=first_pass,task=process_dependency_metrics)),
            collect_releases.si()
        )
    
    result = chain(repo_task_group, refresh_materialized_views.si()).apply_async()
    
    with allow_join_result():
        result.wait()

    if len(np_clustered_array) == 0:
        return
    

    for cluster in np_clustered_array:
        additionalPass = cluster.tolist()
        #Pool the tasks for collecting repo info. 
        repo_info_tasks = create_grouped_task_load(dataList=additionalPass, task=collect_repo_info).tasks

        #pool the repo collection jobs that should be ran first and have deps. 
        primary_repo_jobs = group(
            *create_grouped_task_load(dataList=additionalPass, task=collect_issues).tasks,
            *create_grouped_task_load(dataList=additionalPass, task=collect_pull_requests).tasks
        )

        secondary_repo_jobs = group(
            *create_grouped_task_load(dataList=additionalPass, task=collect_events).tasks,
            *create_grouped_task_load(dataList=additionalPass,task=collect_github_messages).tasks,
            *create_grouped_task_load(dataList=additionalPass, task=process_pull_request_files).tasks,
            *create_grouped_task_load(dataList=additionalPass, task=process_pull_request_commits).tasks
        )
        
        repo_task_group = group(
            *repo_info_tasks,
            chain(primary_repo_jobs,secondary_repo_jobs,process_contributors.si()),
            generate_facade_chain(logger,additionalPass),
            *create_grouped_task_load(dataList=additionalPass,task=process_dependency_metrics).tasks
        )

        result = chain(repo_task_group, refresh_materialized_views.si()).apply_async()
    
        with allow_join_result():
            result.wait()

    return 


DEFINED_COLLECTION_PHASES = [prelim_phase, repo_collect_phase]
if os.environ.get('AUGUR_DOCKER_DEPLOY') != "1":
    DEFINED_COLLECTION_PHASES.append(machine_learning_phase)


class AugurTaskRoutine:
    """class to keep track of various groups of collection tasks as well as how they relate to one another.
    Accessible like a dict, each dict item represents a 'phase' of augur collection executed more or less in parallel.

    Attributes:
        logger (Logger): Get logger from AugurLogger
        jobs_dict (dict): Dict of data collection phases to run
        collection_phases (List[str]): List of phases to run in augur collection.
    """
    def __init__(self,collection_phases: List[str]=[]):
        self.logger = AugurLogger("data_collection_jobs").get_logger()
        #self.session = TaskSession(self.logger)
        self.jobs_dict = {}
        self.collection_phases = collection_phases
        #self.disabled_collection_tasks = disabled_collection_tasks

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

        augur_collection_sequence = []
        for phaseName, job in self.jobs_dict.items():
            self.logger.info(f"Queuing phase {phaseName}")
            
            #Add the phase to the sequence in order as a celery task.
            #The preliminary task creates the larger task chain 
            augur_collection_sequence.append(job.si())
        
        #Link all phases in a chain and send to celery
        augur_collection_chain = chain(*augur_collection_sequence)
        augur_collection_chain.apply_async()

"""
@celery.task
def start_task():

    logger = logging.getLogger(start_task.__name__)

    #Get phase options from the config
    with DatabaseSession(logger, engine) as session:
        config = AugurConfig(logger, session)
        phase_options = config.get_section("Task_Routine")

    #Get list of enabled phases 
    enabled_phase_names = [name for name, phase in phase_options.items() if phase == 1]
    enabled_phases = [phase for phase in DEFINED_COLLECTION_PHASES if phase.__name__ in enabled_phase_names]

    #print(f"disabled: {disabled_phases}")
    augur_collection = AugurTaskRoutine(collection_phases=enabled_phases)

    augur_collection.start_data_collection()
"""

task_list_name = "augur_task_ids"

#Wrap each task in a bind celery task to return its id
@celery.task()
def collection_task_wrapper(self,*args,**kwargs):
    task = kwargs.pop('task')

    task(*args,**kwargs)

    return self.request.id


@celery.task
def task_success(successResult):
    logger = logging.getLogger(successResult.__name__)

    # remove the task id from Redis
    task_id_list = RedisList(task_list_name)
    try:
        task_id_list.remove(successResult)
    except Exception as e:
        logger.error(f"Could not remove id {successResult} from redis. Error: {e}")
    
    # set status to Finished in db
    # set collection date in db


@celery.task
def task_failed(request,exc,traceback):
    logger = logging.getLogger(task_failed.__name__)

    # remove the task id from Redis
    task_id_list = RedisList(task_list_name)
    try:
        task_id_list.remove(successResult)
    except Exception as e:
        logger.error(f"Could not remove id {successResult} from redis. Error: {e}")
    
    # set status to Error in db
    # log traceback to error file


@celery.task
def augur_collection_monitor():           
    raise NotImplementedError
    # calculate current active repos
    # calcuate the number of repos we would like to add to the queue

    # get repos with these requirements
        # haven't been collected or not collected in awhile
        # don't have a status of Error or Collecting

    # loop through repos
        # create chain
        # start task
        # set status in db to Collecting




