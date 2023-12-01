import logging

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.tasks.gitlab.gitlab_paginator import GitlabPaginator
from augur.tasks.gitlab.gitlab_task_session import GitlabTaskManifest
from augur.application.db.data_parse import extract_needed_issue_data_from_gitlab_issue
from augur.tasks.github.util.util import get_owner_repo



@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_issues(repo_git: str) -> int:

    logger = logging.getLogger(collect_gitlab_issues.__name__)

    owner, repo = get_owner_repo(repo_git)
    url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/issues"

    with GitlabTaskManifest(logger) as manifest:

        issues = GitlabPaginator(url, manifest.key_auth, logger)
        for page_data, page_number in issues.iter_pages():

            if page_data == None:
                logger.info("Page was null")
                logger.info(f"Page number: {page_number}")
                break

            #logger.info(f"Page {page_number} data len: {len(page_data)}")
            data = extract_needed_issue_data_from_gitlab_issue(page_data[0], 1, "tool source", "tool version", "Gitlab API")
            #logger.info(f"Issue data: {data}")
            break