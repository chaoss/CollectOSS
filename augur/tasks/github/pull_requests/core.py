import time
import logging

from augur import queue_name
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.data_parse import *
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.util.worker_util import wait_child_tasks
from augur.tasks.github.util.util import remove_duplicate_dicts, add_key_value_pair_to_list_of_dicts, get_owner_repo
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, PullRequestMessageRef, Contributor, Repo


platform_id = 1


def extract_data_from_pr_list(pr_list):

    prs = None
    other_pr_map_data = None
    pr_numbers = None

    return prs, other_pr_data_map, pr_numbers


def extract_data_from_pr(pr_data, repo_id, tool_source, tool_version, data_source):

    # adds cntrb_id to reference the contributors table to the 
    # prs, assignees, reviewers, and metadata
    pr_data, contributor_data = process_pull_request_contributors(pr_data, tool_source, tool_version, data_source)

    # add a field called pr_head_or_base to the head and base field of the pr
    # this is done so we can insert them both into the pr metadata table
    # and still determine whether it is a head or base
    pr_data['head'].update(
        {'pr_head_or_base': 'head'}
    )
    pr_data['base'].update(
        {'pr_head_or_base': 'base'}
    )

    # add metadata field to pr
    pr_data.update(
        {"metadata": [pr_data["head"], pr_data["base"]]}
    )

    # create list of pr_dicts to bulk insert later

    pr_needed_data = extract_needed_pr_data(pr_data, repo_id, tool_source,tool_version)

    # get only the needed data for the pull_request_labels table
    pr_labels = extract_needed_pr_label_data(pr_data["labels"],  platform_id, repo_id,
                                                    tool_source, tool_version, data_source)

    # get only the needed data for the pull_request_assignees table
    pr_assignees = extract_needed_pr_assignee_data(pr_data["assignees"], platform_id, repo_id,
                                                            tool_source, tool_version, data_source)

    # get only the needed data for the pull_request_reviewers table
    pr_reviewers = extract_needed_pr_reviewer_data(pr_data["requested_reviewers"], platform_id, repo_id,
                                                            tool_source, tool_version, data_source)

    # get only the needed data for the pull_request_meta table
    pr_metadata = extract_needed_pr_metadata(pr_data["metadata"], platform_id, repo_id,
                                                    tool_source, tool_version, data_source)                                                                      

    return pr_needed_data, pr_labels, pr_assignees, pr_reviewers, pr_metadata, contributor_data

def insert_pr_contributors(contributors):

    pass


def insert_prs(prs):

    pr_mapping_dict = None

    return pr_mapping_dict

def map_other_pr_data_to_pr(pr_mapping_dict, pr_dict):

    labels = None
    assignees = None
    reviewers  = None
    reviewers = None
    metadata = None

    return labels, assignees, reviewers, metadata 


def insert_other_pr_data(labels, assignees, reviewers, metadata):

    pass



# TODO: Should we insert metadata without user relation?
# NOTE: For contributor related operations: extract_needed_contributor_data takes a piece of github contributor data
# and creates a cntrb_id (primary key for the contributors table) and gets the data needed for the table
def process_pull_request_contributors(pr, tool_source, tool_version, data_source):

    contributors = []

    # get contributor data and set pr cntrb_id
    pr_cntrb = extract_needed_contributor_data(pr["user"], tool_source, tool_version, data_source)
    pr["cntrb_id"] = pr_cntrb["cntrb_id"]

    contributors.append(pr_cntrb)


    if pr["base"]["user"]:

        # get contributor data and set pr metadat cntrb_id
        pr_meta_base_cntrb = extract_needed_contributor_data(pr["base"]["user"], tool_source, tool_version, data_source)
        pr["base"]["cntrb_id"] = pr_meta_base_cntrb["cntrb_id"]

        contributors.append(pr_meta_base_cntrb)

    if pr["head"]["user"]:

        pr_meta_head_cntrb = extract_needed_contributor_data(pr["head"]["user"], tool_source, tool_version, data_source)
        pr["head"]["cntrb_id"] = pr_meta_head_cntrb["cntrb_id"]

        contributors.append(pr_meta_head_cntrb)

    # set cntrb_id for assignees
    for assignee in pr["assignees"]:

        pr_asignee_cntrb = extract_needed_contributor_data(assignee, tool_source, tool_version, data_source)
        assignee["cntrb_id"] = pr_asignee_cntrb["cntrb_id"]

        contributors.append(pr_asignee_cntrb)


    # set cntrb_id for reviewers
    for reviewer in pr["requested_reviewers"]:

        pr_reviwer_cntrb = extract_needed_contributor_data(reviewer, tool_source, tool_version, data_source)
        reviewer["cntrb_id"] = pr_reviwer_cntrb["cntrb_id"]

        contributors.append(pr_reviwer_cntrb)

    return pr, contributors