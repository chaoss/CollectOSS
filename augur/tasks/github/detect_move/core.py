from augur.tasks.github.util.github_task_session import *
from augur.application.db.models import *
from augur.tasks.github.util.github_paginator import GithubPaginator
from augur.tasks.github.util.github_paginator import hit_api
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.github.util.util import parse_json_response
import logging
from datetime import datetime
from enum import Enum
from augur.application.db.util import execute_session_query

class CollectionState(Enum):
    SUCCESS = "Success"
    PENDING = "Pending"
    ERROR = "Error"
    COLLECTING = "Collecting"


def update_repo_with_dict(current_dict,new_dict,logger,db):
    
    
    to_insert = current_dict
    del to_insert['_sa_instance_state']
    to_insert.update(new_dict)

    result = db.insert_data(to_insert, Repo, ['repo_id'])

    url = to_insert['repo_git']
    logger.info(f"Updated repo for {url}\n")



def extract_owner_and_repo_from_endpoint(key_auth, url, logger):
    response_from_gh = hit_api(key_auth, url, logger)

    page_data = parse_json_response(logger, response_from_gh)

    full_repo_name = page_data['full_name']

    splits = full_repo_name.split('/')

    return splits[0], splits[-1]

def ping_github_for_repo_move(augur_db, key_auth, repo, logger,collection_hook='core'):

    owner, name = get_owner_repo(repo.repo_git)
    url = f"https://api.github.com/repos/{owner}/{name}"
    current_repo_dict = repo.__dict__

    attempts = 0
    while attempts < 10:
        response_from_gh = hit_api(key_auth, url, logger)

        if response_from_gh and response_from_gh.status_code != 404:
            break

        attempts += 1

    #Mark as errored if not found
    if response_from_gh.status_code == 404:
        logger.error(f"Repo {repo.repo_git} responded 404 when pinged!")

        repo_update_dict = {
        'repo_git': repo.repo_git,
        'repo_path': None,
        'repo_name': None,
        'description': f"During our check for this repo on {datetime.today().strftime('%Y-%m-%d')}, a 404 error was returned. The repository does not appear to have moved. Instead, it appears to be deleted",
        'data_collection_date': datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        update_repo_with_dict(current_repo_dict, repo_update_dict, logger, augur_db)

        raise Exception(f"ERROR: Repo not found at requested host {repo.repo_git}")
    elif attempts >= 10:
        logger.warning(f"Could not check if repo moved because the api timed out 10 times. Url: {url}")
        return
    

    #skip if not moved
    #301 moved permanently 
    if response_from_gh.status_code != 301:
        logger.info(f"Repo found at url: {url}")
        return
    
    owner, name = extract_owner_and_repo_from_endpoint(key_auth, response_from_gh.headers['location'], logger)


    try:
        old_description = str(repo.description)
    except:
        old_description = ""

    #Create new repo object to update existing
    repo_update_dict = {
        'repo_git': f"https://github.com/{owner}/{name}",
        'repo_path': None,
        'repo_name': None,
        'description': f"(Originally hosted at {url}) {old_description}"
    }

    update_repo_with_dict(current_repo_dict, repo_update_dict, logger,augur_db)

    statusQuery = augur_db.session.query(CollectionStatus).filter(CollectionStatus.repo_id == repo.repo_id)

    collectionRecord = execute_session_query(statusQuery,'one')
    if collection_hook == 'core':
        collectionRecord.core_status = CollectionState.PENDING.value
        collectionRecord.core_task_id = None
    elif collection_hook == 'secondary':
        collectionRecord.secondary_status = CollectionState.PENDING.value
        collectionRecord.secondary_task_id = None

    augur_db.session.commit()

    raise Exception("ERROR: Repo has moved! Marked repo as pending and stopped collection")

    
