import time
import logging
import traceback
import re

from sqlalchemy.exc import IntegrityError


from augur.tasks.init.celery_app import celery_app as celery, engine
from augur.application.db.data_parse import *
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.util.util import add_key_value_pair_to_dicts, get_owner_repo
from augur.tasks.util.worker_util import remove_duplicate_dicts
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, Issue, IssueEvent, IssueLabel, IssueAssignee, PullRequestMessageRef, IssueMessageRef, Contributor, Repo
from augur.application.config import get_development_flag
from augur.application.db.util import execute_session_query
development = get_development_flag()

@celery.task
def collect_issues(repo_git: str) -> None:

    logger = logging.getLogger(collect_issues.__name__)
    owner, repo = get_owner_repo(repo_git)

    # define GithubTaskSession to handle insertions, and store oauth keys 
    with GithubTaskSession(logger) as session:
        
        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id
        

    issue_data = retrieve_all_issue_data(repo_git, logger)

    if issue_data:

        process_issues(issue_data, f"{owner}/{repo}: Issue task", repo_id, logger)

    else:
        logger.info(f"{owner}/{repo} has no issues")


def retrieve_all_issue_data(repo_git, logger) -> None:

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting issues for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"

    # define GithubTaskSession to handle insertions, and store oauth keys 
    
    with GithubTaskSession(logger, engine) as session:

        # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
        # Reference the code documenation for GithubPaginator for more details
        issues = GithubPaginator(url, session.oauths, logger)

    # this is defined so we can decrement it each time 
    # we come across a pr, so at the end we can log how 
    # many issues were collected
    # loop through the issues 
    all_data = []
    num_pages = issues.get_num_pages()
    for page_data, page in issues.iter_pages():

        if page_data is None:
            return all_data

        if len(page_data) == 0:
            logger.debug(
                f"{owner}/{repo}: Issues Page {page} contains no data...returning")
            logger.info(f"{owner}/{repo}: Issues Page {page} of {num_pages}")
            return all_data

        logger.info(f"{owner}/{repo}: Issues Page {page} of {num_pages}")

        all_data += page_data

    return all_data
    
def process_issues(issues, task_name, repo_id, logger) -> None:
    
    # get repo_id or have it passed
    tool_source = "Issue Task"
    tool_version = "2.0"
    data_source = "Github API"

    issue_dicts = []
    issue_mapping_data = {}
    issue_total = len(issues)
    contributors = []
    for index, issue in enumerate(issues):

        # calls is_valid_pr_block to see if the data is a pr.
        # if it is a pr we skip it because we don't need prs 
        # in the issues table
        if is_valid_pr_block(issue) is True:
            issue_total-=1
            continue

        issue, contributor_data = process_issue_contributors(issue, tool_source, tool_version, data_source)

        contributors += contributor_data

        # create list of issue_dicts to bulk insert later
        issue_dicts.append(
            # get only the needed data for the issues table
            extract_needed_issue_data(issue, repo_id, tool_source, tool_version, data_source)
        )

         # get only the needed data for the issue_labels table
        issue_labels = extract_needed_issue_label_data(issue["labels"], repo_id,
                                                       tool_source, tool_version, data_source)

        # get only the needed data for the issue_assignees table
        issue_assignees = extract_needed_issue_assignee_data(issue["assignees"], repo_id,
                                                             tool_source, tool_version, data_source)


        mapping_data_key = issue["url"]
        issue_mapping_data[mapping_data_key] = {
                                            "labels": issue_labels,
                                            "assignees": issue_assignees,
                                            }     

    if len(issue_dicts) == 0:
        print("No issues found while processing")  
        return

    with GithubTaskSession(logger, engine) as session:

        # remove duplicate contributors before inserting
        contributors = remove_duplicate_dicts(contributors)

        # insert contributors from these issues
        logger.info(f"{task_name}: Inserting {len(contributors)} contributors")
        session.insert_data(contributors, Contributor, ["cntrb_id"])
                            

        # insert the issues into the issues table. 
        # issue_urls are gloablly unique across github so we are using it to determine whether an issue we collected is already in the table
        # specified in issue_return_columns is the columns of data we want returned. This data will return in this form; {"issue_url": url, "issue_id": id}
        logger.info(f"{task_name}: Inserting {len(issue_dicts)} issues")
        issue_natural_keys = ["repo_id", "gh_issue_id"]
        issue_return_columns = ["issue_url", "issue_id"]
        issue_string_columns = ["issue_title", "issue_body"]
        try:
            issue_return_data = session.insert_data(issue_dicts, Issue, issue_natural_keys, return_columns=issue_return_columns, string_fields=issue_string_columns)
        except IntegrityError as e:
            logger.error(f"Ran into integrity error:{e} \n Offending data: \n{issue_dicts}")

            if development:
                raise e
        # loop through the issue_return_data so it can find the labels and 
        # assignees that corelate to the issue that was inserted labels 
        issue_label_dicts = []
        issue_assignee_dicts = []
        for data in issue_return_data:

            issue_url = data["issue_url"]
            issue_id = data["issue_id"]

            try:
                other_issue_data = issue_mapping_data[issue_url]
            except KeyError as e:
                logger.info(f"{task_name}: Cold not find other issue data. This should never happen. Error: {e}")


            # add the issue id to the lables and assignees, then add them to a list of dicts that will be inserted soon
            dict_key = "issue_id"
            issue_label_dicts += add_key_value_pair_to_dicts(other_issue_data["labels"], "issue_id", issue_id)
            issue_assignee_dicts += add_key_value_pair_to_dicts(other_issue_data["assignees"], "issue_id", issue_id)


        logger.info(f"{task_name}: Inserting other issue data of lengths: Labels: {len(issue_label_dicts)} - Assignees: {len(issue_assignee_dicts)}")

        # inserting issue labels
        # we are using label_src_id and issue_id to determine if the label is already in the database.
        issue_label_natural_keys = ['label_src_id', 'issue_id']
        issue_label_string_fields = ["label_text", "label_description"]
        session.insert_data(issue_label_dicts, IssueLabel,
                            issue_label_natural_keys, string_fields=issue_label_string_fields)
    
        # inserting issue assignees
        # we are using issue_assignee_src_id and issue_id to determine if the label is already in the database.
        issue_assignee_natural_keys = ['issue_assignee_src_id', 'issue_id']
        session.insert_data(issue_assignee_dicts, IssueAssignee, issue_assignee_natural_keys)



def process_issue_contributors(issue, tool_source, tool_version, data_source):

    contributors = []

    issue_cntrb = extract_needed_contributor_data(issue["user"], tool_source, tool_version, data_source)
    issue["cntrb_id"] = issue_cntrb["cntrb_id"]
    contributors.append(issue_cntrb)

    for assignee in issue["assignees"]:

        issue_assignee_cntrb = extract_needed_contributor_data(issue["user"], tool_source, tool_version, data_source)
        assignee["cntrb_id"] = issue_assignee_cntrb["cntrb_id"]
        contributors.append(issue_assignee_cntrb)

    return issue, contributors


def is_valid_pr_block(issue):
    return (
        'pull_request' in issue and issue['pull_request']
        and isinstance(issue['pull_request'], dict) and 'url' in issue['pull_request']
    )
