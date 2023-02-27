from augur.tasks.github.util.github_task_session import GithubTaskManifest
from augur.tasks.github.releases.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.util import execute_session_query
import traceback

@celery.task
def collect_releases(repo_git):

    logger = logging.getLogger(collect_releases.__name__)
    with GithubTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id

        try:
            releases_model(augur_db, manifest.key_auth, logger, repo_git, repo_id)
        except Exception as e:
            logger.error(f"Could not collect releases for {repo_git}\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
