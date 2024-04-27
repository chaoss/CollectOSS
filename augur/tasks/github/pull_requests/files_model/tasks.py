import logging
from augur.tasks.github.pull_requests.files_model.core import *
from augur.application.db.session import DatabaseSession
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurSecondaryRepoCollectionTask
from augur.application.db.lib import get_repo_by_repo_git
from augur.application.db import get_engine
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth





@celery.task(base=AugurSecondaryRepoCollectionTask)
def process_pull_request_files(repo_git: str) -> None:

    engine = get_engine()

    logger = logging.getLogger(process_pull_request_files.__name__)

    repo = get_repo_by_repo_git(repo_git)

    key_auth = GithubRandomKeyAuth(logger)

    pull_request_files_model(repo, logger, key_auth)