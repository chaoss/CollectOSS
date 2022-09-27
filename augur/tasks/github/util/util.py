"""Utility functions that are useful for several Github tasks"""
from typing import Any, List, Tuple
from httpx import Response
import logging
import json
import httpx


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
        logger.error(f"Error invalid return from GitHub. Response was: {response.text}. Error: {e}")
        return json.loads(json.dumps(response.text))

