import logging
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.pull_requests.files_model.core import *
from augur.tasks.init.celery_app import celery_app as celery

@celery.task
def process_pull_request_files(repo_git: str) -> None:
    logger = logging.getLogger(process_pull_request_files.__name__)

    with GithubTaskSession(logger) as session:
        repo = session.query(Repo).filter(Repo.repo_git == repo_git).one()
        pull_request_files_model(repo.repo_id, logger)