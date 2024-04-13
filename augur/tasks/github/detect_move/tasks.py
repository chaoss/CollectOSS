import logging

from augur.tasks.github.util.github_task_session import GithubTaskManifest
from augur.tasks.github.detect_move.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask, AugurSecondaryRepoCollectionTask
from augur.application.db.lib import get_repo_by_repo_git



@celery.task(base=AugurCoreRepoCollectionTask)
def detect_github_repo_move_core(repo_git : str) -> None:

    logger = logging.getLogger(detect_github_repo_move_core.__name__)

    logger.info(f"Starting repo_move operation with {repo_git}")

    repo = get_repo_by_repo_git(repo_git)

    logger.info(f"Pinging repo: {repo_git}")

    with GithubTaskManifest(logger) as manifest:
        #Ping each repo with the given repo_git to make sure
        #that they are still in place. 
        ping_github_for_repo_move(manifest.augur_db, manifest.key_auth, repo, logger)


@celery.task(base=AugurSecondaryRepoCollectionTask)
def detect_github_repo_move_secondary(repo_git : str) -> None:

    logger = logging.getLogger(detect_github_repo_move_secondary.__name__)

    logger.info(f"Starting repo_move operation with {repo_git}")

    repo = get_repo_by_repo_git(repo_git)

    logger.info(f"Pinging repo: {repo_git}")

    with GithubTaskManifest(logger) as manifest:
        #Ping each repo with the given repo_git to make sure
        #that they are still in place. 
        ping_github_for_repo_move(manifest.augur_db, manifest.key_auth, repo, logger,collection_hook='secondary')