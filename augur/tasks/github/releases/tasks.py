from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.releases.core import *
from augur.tasks.init.celery_app import celery_app as celery, engine

@celery.task
def collect_releases():

    logger = logging.getLogger(collect_releases.__name__)
    with GithubTaskSession(logger, engine) as session:
        repos = session.query(Repo).all()

        for repo in repos:
            releases_model(session, repo.repo_git, repo.repo_id)