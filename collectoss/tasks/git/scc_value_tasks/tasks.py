import logging
from collectoss.application.db.lib import get_session
from collectoss.tasks.git.scc_value_tasks.core import *
from collectoss.tasks.init.celery_app import celery_app as celery
from collectoss.tasks.init.celery_app import FacadeRepoCollectionTask


@celery.task(base=FacadeRepoCollectionTask)
def process_scc_value_metrics(repo_git):

    logger = logging.getLogger(process_scc_value_metrics.__name__)

    value_model(logger,repo_git,)