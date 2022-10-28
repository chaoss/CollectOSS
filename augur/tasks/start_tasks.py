from __future__ import annotations
from typing import List
import time
import logging
import json
from enum import Enum

from celery.result import AsyncResult
from celery import signature
from celery import group, chain, chord, signature


from augur.tasks.github import *
from augur.tasks.data_analysis import *
from augur.tasks.github.detect_move.tasks import detect_github_repo_move
from augur.tasks.github.releases.tasks import collect_releases
from augur.tasks.github.repo_info.tasks import collect_repo_info
from augur.tasks.github.pull_requests.files_model.tasks import process_pull_request_files
from augur.tasks.github.pull_requests.commits_model.tasks import process_pull_request_commits
from augur.tasks.git.facade_tasks import *
# from augur.tasks.data_analysis import *
from augur.tasks.init.celery_app import celery_app as celery
from celery.result import allow_join_result
from augur.application.logs import AugurLogger
from augur.application.db.session import DatabaseSession
from augur.tasks.init.celery_app import engine
from logging import Logger

#Predefine phases. For new phases edit this and the config to reflect.
#The domain of tasks ran should be very explicit.
def prelim_phase(logger):

    tasks_with_repo_domain = []

    with DatabaseSession(logger) as session:
        repos = session.query(Repo).all()

        for repo in repos:
            tasks_with_repo_domain.append(detect_github_repo_move.si(repo.repo_git))

    #preliminary_task_list = [detect_github_repo_move.si()]
    preliminary_tasks = group(*tasks_with_repo_domain)
    return preliminary_tasks

def repo_collect_phase(logger):
    #Here the term issues also includes prs. This list is a bunch of chains that run in parallel to process issue data.
    issue_dependent_tasks = []
    #repo_info should run in a group
    repo_info_tasks = []
    #A chain is needed for each repo.
    with DatabaseSession(logger) as session:
        repos = session.query(Repo).all()
        #Just use list comprehension for simple group
        repo_info_tasks = [collect_repo_info.si(repo.repo_git) for repo in repos]

        for repo in repos:
            first_tasks_repo = group(collect_issues.si(repo.repo_git),collect_pull_requests.si(repo.repo_git))
            second_tasks_repo = group(collect_events.si(repo.repo_git),
                collect_github_messages.si(repo.repo_git),process_pull_request_files.si(repo.repo_git), process_pull_request_commits.si(repo.repo_git))

            repo_chain = chain(first_tasks_repo,second_tasks_repo)
            issue_dependent_tasks.append(repo_chain)
    
    return group(
            *repo_info_tasks,
            chain(group(*issue_dependent_tasks),process_contributors.si()),
            generate_facade_chain(logger),
            collect_releases.si()
        )

def machine_learning_phase(logger):

    with DatabaseSession(logger) as session:
        repos = session.query(Repo).all()

        ml_tasks = []
        clustering_tasks = []
        discourse_tasks = []
        insight_tasks = []
        message_insights_tasks = []
        pull_request_analysis_tasks = []
        for repo in repos:
            clustering_tasks.append(clustering_model.si(repo.repo_git))
            discourse_tasks.append(discourse_analysis_model.si(repo.repo_git))
            insight_tasks.append(insight_model.si(repo.repo_git))
            message_insights_tasks.append(message_insight_model.si(repo.repo_git))
            pull_request_analysis_tasks.append(pull_request_analysis_model.si(repo.repo_git))   

        ml_tasks.extend(clustering_tasks)
        ml_tasks.extend(discourse_tasks)
        ml_tasks.extend(insight_tasks)
        ml_taks.extend(message_insights_tasks)
        ml_taks.extend(pull_request_analysis_tasks)


        return chain(
            *ml_tasks
        )


DEFINED_COLLECTION_PHASES = [prelim_phase, repo_collect_phase, machine_learning_phase]

class AugurTaskRoutine:
    """class to keep track of various groups of collection tasks as well as how they relate to one another.
    Accessible like a dict, each dict item represents a 'phase' of augur collection executed more or less in parallel.

    Attributes:
        logger (Logger): Get logger from AugurLogger
        jobs_dict (dict): Dict of data collection phases to run
        disabled_collection_groups (List[str]): List of keys in jobs dict that have been marked as disabled
    """
    def __init__(self,disabled_collection_phases: List[str]=[], disabled_collection_tasks: List[str]=[]):
        self.logger = AugurLogger("data_collection_jobs").get_logger()
        #self.session = TaskSession(self.logger)
        self.jobs_dict = {}
        self.disabled_collection_phases = disabled_collection_phases
        self.disabled_collection_tasks = disabled_collection_tasks

        #Assemble default phases
        #These will then be able to be overridden through the config.
        if prelim_phase.__name__ not in self.disabled_collection_phases:
            self.jobs_dict[prelim_phase.__name__] = prelim_phase
        
        if repo_collect_phase.__name__ not in self.disabled_collection_phases:
            self.jobs_dict[repo_collect_phase.__name__] = repo_collect_phase

        if machine_learning_phase.__name__ not in self.disabled_collection_phases:
            self.jobs_dict[machine_learning_phase.__name__] = machine_learning_phase

                

    #Get and set dict values that correspond to phases of collection
    def __getitem__(self,key: str) -> dict:
        """Return the collection group with the specified key.
        """
        return self.jobs_dict[key]
    
    def __setitem__(self,key: str,newJobs):
        """Create a new collection job group with the name of the key specified.
        """
        if key in self.disabled_collection_phases:
            self.logger.info(f"Group {key} has been disabled")
            return
        self.jobs_dict[key] = newJobs

    
    def disable_group(self,key: str):
        """Make a group deleted from the dict and unable to be run or added.
        """
        del self.jobs_dict[key]
        self.disabled_collection_phases.append(key)


    def start_data_collection(self):
        """Start all task items and return.
        """
        self.logger.info("Starting augur collection")

        self.logger.info(f"Enabled phases: {self.jobs_dict.keys()}")
        augur_collection_list = []
        for phaseName, job in self.jobs_dict.items():
            self.logger.info(f"Starting phase {phaseName}")
            #Call the function stored in the dict to return the object to call apply_async on
            phaseResult = job(self.logger).apply_async()
            with allow_join_result():
                try:
                    phaseResult.join()
                except Exception as e:
                    #Log full traceback if a phase fails.
                    self.logger.error(
                    ''.join(traceback.format_exception(None, e, e.__traceback__)))
                    self.logger.error(
                        f"Phase {phaseName} has failed during augur collection. Error: {e}")
                    raise e
            #self.logger.info(f"Result of {phaseName} phase: {phaseResult.status}")


@celery.task
def start_task():

    logger = logging.getLogger(start_task.__name__)

    #Get phase options from the config
    with DatabaseSession(logger) as session:
        config = session.config
        phase_options = config.get_section("Task_Routine")

    #Get list of disabled phases
    disabled_phases = [name for name, phase in phase_options.items() if phase == 0]

    #print(f"disabled: {disabled_phases}")
    augur_collection = AugurTaskRoutine(disabled_collection_phases=disabled_phases)

    augur_collection.start_data_collection()


