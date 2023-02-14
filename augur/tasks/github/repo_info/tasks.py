from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.application.db.session import DatabaseSession
from augur.tasks.github.repo_info.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.util import execute_session_query
import traceback

@celery.task()
def collect_repo_info(repo_git: str):

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(collect_repo_info.__name__)

    with GithubTaskSession(logger, engine) as session:
        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo = execute_session_query(query, 'one')
        try:
            repo_info_model(session, repo, logger)
        except Exception as e:
            session.logger.error(f"Could not add repo info for repo {repo.repo_id}\n Error: {e}")
            session.logger.error(
                    ''.join(traceback.format_exception(None, e, e.__traceback__)))
    
