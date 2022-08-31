from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.detect_move.core import *
from augur.tasks.init.celery_app import celery_app as celery


@celery.task
def detect_github_repo_move():
    logger = logging.getLogger(detect_github_repo_move.__name__)

    with GithubTaskSession(logger) as session:
        repos = session.query(Repo).all()

        for repo in repos:
            ping_github_for_repo_move(session, repo)