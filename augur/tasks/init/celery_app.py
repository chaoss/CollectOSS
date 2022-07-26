from celery import Celery
from celery import current_app 
from celery.signals import after_setup_logger
from augur.application.logs import TaskLogConfig

# initialize the celery app
BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
celery_app = Celery('tasks', broker=BROKER_URL,
             backend=BACKEND_URL, include=['augur.tasks.git.facade_tasks', 'augur.tasks.github.issue_tasks', 'augur.tasks.start_tasks'])   


#Load logging config once at task definition
@after_setup_logger.connect
def setup_loggers(*args,**kwargs):
    #load config

    celery_tasks = list(current_app.tasks.keys())

    tasks = [task for task in celery_tasks if 'celery.' not in task]

    print(tasks)
    
    loggingConfig = TaskLogConfig(tasks)

    