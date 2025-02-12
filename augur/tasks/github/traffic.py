import logging

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.data_parse import extract_needed_clone_history_data
from augur.tasks.util.worker_util import remove_duplicate_dicts
from augur.tasks.github.util.util import get_owner_repo
from augur.application.db.models import RepoClone
from augur.application.db.lib import get_repo_by_repo_git, bulk_insert_dicts
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth


@celery.task
def collect_github_repo_clones_data(repo_git: str) -> None:
    
    logger = logging.getLogger(collect_github_repo_clones_data.__name__)
    
    repo_obj = get_repo_by_repo_git(repo_git)
    repo_id = repo_obj.repo_id

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting Github repository clone data for {owner}/{repo}")

    key_auth = GithubRandomKeyAuth(logger)

    clones_data = retrieve_all_clones_data(repo_git, logger, key_auth)

    if clones_data:
        process_clones_data(clones_data, f"{owner}/{repo}: Traffic task", repo_id)
    else:
        logger.info(f"{owner}/{repo} has no clones")

def retrieve_all_clones_data(repo_git: str, logger, key_auth):
    # owner, repo = get_owner_repo(repo_git)

    # url = f"https://api.github.com/repos/{owner}/{repo}/traffic/clones"
    
    # clones = GithubPaginator(url, key_auth, logger)

    # num_pages = clones.get_num_pages()
    all_data = []
    # for page_data, page in clones.iter_pages():

    #     if page_data is None:
    #         return all_data
            
    #     elif len(page_data) == 0:
    #         logger.debug(f"{repo.capitalize()} Traffic Page {page} contains no data...returning")
    #         logger.info(f"Traffic Page {page} of {num_pages}")
    #         return all_data

    #     logger.info(f"{repo} Traffic Page {page} of {num_pages}")

    #     all_data += page_data

    return all_data


def process_clones_data(clones_data, task_name, repo_id, logger) -> None:
    clone_history_data = clones_data[0]['clones']

    clone_history_data_dicts = extract_needed_clone_history_data(clone_history_data, repo_id)

    clone_history_data = remove_duplicate_dicts(clone_history_data_dicts, 'clone_data_timestamp')
    logger.info(f"{task_name}: Inserting {len(clone_history_data_dicts)} clone history records")
    
    bulk_insert_dicts(logger, clone_history_data_dicts, RepoClone, ['repo_id'])
