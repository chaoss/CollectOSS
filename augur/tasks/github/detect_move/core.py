from augur.tasks.github.util.github_task_session import *
from augur.application.db.models import Repo, CollectionStatus
from augur.tasks.github.util.github_paginator import hit_api
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.github.util.util import parse_json_response
from datetime import datetime
from augur.tasks.util.collection_state import CollectionState
from augur.application.db.util import execute_session_query
from augur.application.db.lib import bulk_insert_dicts
from augur.application.db.models import HistoricalRepoURLs
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse


class RepoMovedException(Exception):
    def __init__(self, message, new_url=None):
        super().__init__(message)
        self.new_url = new_url


class RepoGoneException(Exception):
    pass


def update_repo_with_dict(repo, new_dict, logger):
    """
    Update a repository record in the database using a dictionary tagged with
    the appropriate table fields.

    Args:
        repo: orm repo object to update
        new_dict: dict of new values to add to the repo record
        logger: logging object
        db: db object
    """
    to_insert = dict(repo.__dict__)
    del to_insert['_sa_instance_state']

    old_url = to_insert["repo_git"]
    repo_id = to_insert["repo_id"]

    with DatabaseSession(logger) as session:
        previous_alias = HistoricalRepoURLs(repo_id=repo_id, git_url=old_url)
        try:
            session.add(previous_alias)
            session.commit()
        except IntegrityError:
            session.rollback()

    to_insert.update(new_dict)

    bulk_insert_dicts(logger, to_insert, Repo, ['repo_id'])

    url = to_insert['repo_git']
    logger.info(f"Updated repo {old_url} to {url} and set alias")
    return url


def extract_owner_and_repo_from_endpoint(key_auth, url, logger):
    response_from_gh = hit_api(key_auth, url, logger)
    page_data = parse_json_response(logger, response_from_gh)

    # Preferred path: full_name from API response
    full_repo_name = page_data.get('full_name')
    if full_repo_name:
        owner, repo = full_repo_name.split('/', 1)
        return owner, repo

    # Fallback: extract from redirect URL
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')

    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]

    logger.warning(
        "Unable to extract owner/repo from GitHub response or redirect URL",
        extra={"url": url, "keys": list(page_data.keys())}
    )
    return None, None


def ping_github_for_repo_move(session, key_auth, repo, logger, collection_hook='core'):
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

    # 301: Repo moved
    if response_from_gh.status_code == 301:
        redirect_location = (
            response_from_gh.headers.get('location')
            or response_from_gh.headers.get('Location')
        )

        if not redirect_location:
            logger.error(f"Could not get redirect location for repo: {url}")
            raise Exception(f"ERROR: Could not get redirect location for repo: {url}")

        owner, name = extract_owner_and_repo_from_endpoint(
            key_auth, redirect_location, logger
        )

        if not owner or not name:
            raise RepoMovedException(
                "Repo moved but new location could not be determined",
                new_url=redirect_location
            )

        try:
            old_description = str(repo.description)
        except Exception:
            old_description = ""

        repo_update_dict = {
            'repo_git': f"https://github.com/{owner}/{name}",
            'repo_path': None,
            'repo_name': None,
            'description': f"(Originally hosted at {url}) {old_description}"
        }

        new_url = update_repo_with_dict(repo, repo_update_dict, logger)

        raise RepoMovedException(
            "ERROR: Repo has moved! Resetting Collection!",
            new_url=new_url
        )

    # 404: Repo deleted
    if response_from_gh.status_code == 404:
        repo_update_dict = {
            'repo_git': repo.repo_git,
            'repo_path': None,
            'repo_name': None,
            'description': (
                f"During our check for this repo on {datetime.today().strftime('%Y-%m-%d')}, "
                "a 404 error was returned. The repository does not appear to have moved. "
                "Instead, it appears to be deleted"
            ),
            'data_collection_date': datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        update_repo_with_dict(repo, repo_update_dict, logger)

        status_query = session.query(CollectionStatus).filter(
            CollectionStatus.repo_id == repo.repo_id
        )
        collection_record = execute_session_query(status_query, 'one')

        now = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')

        collection_record.core_status = CollectionState.IGNORE.value
        collection_record.core_task_id = None
        collection_record.core_data_last_collected = now

        collection_record.secondary_status = CollectionState.IGNORE.value
        collection_record.secondary_task_id = None
        collection_record.secondary_data_last_collected = now

        collection_record.facade_status = CollectionState.IGNORE.value
        collection_record.facade_task_id = None
        collection_record.facade_data_last_collected = now

        collection_record.ml_status = CollectionState.IGNORE.value
        collection_record.ml_task_id = None
        collection_record.ml_data_last_collected = now

        session.commit()
        raise RepoGoneException(
            "ERROR: Repo has moved, and there is no redirection! "
            "404 returned, not 301. Resetting Collection!"
        )

    logger.info(f"Repo found at url: {url}")
    return
