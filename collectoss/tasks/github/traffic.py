import logging

from collectoss.tasks.init.celery_app import celery_app as celery
from collectoss.application.db.data_parse import extract_needed_clone_history_data
from collectoss.tasks.util.worker_util import remove_duplicate_dicts
from collectoss.tasks.github.util.util import get_owner_repo
from collectoss.application.db.models import RepoClone
from collectoss.application.db.lib import get_repo_by_repo_git, bulk_insert_dicts
from collectoss.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth


@celery.task
def collect_github_repo_clones_data(repo_git: str) -> None:
    
    logger = logging.getLogger(collect_github_repo_clones_data.__name__)
    
    repo_obj = get_repo_by_repo_git(repo_git)
    repo_id = repo_obj.repo_id

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting Github repository clone data for {owner}/{repo}")

    key_auth = GithubRandomKeyAuth(logger)

    clones_data = []

    if clones_data:
        process_clones_data(clones_data, f"{owner}/{repo}: Traffic task", repo_id)
    else:
        logger.info(f"{owner}/{repo} has no clones")


def process_clones_data(clones_data, task_name, repo_id, logger) -> None:
    clone_history_data = clones_data[0]['clones']

    clone_history_data_dicts = extract_needed_clone_history_data(clone_history_data, repo_id)

    clone_history_data = remove_duplicate_dicts(clone_history_data_dicts, 'clone_data_timestamp')
    logger.info(f"{task_name}: Inserting {len(clone_history_data_dicts)} clone history records")
    
    bulk_insert_dicts(logger, clone_history_data_dicts, RepoClone, ['repo_id'])
