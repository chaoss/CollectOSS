import logging 
from augur.tasks.github.pull_requests.commits_model.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurSecondaryRepoCollectionTask
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.application.db.lib import get_repo_by_repo_git



@celery.task(base=AugurSecondaryRepoCollectionTask)
def process_pull_request_commits(repo_git: str) -> None:

    logger = logging.getLogger(process_pull_request_commits.__name__)

    repo = get_repo_by_repo_git(repo_git)

    key_auth = GithubRandomKeyAuth(logger)

    pull_request_commits_model(repo, logger, key_auth)
