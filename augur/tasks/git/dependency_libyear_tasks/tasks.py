import logging
import traceback
from augur.application.db.session import DatabaseSession
from augur.tasks.git.dependency_libyear_tasks.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurFacadeRepoCollectionTask
from augur.application.db.util import execute_session_query

@celery.task(base=AugurFacadeRepoCollectionTask)
def process_libyear_dependency_metrics(repo_git):
    #raise NotImplementedError

    from augur.application.db import get_engine
    engine = get_engine()

    logger = logging.getLogger(process_libyear_dependency_metrics.__name__)

    with DatabaseSession(logger, engine) as session:
        logger.info(f"repo_git: {repo_git}")
        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        

        repo = execute_session_query(query,'one')
        deps_libyear_model(session, repo.repo_id,repo_git,repo.repo_group_id)