import logging
import traceback

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.tasks.gitlab.gitlab_paginator import GitlabPaginator
from augur.tasks.gitlab.gitlab_task_session import GitlabTaskManifest
from augur.application.db.data_parse import extract_needed_issue_data_from_gitlab_issue, extract_needed_gitlab_issue_label_data, extract_needed_gitlab_issue_assignee_data
from augur.tasks.github.util.util import get_owner_repo, add_key_value_pair_to_dicts
from augur.application.db.models import Issue, IssueLabel, IssueAssignee, Repo
from augur.application.db.util import execute_session_query


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_issues(repo_git : str) -> int:


    logger = logging.getLogger(collect_gitlab_issues.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        try:
        
            query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
            repo_obj = execute_session_query(query, 'one')
            repo_id = repo_obj.repo_id

            owner, repo = get_owner_repo(repo_git)
        
            issue_data = retrieve_all_gitlab_issue_data(repo_git, logger, manifest.key_auth)

            if issue_data:
                total_issues = len(issue_data)
                process_issues(issue_data, f"{owner}/{repo}: Gitlab Issue task", repo_id, logger, augur_db)

                return total_issues
            else:
                logger.info(f"{owner}/{repo} has no issues")
                return 0
        except Exception as e:
            logger.error(f"Could not collect gitlab issues for repo {repo_git}\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return -1



def retrieve_all_gitlab_issue_data(repo_git, logger, key_auth) -> None:

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting gitlab issues for {owner}/{repo}")

    url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/issues"
    issues = GitlabPaginator(url, key_auth, logger)

    all_data = []
    num_pages = issues.get_num_pages()
    for page_data, page in issues.iter_pages():

        if page_data is None:
            return all_data

        if len(page_data) == 0:
            logger.debug(
                f"{owner}/{repo}: Gitlab Issues Page {page} contains no data...returning")
            logger.info(f"{owner}/{repo}: Issues Page {page} of {num_pages}")
            return all_data

        logger.info(f"{owner}/{repo}: Gitlab Issues Page {page} of {num_pages}")

        all_data += page_data

    return all_data
    
def process_issues(issues, task_name, repo_id, logger, augur_db) -> None:
    
    # get repo_id or have it passed
    tool_source = "Gitlab Issue Task"
    tool_version = "2.0"
    data_source = "Gitlab API"

    issue_dicts = []
    issue_mapping_data = {}
    for issue in issues:

        issue_dicts.append(
            extract_needed_issue_data_from_gitlab_issue(issue, repo_id, tool_source, tool_version, data_source)
        )

        issue_labels = extract_needed_gitlab_issue_label_data(issue["labels"], repo_id,
                                                       tool_source, tool_version, data_source)
        
        issue_assignees = extract_needed_gitlab_issue_assignee_data(issue["assignees"], repo_id,
                                                             tool_source, tool_version, data_source)
        
        mapping_data_key = issue["id"]
        issue_mapping_data[mapping_data_key] = {
                                            "labels": issue_labels,
                                            "assignees": issue_assignees,
                                            }    


    if len(issue_dicts) == 0:
        print("No gitlab issues found while processing")  
        return
           
    logger.info(f"{task_name}: Inserting {len(issue_dicts)} gitlab issues")
    issue_natural_keys = ["repo_id", "gh_issue_id"]
    issue_string_columns = ["issue_title", "issue_body"]
    issue_return_columns = ["gh_issue_id", "issue_id"]

    issue_return_data = augur_db.insert_data(issue_dicts, Issue, issue_natural_keys, return_columns=issue_return_columns, string_fields=issue_string_columns)

    issue_label_dicts = []
    issue_assignee_dicts = []
    for data in issue_return_data:

        gh_issue_id = data["gh_issue_id"]
        issue_id = data["issue_id"]

        try:
            other_issue_data = issue_mapping_data[gh_issue_id]
        except KeyError as e:
            logger.info(f"{task_name}: Cold not find other gitlab issue data. This should never happen. Error: {e}")


        # add the issue id to the lables and assignees, then add them to a list of dicts that will be inserted soon
        dict_key = "issue_id"
        issue_label_dicts += add_key_value_pair_to_dicts(other_issue_data["labels"], dict_key, issue_id)
        issue_assignee_dicts += add_key_value_pair_to_dicts(other_issue_data["assignees"], dict_key, issue_id)


    logger.info(f"{task_name}: Inserting other gitlab issue data of lengths: Labels: {len(issue_label_dicts)} - Assignees: {len(issue_assignee_dicts)}")

    # inserting issue labels
    # we are using label_src_id and issue_id to determine if the label is already in the database.
    issue_label_natural_keys = ['label_src_id', 'issue_id']
    issue_label_string_fields = ["label_text", "label_description"]
    augur_db.insert_data(issue_label_dicts, IssueLabel,
                        issue_label_natural_keys, string_fields=issue_label_string_fields)

    # inserting issue assignees
    # we are using issue_assignee_src_id and issue_id to determine if the label is already in the database.
    issue_assignee_natural_keys = ['issue_assignee_src_id', 'issue_id']
    augur_db.insert_data(issue_assignee_dicts, IssueAssignee, issue_assignee_natural_keys)