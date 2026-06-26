import logging

from collectoss.application.db.session import DatabaseSession
from collectoss.tasks.github.repo_info.core import *
from collectoss.tasks.init.celery_app import celery_app as celery
from collectoss.tasks.init.celery_app import CoreRepoCollectionTask
from collectoss.application.db.lib import get_repo_by_repo_git
from collectoss.application.db import get_engine


#Task to get regular misc github info
@celery.task(base=CoreRepoCollectionTask)
def collect_repo_info(repo_git: str):

    logger = logging.getLogger(collect_repo_info.__name__)

    repo = get_repo_by_repo_git(repo_git)

    repo_info_model(None, repo, logger)


#Task to get CII api data for linux badge info using github data.
@celery.task(base=CoreRepoCollectionTask)
def collect_linux_badge_info(repo_git: str):

    engine = get_engine()

    logger = logging.getLogger(collect_linux_badge_info.__name__)

    repo = get_repo_by_repo_git(repo_git)

    with DatabaseSession(logger, engine=engine) as session:

        badges_model(logger, repo_git, repo.repo_id, session)
