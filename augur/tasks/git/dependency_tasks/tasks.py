import logging
import traceback
from augur.application.db.session import DatabaseSession
from augur.tasks.git.dependency_tasks.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.util import execute_session_query


@celery.task
def process_dependency_metrics(repo_git_identifiers):
    #raise NotImplementedError

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(process_dependency_metrics.__name__)

    session = DatabaseSession(logger, engine)

    for repo_git in repo_git_identifiers:
        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo = execute_session_query(query,'one')

        try:
            deps_model(session, repo.repo_id)
        except Exception as e:
            session.logger.error(f"Could not complete deps_model!\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")