import logging
import traceback
from augur.application.db.lib import get_session
from augur.tasks.git.dependency_tasks.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurFacadeRepoCollectionTask, AugurSecondaryRepoCollectionTask
from augur.application.db.util import execute_session_query
from augur.tasks.git.util.facade_worker.facade_worker.utilitymethods import get_absolute_repo_path
from augur.application.db.lib import get_value


@celery.task(base=AugurFacadeRepoCollectionTask)
def process_dependency_metrics(repo_git):

    logger = logging.getLogger(process_dependency_metrics.__name__)

    generate_deps_data(logger, repo_git)


@celery.task(base=AugurSecondaryRepoCollectionTask, bind=True)
def process_ossf_dependency_metrics(self, repo_git):

    engine = self.app.engine
    
    logger = logging.getLogger(process_ossf_dependency_metrics.__name__)

    generate_scorecard(logger, repo_git)