from celery import Celery

# initialize the celery app
BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
celery = Celery('tasks', broker=BROKER_URL,
             backend=BACKEND_URL, include=['tasks.facade_tasks', 'tasks.issue_tasks'])