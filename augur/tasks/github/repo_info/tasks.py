import logging

from augur.tasks.github.util.github_task_session import GithubTaskManifest
from augur.tasks.github.repo_info.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.application.db.lib import get_repo_by_repo_git


#Task to get regular misc github info
@celery.task(base=AugurCoreRepoCollectionTask)
def collect_repo_info(repo_git: str):

    logger = logging.getLogger(collect_repo_info.__name__)

    repo = get_repo_by_repo_git(repo_git)

    with GithubTaskManifest(logger) as manifest:

        repo_info_model(manifest.key_auth, repo, logger)


#Task to get CII api data for linux badge info using github data.
@celery.task(base=AugurCoreRepoCollectionTask)
def collect_linux_badge_info(repo_git: str):

    logger = logging.getLogger(collect_linux_badge_info.__name__)

    repo = get_repo_by_repo_git(repo_git)

    with GithubTaskManifest(logger) as manifest:

        badges_model(logger, repo_git, repo.repo_id, manifest.augur_db)
