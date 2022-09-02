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
from augur.tasks.github.detect_move.tasks import detect_github_repo_move
from augur.tasks.github.releases.tasks import collect_releases
from augur.tasks.github.repo_info.tasks import collect_repo_info
from augur.tasks.git.facade_tasks import *
# from augur.tasks.data_analysis import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.logs import AugurLogger
from augur.application.db.session import DatabaseSession
from augur.tasks.init.celery_app import engine
from logging import Logger

pr_numbers = [70, 106, 170, 190, 192, 208, 213, 215, 216, 218, 223, 224, 226, 230, 237, 238, 240, 241, 248, 249, 250, 252, 253, 254, 255, 256, 257, 261, 268, 270, 273, 277, 281, 283, 288, 291, 303, 306, 309, 310, 311, 323, 324, 325, 334, 335, 338, 343, 346, 348, 350, 353, 355, 356, 357, 359, 360, 365, 369, 375, 381, 382, 388, 405, 408, 409, 410, 414, 418, 419, 420, 421, 422, 424, 425, 431, 433, 438, 445, 450, 454, 455, 456, 457, 460, 463, 468, 469, 470, 474, 475, 476, 477, 478, 479, 480, 481, 482, 484, 485, 486, 487, 488, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 504, 506, 507, 508, 509, 510, 512, 514]

#Predefine phases. For new phases edit this and the config to reflect.
#The domain of tasks ran should be very explicit.
class AugurTaskPhase(Enum):
    """All the differant phases of collection augur goes through in sequence"""

    PRELIMINARY = "Preliminary"
    REPO_COLLECT = "Repo_collect"
    MACHINE_LEARNING = "Machine_learning"
    POST_PHASE = "Post_phase"


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
        preliminary_task_list = [detect_github_repo_move.si()]

        preliminary_tasks = group(preliminary_task_list)
        self.jobs_dict[AugurTaskPhase.PRELIMINARY] = preliminary_tasks
        
        #store all tasks that taks a repo as an argument 
        tasks_with_repo_domain = []
        #A chain is needed for each repo.
        with DatabaseSession(self.logger) as session:
            repos = session.query(Repo).all()

            for repo in repos:
                first_tasks_repo = group(collect_issues.si(repo.repo_id),collect_pull_requests.si(repo.repo_id))
                second_tasks_repo = group(collect_events.si(repo.repo_id),collect_github_messages.si(repo.repo_id))

                repo_chain = chain(first_tasks_repo,second_tasks_repo)
                tasks_with_repo_domain.append(repo_chain)
        
        self.jobs_dict[AugurTaskPhase.REPO_COLLECT] = group(
            chain(group(*tasks_with_repo_domain),process_contributors.si()),
            facade_commits_model.si(),
            collect_releases.si(),
            collect_repo_info.si()
        )

                

    #Get and set dict values that correspond to phases of collection
    def __getitem__(self,key: str) -> dict:
        """Return the collection group with the specified key.
        """
        return self.jobs_dict[key]
    
    def __setitem__(self,key: str,newJobs):
        """Create a new collection job group with the name of the key specified.
        """
        if not hasattr(newJobs, 'apply_async') or not callable(newJobs.apply_async):
            self.logger.error("Collection groups must be of celery types that can be called with \'apply_async\'")
            raise AttributeError 
        
        if key in self.disabled_collection_phases:
            self.logger.error("Group has been disabled")
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
            augur_collection_list.append(job)
        
        augur_collection = chain(*augur_collection_list)
        augur_collection.apply_async()


@celery.task
def start_task():

    logger = logging.getLogger(start_task.__name__)

    default_augur_collection = AugurTaskRoutine()

    default_augur_collection.start_data_collection()

"""
    logger.info(f"Collecting data for git and github...")

    with DatabaseSession(logger) as session:

        repos = session.query(Repo).all()

    #task_list = []
    augur_main_routine = AugurTaskRoutine()

    augur_main_routine['facade'] = facade_commits_model.si()

    issues_and_pr_list = [collect_issues.si(repo.repo_git) for repo in repos]
    issues_and_pr_list.extend([collect_pull_requests.si(repo.repo_git) for repo in repos])

    augur_main_routine['collect_issues_and_pull_requests'] = group(issues_and_pr_list)

    augur_main_routine['collect_events'] = group([collect_events.si(repo.repo_git) for repo in repos])
    augur_main_routine['collect_issue_and_pr_comments'] = group([collect_issue_and_pr_comments.si(repo.repo_git) for repo in repos])

    augur_main_routine['process_contributors'] = process_contributors.si()


    augur_main_routine.add_dependency_relationship(job='collect_events',depends_on='collect_issues_and_pull_requests')
    augur_main_routine.add_dependency_relationship(job='collect_issue_and_pr_comments',depends_on='collect_issues_and_pull_requests')
    augur_main_routine.add_dependency_relationship(job='process_contributors',depends_on='collect_events')
    augur_main_routine.add_dependency_relationship(job='process_contributors',depends_on='collect_issue_and_pr_comments')

    augur_main_routine.logger.info(augur_main_routine.dependency_relationships)
    augur_main_routine.start_data_collection()
    augur_main_routine.logger.info(augur_main_routine.dependency_relationships)
    print('no cycle!')
    
    # routine = AugurTaskRoutine()
    # routine['start'] = chain(start_tasks_group,secondary_task_group)
    # routine.start_data_collection()
"""

def create_github_task_chain(repo_git):

    start_task_list = []
    start_task_list.append(collect_pull_requests.si(repo_git))
    start_task_list.append(collect_issues.si(repo_git))

    start_tasks_group = group(start_task_list)
    
    secondary_task_list = []
    secondary_task_list.append(collect_events.si(repo_git))
    secondary_task_list.append(collect_github_messages.si(repo_git))
    
    secondary_task_group = group(secondary_task_list)

    github_task_chain = chain(
        start_tasks_group, secondary_task_group)

    return github_task_chain


def get_owner_repo(git_url):
    """Gets the owner and repository names of a repository from a git url

    :param git_url: String, the git url of a repository
    :return: Tuple, includes the owner and repository names in that order
    """
    split = git_url.split('/')

    owner = split[-2]
    repo = split[-1]

    if '.git' == repo[-4:]:
        repo = repo[:-4]

    return owner, repo