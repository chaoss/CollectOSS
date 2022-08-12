from celery import Celery
from celery import current_app 
from celery.signals import after_setup_logger
from augur.application.logs import TaskLogConfig
import logging

from augur.tasks.init import redis_db_number, redis_conn_string

start_tasks = ['augur.tasks.start_tasks']

github_tasks = ['augur.tasks.github.contributors.tasks', 'augur.tasks.github.issues.tasks', 'augur.tasks.github.pull_requests.tasks', 'augur.tasks.github.events.tasks', 'augur.tasks.github.messages.tasks']

git_tasks = ['augur.tasks.git.facade_tasks']

tasks = start_tasks + github_tasks + git_tasks


# initialize the celery app
BROKER_URL = f'{redis_conn_string}{redis_db_number}'
BACKEND_URL = f'{redis_conn_string}{redis_db_number+1}'
celery_app = Celery('tasks', broker=BROKER_URL,
             backend=BACKEND_URL, include=tasks)   

#Setting to be able to see more detailed states of running tasks
celery_app.conf.task_track_started = True


def split_tasks_into_groups(tasks):
    grouped_tasks = {}

    for task in tasks: 
        task_divided = task.split(".")

        try:
            grouped_tasks[task_divided[-2]].append(task_divided[-1])
        except:
            grouped_tasks[task_divided[-2]] = [task_divided[-1]]
    
    return grouped_tasks



#Load logging config once at task definition
@after_setup_logger.connect
def setup_loggers(*args,**kwargs):
    #load config

    celery_tasks = list(current_app.tasks.keys())

    tasks = [task for task in celery_tasks if 'celery.' not in task]
    
    loggingConfig = TaskLogConfig(split_tasks_into_groups(tasks), logLevel=logging.DEBUG)

    