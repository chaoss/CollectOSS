import time
import logging

from augur.tasks.init.celery_app import celery_app as celery, engine
from augur.application.db.data_parse import extract_needed_clone_history_data
from augur.tasks.github.util.github_paginator import GithubPaginator
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.util.worker_util import remove_duplicate_dicts
from augur.tasks.github.util.util import get_owner_repo
from augur.application.db.models import RepoClone, Repo
from augur.application.db.util import execute_session_query

@celery.task
def collect_github_repo_clones_data(repo_git: str) -> None:
    
    logger = logging.getLogger(collect_github_repo_clones_data.__name__)

    # using GithubTaskSession to get our repo_obj for which we will store data of clones
    with GithubTaskSession(logger) as session:

        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id

        owner, repo = get_owner_repo(repo_git)

        logger.info(f"Collecting Github repository clone data for {owner}/{repo}")
    
    clones_data = retrieve_all_clones_data(repo_git, logger)

    if clones_data:
        process_clones_data(clones_data, f"{owner}/{repo}: Traffic task", repo_id, logger)
    else:
        logger.info(f"{owner}/{repo} has no clones")


def retrieve_all_clones_data(repo_git: str, logger):
    owner, repo = get_owner_repo(repo_git)

    url = f"https://api.github.com/repos/{owner}/{repo}/traffic/clones"
    
    # define GithubTaskSession to handle insertions, and store oauth keys 
    with GithubTaskSession(logger, engine) as session:
    
        clones = GithubPaginator(url, session.oauths, logger)

    num_pages = clones.get_num_pages()
    all_data = []
    for page_data, page in clones.iter_pages():

        if page_data is None:
            return all_data
            
        elif len(page_data) == 0:
            logger.debug(f"{repo.capitalize()} Traffic Page {page} contains no data...returning")
            logger.info(f"Traffic Page {page} of {num_pages}")
            return all_data

        logger.info(f"{repo} Traffic Page {page} of {num_pages}")

        all_data += page_data

    return all_data


def process_clones_data(clones_data, task_name, repo_id, logger) -> None:
    clone_history_data = clones_data[0]['clones']

    clone_history_data_dicts = extract_needed_clone_history_data(clone_history_data, repo_id)

    with GithubTaskSession(logger, engine) as session:
        
        clone_history_data = remove_duplicate_dicts(clone_history_data_dicts, 'clone_data_timestamp')
        logger.info(f"{task_name}: Inserting {len(clone_history_data_dicts)} clone history records")
        
        session.insert_data(clone_history_data_dicts, RepoClone, ['repo_id'])
