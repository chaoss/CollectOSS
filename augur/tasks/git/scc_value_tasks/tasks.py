import logging
import traceback
from augur.application.db.session import DatabaseSession
from augur.tasks.git.scc_value_tasks.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurFacadeRepoCollectionTask, AugurCoreRepoCollectionTask
from augur.application.db.util import execute_session_query

@celery.task(base=AugurFacadeRepoCollectionTask)
def process_scc_value_metrics(repo_git):

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(process_scc_value_metrics.__name__)

    with DatabaseSession(logger,engine) as session:
        logger.info(f"repo_git: {repo_git}")

        query = session.query(Repo).filter(Repo.repo_git == repo_git)

        repo = execute_session_query(query, 'one')

        value_model(session,repo.repo_id, repo_git)