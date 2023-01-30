from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.releases.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.util import execute_session_query
import traceback

@celery.task
def collect_releases(repo_git):

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(collect_releases.__name__)
    with GithubTaskSession(logger, engine) as session:

        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id

        try:
            releases_model(session, repo_git, repo_id)
        except Exception as e:
            logger.error(f"Could not collect releases for {repo_git}\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
