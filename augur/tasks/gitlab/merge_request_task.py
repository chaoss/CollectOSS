import logging

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.tasks.gitlab.gitlab_paginator import GitlabPaginator
from augur.tasks.gitlab.gitlab_task_session import GitlabTaskManifest
from augur.application.db.data_parse import extract_needed_pr_data_from_gitlab_merge_request
from augur.tasks.github.util.util import get_owner_repo
from augur.application.db.models import PullRequest, Repo




@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_merge_requests(repo_git: str) -> int:


    logger = logging.getLogger(collect_gitlab_merge_requests.__name__)

    with GitlabTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        repo_id = augur_db.session.query(Repo).filter(
        Repo.repo_git == repo_git).one().repo_id

        owner, repo = get_owner_repo(repo_git)
        mr_data = retrieve_all_mr_data(repo_git, logger, manifest.key_auth)

        if mr_data:
            process_merge_requests(mr_data, f"{owner}/{repo}: Mr task", repo_id, logger, augur_db)

            return len(mr_data)
        else:
            logger.info(f"{owner}/{repo} has no merge requests")
            return 0


def retrieve_all_mr_data(repo_git: str, logger, key_auth) -> None:

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests"
    mrs = GitlabPaginator(url, key_auth, logger)

    all_data = []
    num_pages = mrs.get_num_pages()
    for page_data, page in mrs.iter_pages():

        if page_data is None:
            return all_data

        if len(page_data) == 0:
            logger.debug(
                f"{owner}/{repo} Mrs Page {page} contains no data...returning")
            logger.info(f"{owner}/{repo} Prs Page {page} of {num_pages}")
            return all_data

        logger.info(f"{owner}/{repo} Mrs Page {page} of {num_pages}")

        all_data += page_data

    return all_data


def process_merge_requests(data, task_name, repo_id, logger, augur_db):

    tool_source = "Mr Task"
    tool_version = "2.0"
    merge_requests = extract_needed_mr_data(data, repo_id, tool_source, tool_version)

    logger.info(f"{task_name}: Inserting mrs of length: {len(merge_requests)}")
    pr_natural_keys = ["repo_id", "pr_src_id"]
    pr_string_fields = ["pr_src_title", "pr_body"]
    pr_return_data = augur_db.insert_data(merge_requests, PullRequest, pr_natural_keys, string_fields=pr_string_fields)


def extract_needed_mr_data(mrs, repo_id, tool_source, tool_version):
     
    data = []
    for mr in mrs:
        data.append(extract_needed_pr_data_from_gitlab_merge_request(mr, repo_id, tool_source, tool_version))

    return data

