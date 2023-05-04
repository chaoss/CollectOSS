"""Utility functions that are useful for several Github tasks"""
from typing import Any, List, Tuple
from httpx import Response
import logging
import json
import httpx
from augur.tasks.github.util.github_task_session import GithubTaskManifest
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Repo
from augur.tasks.util.worker_util import calculate_date_weight_from_timestamps


# This function adds a key value pair to a list of dicts and returns the modified list of dicts back
def add_key_value_pair_to_dicts(data: List[dict], key: str, value: Any) -> List[dict]:
    """Adds a key value pair to a list of dicts

    Args:
        data: list of dicts that is being modified
        key: key that is being added to dicts
        value: value that is being added to dicts

    Returns:
        list of dicts with the key value pair added
    """

    for item in data:

        item[key] = value

    return data

def get_owner_repo(git_url: str) -> Tuple[str, str]:
    """Gets the owner and repository names of a repository from a git url

    Args:
        git_url: the git url of a repository

    Returns:
        the owner and repository names in that order
    """
    split = git_url.split('/')

    owner = split[-2]
    repo = split[-1]

    if '.git' == repo[-4:]:
        repo = repo[:-4]

    return owner, repo


def parse_json_response(logger: logging.Logger, response: httpx.Response) -> dict:
    # try to get json from response
    try:
        return response.json()
    except json.decoder.JSONDecodeError as e:
        logger.warning(f"invalid return from GitHub. Response was: {response.text}. Exception: {e}")
        return json.loads(json.dumps(response.text))

def get_repo_weight_by_issue(logger,repo_git):
    from augur.tasks.github.util.gh_graphql_entities import GitHubRepo as GitHubRepoGraphql

    owner,name = get_owner_repo(repo_git)

    with GithubTaskManifest(logger) as manifest:
        repo_graphql = GitHubRepoGraphql(logger, manifest.key_auth, owner, name)
        number_of_issues_and_prs = len(repo_graphql.get_issues_collection()) + len(repo_graphql.get_pull_requests_collection())
    
    return number_of_issues_and_prs

#Get the weight for each repo for the core collection hook
def get_repo_weight_core(logger,repo_git):
    from augur.tasks.init.celery_app import engine

    with DatabaseSession(logger,engine) as session:
        repo = Repo.get_by_repo_git(session, repo_git)
        if not repo:
            raise Exception(f"Task with repo_git of {repo_git} but could not be found in Repo table")
        
        #try to get the collection status if it exists at this point
        try:
            status = repo.collection_status[0]
            time_factor = calculate_date_weight_from_timestamps(repo.repo_added,status.core_data_last_collected)
        except IndexError:
            time_factor = calculate_date_weight_from_timestamps(repo.repo_added,None)


    #Don't go below zero.
    return max(0,get_repo_weight_by_issue(logger, repo_git) - time_factor)

