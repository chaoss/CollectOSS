from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.releases.core import *
from augur.tasks.init.celery_app import celery_app as celery, engine
from augur.application.db.util import execute_session_query

@celery.task
def collect_releases():

    logger = logging.getLogger(collect_releases.__name__)
    with GithubTaskSession(logger, engine) as session:
        query = session.query(Repo)
        repos = execute_session_query(query, 'all')

        for repo in repos:
            releases_model(session, repo.repo_git, repo.repo_id)