import time
import logging

from typing import Dict, List, Tuple, Optional

from augur.application.db.data_parse import *
from augur.application.db.session import DatabaseSession
from augur.tasks.init.celery_app import engine
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.util.util import add_key_value_pair_to_dicts
from augur.tasks.util.worker_util import remove_duplicate_dicts
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, PullRequestMessageRef, Contributor, Repo

PLATFORM_ID = 1

#TODO: Document tool_source, tool_source, data_source

def extract_data_from_pr(pr_data: dict, 
                        repo_id: int, 
                        tool_source: str, 
                        tool_version: str, 
                        data_source: str) -> Tuple[dict, List[dict], List[dict], List[dict], List[dict], List[dict]]:
    """Extract needed data from single pull request.

    Args:
        pr_data: a pull request from the github api
        repo_id: an integer representing the repo a repo in the repos table

    Returns:
        A tuples that includes
            The needed data from the pr
            The needed data for pr labels
            The needed data for pr assignees
            The needed data for pr reviewers
            The needed data for pr meatadata
            The contributors found amongst all the pull request data
    """
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
    pr_labels = extract_needed_pr_label_data(pr_data["labels"], repo_id,
                                                    tool_source, tool_version, data_source)

    # get only the needed data for the pull_request_assignees table
    pr_assignees = extract_needed_pr_assignee_data(pr_data["assignees"], repo_id,
                                                            tool_source, tool_version, data_source)

    # get only the needed data for the pull_request_reviewers table
    pr_reviewers = extract_needed_pr_reviewer_data(pr_data["requested_reviewers"], repo_id,
                                                            tool_source, tool_version, data_source)

    # get only the needed data for the pull_request_meta table
    pr_metadata = extract_needed_pr_metadata(pr_data["metadata"], repo_id,
                                                    tool_source, tool_version, data_source)                                                                      

    return pr_needed_data, pr_labels, pr_assignees, pr_reviewers, pr_metadata, contributor_data


def extract_data_from_pr_list(pull_requests: List[dict], 
                                repo_id: int, 
                                tool_source: str, 
                                tool_version: str, 
                                data_source: str) -> Tuple[List[dict], 
                                                            Dict[str, Dict[str, List[dict]]], 
                                                            List[int], 
                                                            List[dict]
                                                        ]:
    """Extract needed data from list of pull requests

    Note:
        This also organizes the other pull request data like labels and assignees, in a way that will make it easy to map them to the pull requests after the pull request has been inserted

    Args:
        pull_requests: list of pr dicts
        repo_id: an integer representing the repo a repo in the repos table

    Returns:
        A tuple containing
            A list of pull requests with the data needed for insertion
            A dictionairy with the keys being pr urls and the value being 
                a dict containing labels, assignees, reviewers, and metadata. 
                This is structured in this way to allow for easy mapping back 
                to the prs after they are inserted
            A list of pr numbers to pass to the pr reviews task
            A list of contributors found amongst all the pull request data in the list
    """            
    pr_mapping_data = {}
    pr_dicts = [] 
    pr_numbers = []
    contributors = []
    
    for pr in pull_requests:

        pr_data, labels, assignees, reviewers, metadata, contributor_data = extract_data_from_pr(pr, repo_id, tool_source, tool_version, data_source)

        contributors += contributor_data

        pr_dicts.append(pr_data)
       
        mapping_data_key = pr_data["pr_url"]
        pr_mapping_data[mapping_data_key] = {
                                            "labels": labels,
                                            "assignees": assignees,
                                            "reviewers": reviewers,
                                            "metadata": metadata,
                                            }          
       
         # create a list of pr numbers to pass for the pr reviews task
        pr_numbers.append(pr_data["pr_src_number"]) 

    return pr_dicts, pr_mapping_data, pr_numbers, contributors


def insert_pr_contributors(contributors: List[dict], session: GithubTaskSession, task_name: str) -> None:
    """Insert pr contributors
    
    Args:
        contributors: the contributor data that is being inserted
        session: database session to insert the data with
        task_name: to differiante between log statements since there are multiple tasks of the same type
    """

    # remove duplicate contributors before inserting
    contributors = remove_duplicate_dicts(contributors)

    # insert contributors from these prs
    session.logger.info(f"{task_name}: Inserting {len(contributors)} contributors")
    session.insert_data(contributors, Contributor, ["cntrb_id"])


def insert_prs(pr_dicts: List[dict], session: GithubTaskSession, task_name: str) -> Optional[List[dict]]:
    """Insert pull requests
    
    Args:
        pr_dicts: the pull request data that is being inserted
        session: database session to insert the data with
        task_name: to differiante between log statements since there are multiple tasks of the same type

    Returns:
        list of dicts that contain a pr_url and a pull_request_id. 
            So we can determine what labels, assigness, and other data belong to each pr
    """

    session.logger.info(f"{task_name}: Inserting prs of length: {len(pr_dicts)}")
    pr_natural_keys = ["pr_url"]
    pr_return_columns = ["pull_request_id", "pr_url"]
    pr_return_data = session.insert_data(pr_dicts, PullRequest, pr_natural_keys, return_columns=pr_return_columns)

    return pr_return_data

def map_other_pr_data_to_pr(
                            pr_return_data: List[dict], 
                            pr_mapping_data: Dict[str, Dict[str, List[dict]]], 
                            logger: logging.Logger) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    """Map labels, assigness, reviewers, and metadata to their respecive prs
    
    Args:
        pr_return_data: list of dicts containing pr urls and pull request ids
        pr_mapping_data: dict containing pr urls as the keys and the values 
            being a dict containing other related pr data
        logger: handles logging

    Returns:
        A tuple containing
            list of labels that have pull request ids
            list of assignees that have pull request ids
            list of reviewers that have pull request ids
            list of metadata that have pull request ids
    """

    pr_label_dicts = []
    pr_assignee_dicts = []
    pr_reviewer_dicts = []
    pr_metadata_dicts = []
    for data in pr_return_data:

        pr_url = data["pr_url"]
        pull_request_id = data["pull_request_id"]

        try:
            other_pr_data = pr_mapping_data[pr_url]
        except KeyError as e:
            logger.info(f"Cold not find other pr data. This should never happen. Error: {e}")


        # add the pull_request_id to the labels, assignees, reviewers, or metadata then add them to a list of dicts that will be inserted soon
        dict_key = "pull_request_id"
        pr_label_dicts += add_key_value_pair_to_dicts(other_pr_data["labels"], dict_key, pull_request_id)
        pr_assignee_dicts += add_key_value_pair_to_dicts(other_pr_data["assignees"], dict_key, pull_request_id)
        pr_reviewer_dicts += add_key_value_pair_to_dicts(other_pr_data["reviewers"], dict_key, pull_request_id)
        pr_metadata_dicts += add_key_value_pair_to_dicts(other_pr_data["metadata"], dict_key, pull_request_id)

    return pr_label_dicts, pr_assignee_dicts, pr_reviewer_dicts, pr_metadata_dicts 


def insert_pr_labels(labels: List[dict], logger: logging.Logger) -> None:
    """Insert pull request labels

    Note:
        This assumes the labels have pull request ids and only the data needed for the database

    Args:
        labels: list of labels to insert
        logger: handles logging
    """
    with DatabaseSession(logger) as session:

        # we are using pr_src_id and pull_request_id to determine if the label is already in the database.
        pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
        session.insert_data(labels, PullRequestLabel, pr_label_natural_keys)


def insert_pr_assignees(assignees: List[dict], logger: logging.Logger) -> None:
    """Insert pull request assignees

    Note:
        This assumes the assignees have pull request ids and only the data needed for the database

    Args:
        assignees: list of assignees to insert
        logger: handles logging
    """
    with DatabaseSession(logger) as session:

        # we are using pr_assignee_src_id and pull_request_id to determine if the label is already in the database.
        pr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
        session.insert_data(assignees, PullRequestAssignee, pr_assignee_natural_keys)


def insert_pr_reviewers(reviewers: List[dict], logger: logging.Logger) -> None:
    """Insert pull request reviewers

    Note:
        This assumes the reviewers have pull request ids and only the data needed for the database

    Args:
        reviewers: list of reviewers to insert
        logger: handles logging
    """
    with DatabaseSession(logger) as session:

        # we are using pr_src_id and pull_request_id to determine if the label is already in the database.
        pr_reviewer_natural_keys = ["pull_request_id", "pr_reviewer_src_id"]
        session.insert_data(reviewers, PullRequestReviewer, pr_reviewer_natural_keys)


def insert_pr_metadata(metadata: List[dict], logger: logging.Logger) -> None:
    """Insert pull request metadata

    Note:
        This assumes the metadata have pull request ids and only the data needed for the database

    Args:
        metadata: list of metadata to insert
        logger: handles logging
    """
    with DatabaseSession(logger) as session:

        # inserting pr metadata
        # we are using pull_request_id, pr_head_or_base, and pr_sha to determine if the label is already in the database.
        pr_metadata_natural_keys = ['pull_request_id', 'pr_head_or_base', 'pr_sha']
        session.insert_data(metadata, PullRequestMeta, pr_metadata_natural_keys)




# TODO: Should we insert metadata without user relation?
# NOTE: For contributor related operations: extract_needed_contributor_data takes a piece of github contributor data
# and creates a cntrb_id (primary key for the contributors table) and gets the data needed for the table
def process_pull_request_contributors(pr: dict, tool_source: str, tool_version: str, data_source: str) -> Tuple[dict, List[dict]]:

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