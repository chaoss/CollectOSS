from celery import Celery
from celery import current_app 
from celery.signals import after_setup_logger
from augur.application.logs import TaskLogConfig
import logging

# initialize the celery app
BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
celery_app = Celery('tasks', broker=BROKER_URL,
             backend=BACKEND_URL, include=['augur.tasks.git.facade_tasks', 'augur.tasks.github.issue_tasks', 'augur.tasks.start_tasks'])   

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

    