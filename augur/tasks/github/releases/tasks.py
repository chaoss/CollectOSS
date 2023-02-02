from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.releases.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.util import execute_session_query
import traceback

@celery.task
def collect_releases():

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(collect_releases.__name__)
    with GithubTaskSession(logger, engine) as session:
        query = session.query(Repo)
        repos = execute_session_query(query, 'all')

        for repo in repos:
            try:
                releases_model(session, repo.repo_git, repo.repo_id)
            except Exception as e:
                logger.error(f"Could not collect releases for {repo.repo_git}\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
