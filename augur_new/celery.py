from celery import Celery

# initialize the celery app
BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
celery = Celery('tasks', broker=BROKER_URL,
             backend=BACKEND_URL, include=['augur_new.tasks.facade_tasks', 'augur_new.tasks.issue_tasks', 'augur_new.tasks.start_tasks'])