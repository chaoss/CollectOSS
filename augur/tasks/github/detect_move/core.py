from augur.tasks.github.util.github_task_session import *
from augur.application.db.models import *
from augur.tasks.github.util.github_paginator import GithubPaginator
from augur.tasks.github.util.github_paginator import hit_api
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.github.util.util import parse_json_response
import logging

def extract_owner_and_repo_from_endpoint(session,url):
    response_from_gh = hit_api(session.oauths, url, session.logger)

    page_data = parse_json_response(session.logger, response_from_gh)

    full_repo_name = page_data['full_name']

    splits = full_repo_name.split('/')

    return splits[0], splits[-1]

def ping_github_for_repo_move(session,repo):

    owner, name = get_owner_repo(repo.repo_git)
    url = f"https://api.github.com/repos/{owner}/{name}"

    response_from_gh = hit_api(session.oauths, url, session.logger)

    #skip if not moved
    #301 moved permanently 
    if response_from_gh.status_code != 301:
        session.logger.info(f"Repo found at url: {url}")
        return
    
    owner, name = extract_owner_and_repo_from_endpoint(session, response_from_gh.headers['location'])

    current_repo_dict = repo.__dict__
    del current_repo_dict['_sa_instance_state']


    try:
        old_description = str(repo.description)
    except:
        old_description = ""

    #Create new repo object to update existing
    repo_update_dict = {
        'repo_git': f"https://github.com/{owner}/{name}",
        'repo_path': None,
        'repo_name': None,
        'repo_status': 'New',
        'description': f"(Originally hosted at {url}) {old_description}"
    }

    current_repo_dict.update(repo_update_dict)

    result = session.insert_data(current_repo_dict, Repo, ['repo_id'])

    session.logger.info(f"Updated repo for {owner}/{name}\n")
