import logging

from collectoss.tasks.github.releases.core import *
from collectoss.tasks.init.celery_app import celery_app as celery
from collectoss.tasks.init.celery_app import CoreRepoCollectionTask
from collectoss.application.db.lib import get_repo_by_repo_git, get_session
from collectoss.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth


@celery.task(base=CoreRepoCollectionTask)
def collect_releases(repo_git):

    logger = logging.getLogger(collect_releases.__name__)

    repo_obj = get_repo_by_repo_git(repo_git)
    repo_id = repo_obj.repo_id

    key_auth = GithubRandomKeyAuth(logger)

    with get_session() as session:

        releases_model(session, key_auth, logger, repo_git, repo_id)