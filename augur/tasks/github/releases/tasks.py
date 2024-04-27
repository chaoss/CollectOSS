import logging

from augur.tasks.github.releases.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.application.db.lib import get_repo_by_repo_git
from augur.application.db import get_engine
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.application.db.session import DatabaseSession


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_releases(repo_git):

    logger = logging.getLogger(collect_releases.__name__)

    repo_obj = get_repo_by_repo_git(repo_git)
    repo_id = repo_obj.repo_id

    key_auth = GithubRandomKeyAuth(logger)

    with DatabaseSession(logger, get_engine()) as session:

        releases_model(session, key_auth, logger, repo_git, repo_id)