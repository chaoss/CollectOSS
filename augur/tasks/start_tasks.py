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
from augur.tasks.git.facade_tasks import *
# from augur.tasks.data_analysis import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.logs import AugurLogger
from augur.application.db.session import DatabaseSession
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
        started_jobs (List[str]): List of keys in jobs_dict that have been started
        disabled_collection_groups (List[str]): List of keys in jobs dict that have been marked as disabled
    """
    def __init__(self,disabled_collection_phases: List[str]=[], disabled_collection_tasks: List[str]=[]):
        self.logger = AugurLogger("data_collection_jobs").get_logger()
        #self.session = TaskSession(self.logger)
        self.jobs_dict = {}
        self.started_jobs = []
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
                second_tasks_repo = group(collect_events.si(repo.repo_id),collect_issue_and_pr_comments.si(repo.repo_id))

                repo_chain = chain(first_tasks_repo,second_tasks_repo)
                all_task_by_repo_list.append(repo_chain)
        
        self.jobs_dict[AugurTaskPhase.REPO_COLLECT] = chain(
                group(facade_commits_model.si(),*all_task_by_repo_list),
                process_contributors.si())

                

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
        self.dependency_relationships[key] = []

    
    def disable_group(self,key: str):
        """Make a group deleted from the dict and unable to be run or added.
        """
        del self.jobs_dict[key]
        del self.dependency_relationships[key]
        self.disabled_collection_phases.append(key)

    #force these params to be kwargs so they are more readable
    def add_dependency_relationship(self,job=None,depends_on=None):
        """Mark one key in the outfacing dictionary to be dependent on a differant item with the other specified key. Set up one to listen for the other to finish before starting.
        """
        assert (job in self.jobs_dict.keys() and depends_on in self.jobs_dict.keys()), "One or both collection groups don't exist!"
        assert (job != depends_on), "Something can not depend on itself!"

        self.dependency_relationships[job].append(depends_on)
    
    def _update_dependency_relationship_with_celery_id(self,celery_id: str,dependency_name: str):
        """One a task is ran it is assigned a uuid by celery to represent the instance that is now running. 
        This replaces the dependency relationship to reflect a now-running task as what is actually being 
        waited on for dependencies. Now the id can be passed to a listener.
        """
        #Replace dependency with active celery id once started so that dependent tasks can check status
        for group_name in self.dependency_relationships.keys():
            #self.dependency_relationships[group_name] = [celery_id if item == name else item for item in self.dependency_relationships[group_name]]
            for index,item in enumerate(self.dependency_relationships[group_name]):
                if item == dependency_name:
                    self.dependency_relationships[group_name][index] = celery_id    
                    break #break once dependency_name found. Should only occur once.


    def start_data_collection(self):
        """Start all task items and listeners and return.
        """
        #First, start all task groups that have no dependencies. 
        for name, collection_set in self.jobs_dict.items():
            if not len(self.dependency_relationships[name]):
                self.logger.info(f"Starting non dependant collection group {name}...")
                self.started_jobs.append(name)
                task_collection = collection_set.apply_async()
                
                self._update_dependency_relationship_with_celery_id(task_collection.id,name)
        
        #Then try to go after tasks with dependencies.
        #'loop while there are elements of the jobs dict that haven't been started'
        while not all(job_name in self.started_jobs for job_name in self.jobs_dict.keys()):
            for name in self.dependency_relationships.keys():
                #Check that task group has no dependencies that haven't been started yet and that it has not already been started.
                if not any(group_key in self.dependency_relationships[name] for group_key in list(self.jobs_dict.keys())) and not name in self.started_jobs:
                    self.started_jobs.append(name)
                    self.logger.info(f"Starting dependant collection group {name}...")
                    dependent_task_collection = deploy_dependent_task.si(*self.dependency_relationships[name],task_set=self.jobs_dict[name])
                    result = dependent_task_collection.apply_async()
                    print(result)

                    self._update_dependency_relationship_with_celery_id(result.id,name)
                
            
            #if dependency_cycle:
            #    raise Exception("Task group dependency cycle found as all pending tasks have prereqs that cannot be run.")




@celery.task
def start_task():

    logger = logging.getLogger(start_task.__name__)

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
    secondary_task_list.append(collect_issue_and_pr_comments.si(repo_git))
    
    secondary_task_group = group(secondary_task_list)

    github_task_chain = chain(start_tasks_group, secondary_task_group)

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