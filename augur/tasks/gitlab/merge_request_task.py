import logging

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.tasks.gitlab.gitlab_paginator import GitlabPaginator
from augur.tasks.gitlab.gitlab_task_session import GitlabTaskManifest
from augur.application.db.data_parse import extract_needed_pr_data_from_gitlab_merge_request, extract_needed_merge_request_assignee_data, extract_needed_mr_label_data
from augur.tasks.github.util.util import get_owner_repo, add_key_value_pair_to_dicts
from augur.application.db.models import PullRequest, PullRequestAssignee, PullRequestLabel, Repo


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

    url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests?with_labels_details=True"
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
    data_source = "Gitlab API"

    merge_requests = []
    mr_mapping_data = {}
    for mr in data:
        merge_requests.append(extract_needed_pr_data_from_gitlab_merge_request(mr, repo_id, tool_source, tool_version))

        assignees = extract_needed_merge_request_assignee_data(mr["assignees"], repo_id, tool_source, tool_version, data_source)

        labels = extract_needed_mr_label_data(mr["labels"], repo_id, tool_source, tool_version, data_source)

        mapping_data_key = mr["id"]
        mr_mapping_data[mapping_data_key] = {
                                            "assignees": assignees,
                                            "labels": labels
                                            }          

    logger.info(f"{task_name}: Inserting mrs of length: {len(merge_requests)}")
    pr_natural_keys = ["repo_id", "pr_src_id"]
    pr_string_fields = ["pr_src_title", "pr_body"]
    pr_return_columns = ["pull_request_id", "pr_src_id"]
    pr_return_data = augur_db.insert_data(merge_requests, PullRequest, pr_natural_keys, return_columns=pr_return_columns, string_fields=pr_string_fields)


    mr_assignee_dicts = []
    mr_label_dicts = []
    for data in pr_return_data:

        mr_src_id = data["pr_src_id"]
        pull_request_id = data["pull_request_id"]

        try:
            other_mr_data = mr_mapping_data[mr_src_id]
        except KeyError as e:
            logger.info(f"Cold not find other pr data. This should never happen. Error: {e}")

        dict_key = "pull_request_id"
        mr_assignee_dicts += add_key_value_pair_to_dicts(other_mr_data["assignees"], dict_key, pull_request_id)
        mr_label_dicts += add_key_value_pair_to_dicts(other_mr_data["labels"], dict_key, pull_request_id)

    logger.info(f"{task_name}: Inserting other pr data of lengths: Labels: {len(mr_label_dicts)} - Assignees: {len(mr_assignee_dicts)}")

    # TODO: Setup unique key on asignees with a value of ('cntrb_id', 'pull_request_id') and add 'cntrb_id' to assingee data
    mr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
    augur_db.insert_data(mr_assignee_dicts, PullRequestAssignee, mr_assignee_natural_keys)

    pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
    pr_label_string_fields = ["pr_src_description"]
    augur_db.insert_data(mr_label_dicts, PullRequestLabel, pr_label_natural_keys, string_fields=pr_label_string_fields)

