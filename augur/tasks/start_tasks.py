from __future__ import annotations
from typing import List
import time
import logging
import json

from celery.result import AsyncResult
from celery.result import allow_join_result
from celery import signature
from celery import group, chain, chord, signature


from augur.tasks.github import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.logs import AugurLogger

pr_numbers = [70, 106, 170, 190, 192, 208, 213, 215, 216, 218, 223, 224, 226, 230, 237, 238, 240, 241, 248, 249, 250, 252, 253, 254, 255, 256, 257, 261, 268, 270, 273, 277, 281, 283, 288, 291, 303, 306, 309, 310, 311, 323, 324, 325, 334, 335, 338, 343, 346, 348, 350, 353, 355, 356, 357, 359, 360, 365, 369, 375, 381, 382, 388, 405, 408, 409, 410, 414, 418, 419, 420, 421, 422, 424, 425, 431, 433, 438, 445, 450, 454, 455, 456, 457, 460, 463, 468, 469, 470, 474, 475, 476, 477, 478, 479, 480, 481, 482, 484, 485, 486, 487, 488, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 504, 506, 507, 508, 509, 510, 512, 514]

def deserialize_task_set(dict_obj):

    if dict_obj['task'] == 'celery.group' or dict_obj['task'] == 'celery.chain':
        #return group(dict(dict_obj))
        task_list = []
        for task in dict_obj['kwargs']['tasks']:
            task_list.append(signature(dict(task)))
        
        return group(task_list) if dict_obj['task'] == 'celery.group' else chain(task_list)
    else:
        #assume its a signature
        return signature(dict(dict_obj))



#Use this task to listen for other tasks before deploying.
#NOTE: celery pickles signature objects as dicts
@celery.task
def deploy_dependent_task(*args,task_set,bind=True):
    logger = logging.getLogger(deploy_dependent_task.__name__)

    logger.info(f"Ids are {args}...")
    for task_id in args:
        prereq = AsyncResult(str(task_id))
        print(prereq.status)
        with allow_join_result():
            prereq.wait()
    
    #The convention now is to just add the string 'child' after the autogen'd
    #parent task id to be consistant.
    to_execute = deserialize_task_set(task_set)

    child = to_execute.apply_async(task_id=(deploy_dependent_task.request.id + "child"))

    if bind:
        with allow_join_result():
            child.wait()#Return when the child does so that tasks that are dependent on this dependent task can know when it is complete.


#Class to control what tasks are run when the augur collection is started.
#Groups are run asynchronously 

#routine = AugurTaskRoutine()
#routine['facade'] = facade_commits_model.si()
#routine['my_task_set'] = group(some_tasks)
#routine.add_dependency_relationship('my_task_set','facade')
#routine.start()
class AugurTaskRoutine:

    def __init__(self,disabled_collection_groups: List[str]=[]):
        self.logger = AugurLogger("data_collection_jobs").get_logger()
        #self.session = TaskSession(self.logger)
        self.jobs_dict = {}
        self.started_jobs = []
        self.disabled_collection_groups = disabled_collection_groups

        self.dependency_relationships = {}

    @classmethod
    def from_json(cls,routine_as_json) -> AugurTaskRoutine:
        routine = json.loads(routine_as_json)
        obj = cls()

        for key in routine.keys():
            obj[key] = routine[key]['jobs']
            
            #add any deps
            for dep in routine[key]['dependencies']:
                obj.add_dependency_relationship(job=key,depends_on=dep)
        
        return obj
        
    @classmethod
    def from_dict(cls,routine_as_dict: dict) -> AugurTaskRoutine:
        obj = cls()

        for key in routine_as_dict.keys():
            obj[key] = routine_as_dict[key]['jobs']
            
            #add any deps
            for dep in routine_as_dict[key]['dependencies']:
                obj.add_dependency_relationship(job=key,depends_on=dep)
        
        return obj

    #Get and set dict values that correspond to celery task groups
    def __getitem__(self,key: str) -> dict:
        return self.jobs_dict[key]
    
    def __setitem__(self,key: str,newJobs):
        if not hasattr(newJobs, 'apply_async') or not callable(newJobs.apply_async):
            self.logger.error("Collection groups must be of celery types that can be called with \'apply_async\'")
            raise AttributeError 
        
        if key in self.disabled_collection_groups:
            self.logger.error("Group has been disabled")
            return
        self.jobs_dict[key] = newJobs
        self.dependency_relationships[key] = []

    #Make a group deleted from the dict and unable to be run or added.
    def disable_group(self,key: str):
        del self.jobs_dict[key]
        del self.dependency_relationships[key]
        self.disabled_collection_groups.append(key)

    #force these params to be kwargs so they are more readable
    def add_dependency_relationship(self,job=None,depends_on=None):
        assert (job in self.jobs_dict.keys() and depends_on in self.jobs_dict.keys()), "One or both collection groups don't exist!"
        assert (job != depends_on), "Something can not depend on itself!"

        self.dependency_relationships[job].append(depends_on)
    
    def _update_dependency_relationship_with_celery_id(self,celery_id: str,dependency_name: str):
        #Replace dependency with active celery id once started so that dependent tasks can check status
        for group_name in self.dependency_relationships.keys():
            #self.dependency_relationships[group_name] = [celery_id if item == name else item for item in self.dependency_relationships[group_name]]
            for index,item in enumerate(self.dependency_relationships[group_name]):
                if item == dependency_name:
                    self.dependency_relationships[group_name][index] = celery_id    
                    break #break once dependency_name found. Should only occur once.


    def start_data_collection(self):
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
def start_task(repo_git: str):

    owner, repo = get_owner_repo(repo_git)
    
    logger = logging.getLogger(start_task.__name__)

    logger.info(f"Collecting data for {owner}/{repo}")
    
 
    start_task_list = []
    start_task_list.append(collect_pull_requests.si(repo_git))
    start_task_list.append(collect_issues.si(repo_git))

    start_tasks_group = group(start_task_list)
    
    secondary_task_list = []
    secondary_task_list.append(collect_events.si(repo_git))
    secondary_task_list.append(collect_issue_and_pr_comments.si(repo_git))
    
    secondary_task_group = group(secondary_task_list)

    task_chain = chain(
        start_tasks_group, 
        secondary_task_group, 
    )

    task_chain.apply_async()


def get_owner_repo(git_url):
    """ Gets the owner and repository names of a repository from a git url

    :param git_url: String, the git url of a repository
    :return: Tuple, includes the owner and repository names in that order
    """
    split = git_url.split('/')

    owner = split[-2]
    repo = split[-1]

    if '.git' == repo[-4:]:
        repo = repo[:-4]

    return owner, repo