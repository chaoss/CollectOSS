from augur.tasks.init.celery_app import celery_app as celery

@celery.task()
def successful_task():
    pass

@celery.task()
def failure_task():
    raise Exception("ERROR")


