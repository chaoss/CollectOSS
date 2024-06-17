import logging
from augur.tasks.git.dependency_libyear_tasks.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurFacadeRepoCollectionTask

@celery.task(base=AugurFacadeRepoCollectionTask, bind=True)
def process_libyear_dependency_metrics(self, repo_git):
    #raise NotImplementedError

    logger = logging.getLogger(process_libyear_dependency_metrics.__name__)

    deps_libyear_model(logger, repo_git)