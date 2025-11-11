from augur.tasks.github.util.github_task_session import *
from augur.application.db.models import Repo, CollectionStatus
from augur.tasks.github.util.github_paginator import hit_api
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.github.util.util import parse_json_response
from datetime import datetime
from augur.tasks.util.collection_state import CollectionState
from augur.application.db.util import execute_session_query
from augur.application.db.lib import bulk_insert_dicts



def update_repo_with_dict(repo,new_dict,logger):
    """
        Update a repository record in the database using a dictionary tagged with
        the appropriate table fields

        Args:
            repo: orm repo object to update
            new_dict: dict of new values to add to the repo record
            logger: logging object
            db: db object
    """
    to_insert = {}
    to_insert['repo_id'] = repo.repo_id # this is here because its needed as a unique key for bulk_insert_dicts
    to_insert['repo_git'] = repo.repo_git
    to_insert['repo_path'] = repo.repo_path
    to_insert['repo_name'] = repo.repo_name
    to_insert['description'] = repo.description
    to_insert.update(new_dict)

    result = bulk_insert_dicts(logger, to_insert, Repo, ['repo_id'])

    url = to_insert['repo_git']
    logger.info(f"Updated repo for {url}\n")



def extract_owner_and_repo_from_endpoint(key_auth, url, logger):
    response_from_gh = hit_api(key_auth, url, logger)

    page_data = parse_json_response(logger, response_from_gh)

    full_repo_name = page_data['full_name']

    splits = full_repo_name.split('/')

    return splits[0], splits[-1]

def ping_github_for_repo_move(session, key_auth, repo, logger,collection_hook='core'):

    owner, name = get_owner_repo(repo.repo_git)
    url = f"https://api.github.com/repos/{owner}/{name}"

    attempts = 0
    while attempts < 10:
        response_from_gh = hit_api(key_auth, url, logger, follow_redirects=False)

        if response_from_gh:
            break

        attempts += 1

    if attempts >= 10:
        logger.error(f"Could not check if repo moved because the api timed out 10 times. Url: {url}")
        raise Exception(f"ERROR: Could not get api response for repo: {url}")

    #Update Url and retry if 301
    #301 moved permanently 
    if response_from_gh.status_code == 301:
        redirect_location = response_from_gh.headers.get('location') or response_from_gh.headers.get('Location')
        if not redirect_location:
            logger.error(f"Could not check if repo moved because the redirect location is not present. Url: {url}")
            raise Exception(f"ERROR: Could not get redirect location for repo: {url}")

        owner, name = extract_owner_and_repo_from_endpoint(key_auth, redirect_location, logger)

        try:
            old_description = str(repo.description)
        except Exception:
            old_description = ""

        #Create new repo object to update existing
        repo_update_dict = {
            'repo_git': f"https://github.com/{owner}/{name}",
            'repo_path': None,
            'repo_name': None,
            'description': f"(Originally hosted at {url}) {old_description}"
        }

        update_repo_with_dict(repo, repo_update_dict, logger)

        raise Exception("ERROR: Repo has moved! Resetting Collection!")
    
    #Mark as ignore if 404
    if response_from_gh.status_code == 404:
        repo_update_dict = {
            'repo_git': repo.repo_git,
            'repo_path': None,
            'repo_name': None,
            'description': f"During our check for this repo on {datetime.today().strftime('%Y-%m-%d')}, a 404 error was returned. The repository does not appear to have moved. Instead, it appears to be deleted",
            'data_collection_date': datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

        update_repo_with_dict(repo, repo_update_dict, logger)

        statusQuery = session.query(CollectionStatus).filter(CollectionStatus.repo_id == repo.repo_id)

        collectionRecord = execute_session_query(statusQuery,'one')

        collectionRecord.core_status = CollectionState.IGNORE.value
        collectionRecord.core_task_id = None
        collectionRecord.core_data_last_collected = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')

        collectionRecord.secondary_status = CollectionState.IGNORE.value
        collectionRecord.secondary_task_id = None
        collectionRecord.secondary_data_last_collected = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')

        collectionRecord.facade_status = CollectionState.IGNORE.value
        collectionRecord.facade_task_id = None
        collectionRecord.facade_data_last_collected = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')

        collectionRecord.ml_status = CollectionState.IGNORE.value
        collectionRecord.ml_task_id = None
        collectionRecord.ml_data_last_collected = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')


        session.commit()
        raise Exception("ERROR: Repo has moved, and there is no redirection! 404 returned, not 301. Resetting Collection!")

    
    #skip if not 404
    logger.info(f"Repo found at url: {url}")
    return

