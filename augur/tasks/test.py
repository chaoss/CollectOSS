from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.data_analysis.contributor_breadth_worker import 
@celery.task()
def successful_task():
    pass

@celery.task()
def failure_task():
    raise Exception("ERROR")


