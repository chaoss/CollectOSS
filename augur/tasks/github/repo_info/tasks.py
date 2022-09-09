from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.repo_info.core import *
from augur.tasks.init.celery_app import celery_app as celery, engine


@celery.task
def collect_repo_info(repo_git: str):

    logger = logging.getLogger(collect_repo_info.__name__)

    with GithubTaskSession(logger, engine) as session:
        repo = session.query(Repo).filter(Repo.repo_git == repo_git).one()
        try:
            repo_info_model(session, repo)
        except Exception as e:
            session.logger.error(f"Could not add repo info for repo {repo.repo_id}\n Error: {e}")