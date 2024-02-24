import logging
import traceback
from augur.application.db.session import DatabaseSession
from augur.application.db import get_engine
from augur.tasks.git.dependency_tasks.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurFacadeRepoCollectionTask, AugurCoreRepoCollectionTask, AugurSecondaryRepoCollectionTask
from augur.application.db.util import execute_session_query
from augur.tasks.git.util.facade_worker.facade_worker.utilitymethods import get_absolute_repo_path
from augur.application.config import AugurConfig


@celery.task(base=AugurFacadeRepoCollectionTask)
def process_dependency_metrics(repo_git):
    #raise NotImplementedError

    engine = get_engine()

    logger = logging.getLogger(process_dependency_metrics.__name__)

    with DatabaseSession(logger, engine) as session:
        logger.info(f"repo_git: {repo_git}")
        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        

        repo = execute_session_query(query,'one')

        config = AugurConfig(session.logger, session)
    
        absolute_repo_path = get_absolute_repo_path(config.get_section("Facade")['repo_directory'],repo.repo_id,repo.repo_path,repo.repo_name)

        session.logger.debug(f"This is the deps model repo: {repo_git}.")

        generate_deps_data(session,repo.repo_id,absolute_repo_path)


@celery.task(base=AugurSecondaryRepoCollectionTask)
def process_ossf_dependency_metrics(repo_git):

    engine = get_engine()
    
    logger = logging.getLogger(process_ossf_dependency_metrics.__name__)

    with DatabaseSession(logger, engine) as session:
        logger.info(f"repo_git: {repo_git}")

        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        
        repo = execute_session_query(query,'one')
        generate_scorecard(session, repo.repo_id, repo_git)