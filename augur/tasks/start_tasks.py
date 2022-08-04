from augur.tasks.github.issue_tasks import *

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.util.task_session import TaskSession
from augur.application.logs import AugurLogger
from celery.result import AsyncResult
import time

pr_numbers = [70, 106, 170, 190, 192, 208, 213, 215, 216, 218, 223, 224, 226, 230, 237, 238, 240, 241, 248, 249, 250, 252, 253, 254, 255, 256, 257, 261, 268, 270, 273, 277, 281, 283, 288, 291, 303, 306, 309, 310, 311, 323, 324, 325, 334, 335, 338, 343, 346, 348, 350, 353, 355, 356, 357, 359, 360, 365, 369, 375, 381, 382, 388, 405, 408, 409, 410, 414, 418, 419, 420, 421, 422, 424, 425, 431, 433, 438, 445, 450, 454, 455, 456, 457, 460, 463, 468, 469, 470, 474, 475, 476, 477, 478, 479, 480, 481, 482, 484, 485, 486, 487, 488, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 504, 506, 507, 508, 509, 510, 512, 514]

#Use this task to listen for other tasks before deploying.
@celery.task
def deploy_dependent_task(*args,task_set):
    #prereqs = [AsyncResult(str(task_id)) for task_id in args]

    for task_id in args:
        prereq = AsyncResult(str(task_id))

        prereq.wait()
    
    #The convention now is to just add the string 'child' after the autogen'd
    #parent task id to be consistant.
    task_set.apply_async(task_id=(self.request.id + "child"))


#Class to control what tasks are run when the augur collection is started.
#Groups are run asynchronously 
class AugurTaskRoutine:

    def __init__(self,disabled_collection_groups=[]):
        self.logger = AugurLogger("data_collection_groups").get_logger()
        #self.session = TaskSession(self.logger)
        self.jobs_dict = {}
        self.started_jobs = []
        self.disabled_collection_groups = disabled_collection_groups

        self.dependency_relationships = {}

    #Get and set dict values that correspond to celery task groups
    def __getitem__(self,key):
        return self.jobs_dict[key]
    
    def __setitem__(self,key,newJobs):
        if not hasattr(newJobs, 'apply_async') or not callable(newJobs.apply_async):
            self.logger.error("Collection groups must be of celery types that can be called with \'apply_async\'")
            raise AttributeError 
        
        if key in self.disabled_collection_groups:
            self.logger.error("Group has been disabled")
            return
        self.jobs_dict[key] = newJobs
        self.dependency_relationships[key] = []

    #Make a group deleted from the dict and unable to be run or added.
    def disable_group(self,key):
        del self.jobs_dict[key]
        del self.dependency_relationships[key]
        self.disabled_collection_groups.append(key)

    def add_dependency_relationship(self,key,otherKey):
        assert (key in self.jobs_dict.keys() and otherKey in self.jobs_dict.keys()), "One or both collection groups don't exist!"

        self.dependency_relationships[key].append(otherKey)
    
    def _update_dependency_relationship_with_celery_id(self,celery_id,dependency_name,append=None):
        #Replace dependency with active celery id once started so that dependent tasks can check status
        #append is to add the id of the child task before it starts. (Don't worry the parent task starts it before it dies and the child is added on the end)
        #IMPORTANT for the append to actually be on the end of the list.
        for group_name in self.dependency_relationships.keys():
            #self.dependency_relationships[group_name] = [celery_id if item == name else item for item in self.dependency_relationships[group_name]]
            for index,item in enumerate(self.dependency_relationships[group_name]):
                if item == dependency_name:
                    self.dependency_relationships[group_name][index] = celery_id

                    if append:
                        self.dependency_relationships[group_name].append(append)
                    
                    break #break once dependency_name found. Should only occur once.


    def start_data_collection(self):
        #First, start all task groups that have no dependencies. 
        for name, collection_set in self.jobs_dict.items():
            self.logger.info(f"Starting non dependant collection group {name}...")

            if not self.dependency_relationships[name]:
                self.started_jobs.append(name)
                task_collection = collection_set.apply_async()
                
                self._update_dependency_relationship_with_celery_id(task_collection.id,name)
        
        dependency_cycle = True
        #Check if there are any elements in any of the dependency_relationships lists
        #that still haven't been replaced by celery task ids.
        while not all( any(check in dependencies for check in list(self.jobs_dict.keys())) for dependencies in self.dependency_relationships.values()):
            dependency_cycle = True
            for name in self.dependency_relationships.keys():
                #Check that task group has no dependencies that haven't been started yet and that it has not already been started.
                if not any(check in self.dependency_relationships[name] for check in list(self.jobs_dict.keys())) and not name in self.started_jobs:
                    self.started_jobs.append(name)
                    dependency_cycle = False
                    #task_collection = self.jobs_dict[name].apply_async()
                    dependent_task_collection = deploy_dependent_task.si(*self.dependency_relationships[name],task_set=self.jobs_dict[name])
                    result = dependent_task_collection.apply_async()

                    self._update_dependency_relationship_with_celery_id(task_collection.id,name,append=(task_collection.id + "child"))
                
            
            if dependency_cycle:
                raise Exception("Task group dependency cycle found as all pending tasks have prereqs that cannot be run.")

@celery.task
def start_task(repo_git: str):

    owner, repo = get_owner_repo(repo_git)
    
    logger = logging.getLogger(start_task.__name__)
    session = TaskSession(logger)

    logger.info(f"Collecting data for {owner}/{repo}")
 
    start_task_list = []
    start_task_list.append(collect_pull_requests.si(repo_git))
    start_task_list.append(collect_issues.si(repo_git))

    start_tasks_group = group(start_task_list)
    

    secondary_task_list = []
    # secondary_task_list.append(pull_request_reviews.s(owner, repo, pr_numbers))
    secondary_task_list.append(collect_events.si(repo_git))
    secondary_task_list.append(collect_issue_and_pr_comments.si(repo_git))
    
    secondary_task_group = group(secondary_task_list)

    third_task_list = []
    # third_task_list.append(process_contributors.s())
    
    third_task_group = group(third_task_list)


    job = chain(
        start_tasks_group,
        secondary_task_group,
        process_contributors.si()
    )

    job.apply_async()

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