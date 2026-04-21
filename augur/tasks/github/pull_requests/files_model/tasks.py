import logging
from augur.tasks.github.pull_requests.files_model.core import *
from augur.tasks.github.util.github_task_session import GithubTaskManifest
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import SecondaryRepoCollectionTask
from augur.application.db.util import execute_session_query

@celery.task(base=SecondaryRepoCollectionTask)
def process_pull_request_files(repo_git: str, full_collection: bool) -> None:

    logger = logging.getLogger(process_pull_request_files.__name__)

    with GithubTaskManifest(logger) as manifest:
        db_session = manifest.db_session
        query = db_session.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo = execute_session_query(query, 'one')

        pull_request_files_model(repo.repo_id, logger, db_session, manifest.key_auth, full_collection)