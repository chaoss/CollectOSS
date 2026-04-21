import logging 
from collectoss.tasks.github.pull_requests.commits_model.core import *
from collectoss.tasks.init.celery_app import celery_app as celery
from collectoss.tasks.init.celery_app import SecondaryRepoCollectionTask
from collectoss.tasks.github.util.github_task_session import GithubTaskManifest
from collectoss.application.db.lib import get_repo_by_repo_git



@celery.task(base=SecondaryRepoCollectionTask)
def process_pull_request_commits(repo_git: str, full_collection: bool) -> None:

    logger = logging.getLogger(process_pull_request_commits.__name__)

    repo = get_repo_by_repo_git(repo_git)

    with GithubTaskManifest(logger) as manifest:

        pull_request_commits_model(repo.repo_id, logger, manifest.db_session, manifest.key_auth, full_collection)
