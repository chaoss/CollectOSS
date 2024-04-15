import logging

from augur.tasks.github.util.github_task_session import GithubTaskManifest
from augur.tasks.github.releases.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.application.db.lib import get_repo_by_repo_git


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_releases(repo_git):

    logger = logging.getLogger(collect_releases.__name__)

    repo_obj = get_repo_by_repo_git(repo_git)
    repo_id = repo_obj.repo_id

    with GithubTaskManifest(logger) as manifest:

        releases_model(manifest.augur_db, manifest.key_auth, logger, repo_git, repo_id)