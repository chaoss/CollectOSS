import logging

from augur.application.db.session import DatabaseSession
from augur.tasks.github.repo_info.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.application.db.lib import get_repo_by_repo_git
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.application.db import get_engine


#Task to get regular misc github info
@celery.task(base=AugurCoreRepoCollectionTask)
def collect_repo_info(repo_git: str):

    logger = logging.getLogger(collect_repo_info.__name__)

    repo = get_repo_by_repo_git(repo_git)

    key_auth = GithubRandomKeyAuth(logger)

    repo_info_model(key_auth, repo, logger)


#Task to get CII api data for linux badge info using github data.
@celery.task(base=AugurCoreRepoCollectionTask)
def collect_linux_badge_info(repo_git: str):

    engine = get_engine()

    logger = logging.getLogger(collect_linux_badge_info.__name__)

    repo = get_repo_by_repo_git(repo_git)

    with DatabaseSession(logger, engine=engine) as session:

        badges_model(logger, repo_git, repo.repo_id, session)
