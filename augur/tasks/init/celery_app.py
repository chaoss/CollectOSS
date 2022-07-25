from celery import Celery
# initialize the celery app
BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
celery_app = Celery('tasks', broker=BROKER_URL,
             backend=BACKEND_URL, include=['augur.tasks.git.facade_tasks', 'augur.tasks.github.issue_tasks', 'augur.tasks.start_tasks'])   