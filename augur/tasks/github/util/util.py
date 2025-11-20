"""Utility functions that are useful for several Github tasks"""
from typing import Any, List, Tuple
import logging
import urllib.parse
import json
import httpx
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.tasks.github.util.github_graphql_data_access import GithubGraphQlDataAccess
from augur.application.db.lib import get_repo_by_repo_git
from augur.tasks.util.worker_util import calculate_date_weight_from_timestamps

def get_repo_src_id(owner, repo, logger):
    

    query = """query($repo: String!, $owner: String!) {
                    repository(name: $repo, owner: $owner) {
                        databaseId
                    }
                }
                """
    
    key_auth = GithubRandomKeyAuth(logger)
    
    github_graphql_data_access = GithubGraphQlDataAccess(key_auth, logger)

    variables = {
        "owner": owner,
        "repo": repo
    }

    result_keys = ["repository", "databaseId"]

    repo_src_id = github_graphql_data_access.get_resource(query, variables, result_keys)

    return repo_src_id



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

def get_gitlab_repo_identifier(owner, repo):

    return urllib.parse.quote(f"{owner}/{repo}", safe='')


def parse_json_response(logger: logging.Logger, response: httpx.Response) -> dict:
    # try to get json from response
    try:
        return response.json()
    except json.decoder.JSONDecodeError as e:
        logger.warning(f"invalid return. Response was: {response.text}. Exception: {e}")
        return json.loads(json.dumps(response.text))

def get_repo_weight_by_issue(logger,repo_git):
    """
    Retrieve the sum of the number of issues and prs in a repository from a graphql query.

    Arguments:
        logger: logger object
        repo_git: repository url
    
    Returns:
        Sum of issues and prs for that repo
    """

    from augur.tasks.github.util.gh_graphql_entities import GitHubRepo as GitHubRepoGraphql

    owner,name = get_owner_repo(repo_git)

    key_auth = GithubRandomKeyAuth(logger)

    repo_graphql = GitHubRepoGraphql(logger, key_auth, owner, name)
    number_of_issues_and_prs = len(repo_graphql.get_issues_collection()) + len(repo_graphql.get_pull_requests_collection())
    
    return number_of_issues_and_prs

#Get the weight for each repo for the core collection hook
def get_repo_weight_core(logger, repo_git):
    # Defensive: ensure repo exists
    repo = get_repo_by_repo_git(repo_git)
    if not repo:
        logger.error(f"get_repo_weight_core: Repo with repo_git '{repo_git}' not found")
        return 0

    # try to get the collection status if it exists at this point
    try:
        status = repo.collection_status[0]
        time_factor = calculate_date_weight_from_timestamps(repo.repo_added, status.core_data_last_collected)
    except Exception:
        # If no collection status or other error, fall back to using repo.repo_added
        time_factor = calculate_date_weight_from_timestamps(repo.repo_added, None)

    # get the raw issue/pr count defensively
    try:
        raw = get_repo_weight_by_issue(logger, repo_git)
        raw_count = int(raw) if (raw is not None) else 0
    except Exception as e:
        logger.error("get_repo_weight_core: error getting repo weight by issue for %s: %s", repo_git, e)
        raw_count = 0

    time_factor_val = int(time_factor) if (time_factor is not None) else 0

    # Don't go below zero.
    return max(0, raw_count - time_factor_val)

