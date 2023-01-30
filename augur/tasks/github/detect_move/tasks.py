from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.detect_move.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.util import execute_session_query



@celery.task()
def detect_github_repo_move(repo_git : str) -> None:

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(detect_github_repo_move.__name__)

    logger.info(f"Starting repo_move operation with {repo_git}")
    with GithubTaskSession(logger, engine) as session:
        #Ping each repo with the given repo_git to make sure
        #that they are still in place. 
        try:
            query = session.query(Repo).filter(Repo.repo_git == repo_git)
            repo = execute_session_query(query, 'one')
            logger.info(f"Pinging repo: {repo_git}")
            ping_github_for_repo_move(session, repo)
        except Exception as e:
            logger.error(f"Could not check repo source for {repo_git}\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")