import logging
import traceback
from augur.tasks.git.dependency_tasks.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurFacadeRepoCollectionTask, AugurSecondaryRepoCollectionTask


@celery.task(base=AugurFacadeRepoCollectionTask)
def process_dependency_metrics(repo_git):

    logger = logging.getLogger(process_dependency_metrics.__name__)

    generate_deps_data(logger, repo_git)


@celery.task(base=AugurSecondaryRepoCollectionTask, bind=True)
def process_ossf_dependency_metrics(self, repo_git):

    engine = self.app.engine
    
    logger = logging.getLogger(process_ossf_dependency_metrics.__name__)

    generate_scorecard(logger, repo_git)