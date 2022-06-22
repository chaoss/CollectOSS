from typing import Any, Union, Optional
from dataclasses import dataclass
from enforce_typing import enforce_types

import json
from celery import group, chain, chord, signature
from celery.utils.log import get_task_logger


import time
import traceback
import logging
import sys

import sqlalchemy as s

from .main import app
from .main import redis_conn

from .db_models import PullRequests, Message, PullRequestReviews, PullRequestLabels, PullRequestReviewers, PullRequestEvents, PullRequestMeta, PullRequestAssignees, PullRequestReviewMessageRef, SQLAlchemy, Issues, IssueEvents

from .github_paginator import GithubPaginator
from .worker_base import TaskSession



config_path = '../augur/augur.config.json'


with open(config_path, 'r') as f:
    config = json.load(f)

# creates a class that is sub class of the sqlalchemy.orm.Session class that additional methods and fields added to it. 

@celery.task
def start(owner: str, repo):
    
    logger = get_task_logger(start.name)
    session = TaskSession(logger, config)

    logger.info(f"Collecting data for {owner}/{repo}")
    logger.info("Prepping to start pr comments, pr events, and pr reviews")

    start_tasks_group = group(pull_requests.s(owner, repo), issues.s(owner, repo))

    start_tasks_group.apply_async()

    logger.info("Made it")
    logger.info(f"Group id: {start_tasks_group.id}")




    # secondary_task_list = []
    # # task_list.append(pull_request_reviews.s(owner, repo))
    # # secondary_task_list.append(github_events.s(owner, repo))
    # # task_list.append(github_messages.s(owner, repo))
    
    # secondary_task_group = group(secondary_task_list)

    # job = chain(
    #     start_tasks_group,
    #     secondary_task_group,
    # )

    # job.apply_async()


@celery.task
def pull_requests(owner: str, repo: str) -> None:

    logger = get_task_logger(pull_requests.name)
    session = TaskSession(logger, config)

    logger.info(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&direction=desc"
    

    # get repo_id or have it passed
    repo_id = 1
    tool_source = "Pr Task"
    tool_version = "2.0"
    platform_id = 25150
    data_source = "Github API"

    pr_natural_keys = ["pr_url"]

    # returns an iterable of all prs at this url
    prs = GithubPaginator(url, session.oauths, logger)

    # logger.info(f"Pages collected: length: {len(prs)}")

    pr_label_dicts = []
    pr_assignee_dicts = []
    pr_reviewer_dicts = []
    pr_metadata_dicts = []

    repo_pr_numbers = []

    # creating a list, because we would like to bulk insert in the future

    len_prs = len(prs)
    for index, pr in enumerate(prs):

        if index == 100:
            break

        pr['head'].update(
            {'pr_head_or_base': 'head'}
        )
        pr['base'].update(
            {'pr_head_or_base': 'base'}
        )

        logger.info(f"Inserting pr {index + 1} of {len_prs}")
        pr_object = PrObject(pr, repo_id, tool_source,
                             tool_version)

        # when the object gets inserted the db_row is added to the object which is a PullRequests orm object (so it contains all the column values)
        session.insert_data([pr_object], PullRequests, pr_natural_keys)

        if pr_object.db_row is None:
            logger.info("Error while inserting pr, skipping other data")
            continue

        pr_label_dicts += extract_needed_pr_label_data(pr_object.labels, pr_object.db_row.pull_request_id,  platform_id, repo_id,
                                                       tool_source, tool_version, data_source)

        pr_assignee_dicts += extract_needed_pr_assignee_data(pr_object.assignees, pr_object.db_row.pull_request_id, platform_id, repo_id,
                                                             tool_source, tool_version, data_source)

        pr_reviewer_dicts += extract_needed_pr_reviewer_data(pr_object.reviewers, pr_object.db_row.pull_request_id, platform_id, repo_id,
                                                             tool_source, tool_version, data_source)

        pr_metadata_dicts += extract_needed_pr_metadata(pr_object.metadata, pr_object.db_row.pull_request_id, platform_id, repo_id,
                                                        tool_source, tool_version, data_source)

        # get a list of pr numbers to pass for the pr reviews task
        repo_pr_numbers.append(pr["number"]) 


    # logger.info(f"\nInserting pr labels of length: {len(pr_label_dicts)}")
    # pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
    # session.insert_data(pr_label_dicts, PullRequestLabels, pr_label_natural_keys)
  

    # logger.info(f"\nInserting pr assignees of length: {len(pr_assignee_dicts)}")
    # pr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
    # session.insert_data(pr_assignee_dicts, PullRequestAssignees, pr_assignee_natural_keys)
 

    # logger.info(f"\nInserting pr reviewers of length: {len(pr_reviewer_dicts)}")
    # pr_reviewer_natural_keys = ["pr_reviewer_src_id", "pull_request_id"]
    # session.insert_data(pr_reviewer_dicts, PullRequestReviewers, pr_reviewer_natural_keys)
    

    start_time = time.time()
    logger.info(f"\nBulk Inserting pr metadata of length: {len(pr_metadata_dicts)}")
    pr_metadata_natural_keys = ['pull_request_id', 'pr_head_or_base', 'pr_sha']
    session.insert_bulk_data(pr_metadata_dicts, PullRequestMeta, pr_metadata_natural_keys)
    
    total_time = time.time() - start_time

    print(f"{total_time} seconds to insert metadata")



# retrieve only the needed data for pr labels from the api response
def extract_needed_pr_label_data(labels: [dict], pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> [dict]:

    if len(labels) == 0:
        return []

    label_dicts = []
    for label in labels:

        label_dict = {
            'pull_request_id': pr_id,
            'pr_src_id': int(label['id']),
            'pr_src_node_id': label['node_id'],
            'pr_src_url': label['url'],
            'pr_src_description': label['name'],
            'pr_src_color': label['color'],
            'pr_src_default_bool': label['default'],
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

        # label_obj = PullRequestLabels(**label_dict)

        label_dicts.append(label_dict)

    return label_dicts

# retrieve only the needed data for pr assignees from the api response
def extract_needed_pr_assignee_data(assignees: [dict], pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> [dict]:

    if len(assignees) == 0:
        return []


    assignee_dicts = []
    for assignee in assignees:

        assignee_dict = {
            'pull_request_id': pr_id,
            'contrib_id': None,
            'pr_assignee_src_id': int(assignee['id']),
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

        assignee_dicts.append(assignee_dict)

    return assignee_dicts

# retrieve only the needed data for pr reviewers from the api response
def extract_needed_pr_reviewer_data(reviewers: [dict], pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> [dict]:

    if len(reviewers) == 0:
        return []

    reviewer_dicts = []
    for reviewer in reviewers:

        reviewer_dict = {
            'pull_request_id': pr_id,
            'cntrb_id': None,
            'pr_reviewer_src_id': int(float(reviewer['id'])),
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

    reviewer_dicts.append(reviewer_dict)

    return reviewer_dicts


def extract_needed_pr_metadata(metadata_list: [dict], pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> [dict]:

    if len(metadata_list) == 0:
        return []

    metadata_dicts = []
    for meta in metadata_list:

        metadata_dict = {
            'pull_request_id': pr_id,
            'pr_head_or_base': meta['pr_head_or_base'],
            'pr_src_meta_label': meta['label'],
            'pr_src_meta_ref': meta['ref'],
            'pr_sha': meta['sha'],
            # Cast as int for the `nan` user by SPG on 11/28/2021; removed 12/6/2021
            'cntrb_id': None,
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

        metadata_dicts.append(metadata_dict)

    return metadata_dicts



@celery.task
def pull_request_review_comments(owner: str, repo: str) -> None:

    logger = get_task_logger(pull_request_review_comments.name)
    session = TaskSession(logger, config)

    logger.info(f"Collecting pull request comments for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/comments"

    pr_comments = GithubPaginator(url, session.oauths)

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"
    pr_comment_natural_keys = ["platform_msg_id"]
    pr_comment_ref_natural_keys = ["pr_review_msg_src_id"]

    pr_comment_ref_dicts = []

    pr_comment_len = len(pr_comments)

    logger.info(f"Pr comments len: {pr_comment_len}")
    for index, comment in enumerate(pr_comments):

        # pr url associated with this comment
        comment_pr_url = comment["pull_request_url"]

        related_pr = PullRequests.query.filter_by(pr_url=comment_pr_url).one()

        if not related_pr:
            logger.info(
                f"Error can't find pr for pr comment with id: {comment['id']}")
            continue

        pr_id = related_pr.pull_request_id

        pr_comment_object = PrCommentObject(comment, platform_id, repo_id, tool_source, tool_version, data_source)

        logger.info(f"Inserting pr review comment {index + 1} of {pr_comment_len}")
        session.insert_data([pr_comment_object], Message, pr_comment_natural_keys)

        msg_id = pr_comment_object.db_row.msg_id

        pr_comment_ref = extract_pr_comment_ref_data(
            comment, pr_id, msg_id, repo_id, tool_source, tool_version, data_source)

        logger.info(pr_comment_ref)

        pr_comment_ref_dicts.append(
            pr_comment_ref
        )

        # pr_comment_ref_dicts.append(
        #     extract_pr_comment_ref_data(comment, pr_id, msg_id, repo_id, tool_source, tool_version, data_source)
        # )

    logger.info(f"Insert pr comment refs")
    session.insert_data(pr_comment_ref_dicts, PullRequestReviewMessageRef, pr_comment_ref_natural_keys)


def extract_pr_comment_ref_data(comment: dict, pr_id: int, msg_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> dict:

    pr_review_comment_message_ref = {
        'pr_review_id':  pr_id,
        # msg_id turned up null when I removed the cast to int ..
        'msg_id': msg_id,
        'pr_review_msg_url': comment['url'],
        'pr_review_src_id': int(comment['pull_request_review_id']),
        'pr_review_msg_src_id': int(comment['id']),
        'pr_review_msg_node_id': comment['node_id'],
        'pr_review_msg_diff_hunk': comment['diff_hunk'],
        'pr_review_msg_path': comment['path'],
        'pr_review_msg_position': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['position']
        ) else comment['position'],
        'pr_review_msg_original_position': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['original_position']
        ) else comment['original_position'],
        'pr_review_msg_commit_id': str(comment['commit_id']),
        'pr_review_msg_original_commit_id': str(comment['original_commit_id']),
        'pr_review_msg_updated_at': comment['updated_at'],
        'pr_review_msg_html_url': comment['html_url'],
        'pr_url': comment['pull_request_url'],
        'pr_review_msg_author_association': comment['author_association'],
        'pr_review_msg_start_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['start_line']
        ) else comment['start_line'],
        'pr_review_msg_original_start_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['original_start_line']
        ) else int(comment['original_start_line']),
        'pr_review_msg_start_side': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            str(comment['start_side'])
        ) else str(comment['start_side']),
        'pr_review_msg_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['line']
        ) else int(comment['line']),
        'pr_review_msg_original_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['original_line']
        ) else int(comment['original_line']),
        'pr_review_msg_side': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            str(comment['side'])
        ) else str(comment['side']),
        'tool_source': 'pull_request_reviews model',
        'tool_version': tool_version + "_reviews",
        'data_source': data_source,
        'repo_id': repo_id
    }

    # pr_comment_msg_ref = {
    #     'pull_request_id': pr_id,
    #     # to cast, or not to cast. That is the question. 12/6/2021
    #     'msg_id': msg_id,
    #     'pr_message_ref_src_comment_id': int(comment['id']),
    #     'pr_message_ref_src_node_id': comment['node_id'],
    #     'tool_source': tool_source,
    #     'tool_version': tool_version,
    #     'data_source': data_source,
    #     'repo_id': repo_id
    # }

    return pr_review_comment_message_ref

@celery.task
def github_events(owner: str, repo: str):

    logger = get_task_logger(github_events.name)
    logger.info(f"Collecting pull request events for {owner}/{repo}")
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"
    
    pr_events = GithubPaginator(url, session.oauths)

    data = []
    for pr_event in pr_events:
        data.append(pr_event)

    # len_pr_events = len(pr_events)

    # logger.info(f"Length of pr events: {len_pr_events}")

    # logger.info(f"Number of tasks with 500 events: {len_pr_events // 500}")

    # events_per_task = 500
    # max_tasks = 5

    # if len_pr_events > (max_tasks * 1000):
    #     events_per_task = len_pr_events // max_tasks
    #     # round up the events per task so we ensure no more than 5 tasks are spawned
    #     events_per_task += 1
    logger.info(len(data))

    min_events_per_task = 250
    max_tasks = 1

    chunked_data = chunk_data(data, min_events_per_task, max_tasks)

    
    task_list = [process_events.s(data) for data in chunked_data]

    process_events_job = group(task_list)

    result = process_events_job.apply_async()

    logger.info(result.ready())

    logger.info(result.successful())

    total_time = time.time() - start_time
    logger.info(f"{total_time} to complete github events for {owner}/{repo}")


def chunk_data(data, min_events_per_task, max_tasks):

    data_length = len(data)

    events_per_task = (data_length // max_tasks) + 1

    if min_events_per_task > events_per_task:
        events_per_task = min_events_per_task

    end = 0
    index = 0
    chunked_data = []
    while(end + 1 < data_length):

        start = index * events_per_task
        end = start + events_per_task        
        list_slice = data[slice(start, end)]
        chunked_data.append(list_slice)

        index+=1

    return chunked_data

@celery.task
def process_events(events):

    logger = get_task_logger(process_events.name)
    session = TaskSession(logger, config)

    logger.info(f"Len of events: {len(events)}")
    logger.info(f"Type of events: {type(events)}")

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"
    # TODO: Could replace this with "id" but it isn't stored on the table for some reason
    pr_event_natural_keys = ["platform_id", "node_id"]
    issue_event_natural_keys = ["issue_id", "issue_event_src_id"]
    pr_event_dicts = []
    issue_event_dicts = []

    for index, event in enumerate(events):
        
        logger.info(f"Proccessing event {index + 1} of {len(events)}")

        if 'pull_request' in list(event["issue"].keys()):
            pr_url = event["issue"]["pull_request"]["url"]

            try:
                related_pr = PullRequests.query.filter_by(pr_url=pr_url).one()
            except s.orm.exc.NoResultFound:
                logger.info("Could not find related pr")
                logger.info(f"We were searching for: {pr_url}")
                # TODO: Add table to log all errors
                logger.info("Skipping")
                continue

            pr_event_dicts.append(
                extract_pr_event_data(event, related_pr.pull_request_id, platform_id, repo_id,
                                      tool_source, tool_version, data_source)
            )

        else:
            issue_url = event["issue"]["url"]

            try:
                related_issue = Issues.query.filter_by(issue_url=issue_url).one()
            except s.orm.exc.NoResultFound:
                logger.info("Could not find related pr")
                logger.info(f"We were searching for: {issue_url}")
                # TODO: Add table to log all errors
                logger.info("Skipping")
                continue

            issue_event_dicts.append(
                extract_issue_event_data(event, related_issue.issue_id, platform_id, repo_id,
                                         tool_source, tool_version, data_source)
            )

    logger.info(f"Issue event count: {len(issue_event_dicts)}")
    logger.info(f"Pr event count: {len(pr_event_dicts)}")

    logger.info("Inserting all pr events")
    session.insert_data(pr_event_dicts, PullRequestEvents, pr_event_natural_keys)

    logger.info("Inserting all issue events")
    session.insert_data(issue_event_dicts, IssueEvents, issue_event_natural_keys)

def extract_pr_event_data(event: dict, pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> dict:

    # TODO: Add db pull request id

    pr_event = {
        'pull_request_id': pr_id,
        'cntrb_id': None,
        'action': event['event'],
        'action_commit_hash': None,
        'created_at': event['created_at'],
        'issue_event_src_id': int(event['issue']["id"]),
        'node_id': event['node_id'],
        'node_url': event['url'],
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': data_source,
        'pr_platform_event_id': int(event['issue']["id"]),
        'platform_id': platform_id,
        'repo_id': repo_id
    }

    return pr_event


def extract_issue_event_data(event: dict, issue_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> dict:

    # TODO: Add db pull request id

    issue_event = {
        'issue_event_src_id': int(event['id']),
        'issue_id': issue_id,
        'node_id': event['node_id'],
        'node_url': event['url'],
        'cntrb_id': None,
        'created_at': event['created_at'] if (
            event['created_at']
        ) else None,
        'action': event['event'],
        'action_commit_hash': event['commit_id'],
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': data_source,
        'repo_id': repo_id,
        'platform_id': platform_id
    }

    return issue_event

# do this task after others because we need to add the multi threading like we did it before
@celery.task
def pull_request_reviews(owner: str, repo: str, pr_number_list: [int]) -> None:

    logger = get_task_logger(pull_request_reviews.name)
    session = TaskSession(logger, config)

    logger.info(f"Collecting pull request reviews for {owner}/{repo}")

    # for pr_number in pr_number_list:

    #     url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

        # add pr review


def create_pr_review_object(review: dict, platform_id: int, repo_id: int, tool_version: str, data_source: str):

    # TODO: Add db pull request id

    return PullRequestReviews(
        #pull_request_id=review['pull_request_id'],
        cntrb_id=None,
        pr_review_author_association=review['author_association'],
        pr_review_state=review['state'],
        pr_review_body=str(review['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
            review['body']
        ) else None,
        pr_review_submitted_at=review['submitted_at'] if (
            'submitted_at' in review
        ) else None,
        # 12/3/2021 cast as int due to error. # Here, `pr_review_src_id` is mapped to `id` SPG 11/29/2021. This is fine. Its the review id.
        pr_review_src_id=int(float(review['id'])),
        pr_review_node_id=review['node_id'],
        pr_review_html_url=review['html_url'],
        pr_review_pull_request_url=review['pull_request_url'],
        pr_review_commit_id=review['commit_id'],
        tool_source='pull_request_reviews model',
        tool_version= tool_version + "_reviews",
        data_source=data_source,
        repo_id=repo_id,
        platform_id=platform_id
    )

class GithubObject():

    def __init__(self, data: dict):

        self.data = data
        self.db_row = None

    def set_db_row(self, row):
        self.db_row = row

    def get_dict(self) -> dict:
        return self.data


class PrObject(GithubObject):
    def __init__(self, pr: dict, repo_id: int, tool_source: str, tool_version: str):

        dict_data = {
            'repo_id': repo_id,
            'pr_url': pr['url'],
            # 1-22-2022 inconsistent casting; sometimes int, sometimes float in bulk_insert
            'pr_src_id': int(str(pr['id']).encode(encoding='UTF-8').decode(encoding='UTF-8')),
            # 9/20/2021 - This was null. No idea why.
            'pr_src_node_id': pr['node_id'],
            'pr_html_url': pr['html_url'],
            'pr_diff_url': pr['diff_url'],
            'pr_patch_url': pr['patch_url'],
            'pr_issue_url': pr['issue_url'],
            'pr_augur_issue_id': None,
            'pr_src_number': pr['number'],
            'pr_src_state': pr['state'],
            'pr_src_locked': pr['locked'],
            'pr_src_title': str(pr['title']),
            'pr_augur_contributor_id': None,
            ### Changed to int cast based on error 12/3/2021 SPG (int cast above is first change on 12/3)
            'pr_body': str(pr['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
                pr['body']
            ) else None,
            'pr_created_at': pr['created_at'],
            'pr_updated_at': pr['updated_at'],
            'pr_closed_at': None if not (
                pr['closed_at']
            ) else pr['closed_at'],
            'pr_merged_at': None if not (
                pr['merged_at']
            ) else pr['merged_at'],
            'pr_merge_commit_sha': pr['merge_commit_sha'],
            'pr_teams': None,
            'pr_milestone': None,
            'pr_commits_url': pr['commits_url'],
            'pr_review_comments_url': pr['review_comments_url'],
            'pr_review_comment_url': pr['review_comment_url'],
            'pr_comments_url': pr['comments_url'],
            'pr_statuses_url': pr['statuses_url'],
            'pr_meta_head_id': None if not (
                pr['head']
            ) else pr['head']['label'],
            'pr_meta_base_id': None if not (
                pr['base']
            ) else pr['base']['label'],
            'pr_src_issue_url': pr['issue_url'],
            'pr_src_comments_url': pr['comments_url'],
            'pr_src_review_comments_url': pr['review_comments_url'],
            'pr_src_commits_url': pr['commits_url'],
            'pr_src_statuses_url': pr['statuses_url'],
            'pr_src_author_association': pr['author_association'],
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': 'GitHub API'
        }

        self.labels = pr["labels"]
        self.assignees = pr["assignees"]
        self.reviewers = pr["requested_reviewers"]
        self.metadata = [pr["head"], pr["base"]]

        super().__init__(dict_data)


class PrCommentObject(GithubObject):
    def __init__(self, comment: dict, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str):

        dict_data = {
            'pltfrm_id': platform_id,
            'msg_text': str(comment['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
                comment['body']
            ) else None,
            'msg_timestamp': comment['created_at'],
            'cntrb_id': None,
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id,
            'platform_msg_id': int(comment['id']),
            'platform_node_id': comment['node_id']
        }

        super().__init__(dict_data)


@celery.task
def issues(owner: str, repo: str) -> None:

    logger = get_task_logger(start.name)
    session = TaskSession(logger, config)

    print(f"Collecting issues for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"

    # get repo_id or have it passed
    repo_id = 1
    tool_source = "Issue Task"
    tool_version = "2.0"
    # platform_id = 25150
    data_source = "Github API"

    issue_natural_keys = ["issue_url"]

    # returns an iterable of all prs at this url
    issues = GithubPaginator(url, session.oauths, logger)

    # issue_label_dicts = []
    # issue_assignee_dicts = []
 

    # creating a list, because we would like to bulk insert in the future
    len_issues = len(issues)
    issue_total = len_issues
    print(f"Length of issues: {len_issues}")
    for index, issue in enumerate(issues):

        print(f"Inserting issue {index + 1} of {len_issues}")

        if is_valid_pr_block(issue) is True:
            issue_total-=1
            continue

        issue_object = IssueObject(issue, repo_id, tool_source, tool_version, data_source)

        # when the object gets inserted the db_row is added to the object which is a PullRequests orm object (so it contains all the column values)
        session.insert_data([issue_object], Issues, issue_natural_keys)

    print(f"{issue_total} issues inserted")

def is_valid_pr_block(issue):
    return (
        'pull_request' in issue and issue['pull_request']
        and isinstance(issue['pull_request'], dict) and 'url' in issue['pull_request']
    )



class IssueObject(GithubObject):
    def __init__(self, issue: dict, repo_id: int, tool_source: str, tool_version: str, data_source: str):

        dict_data = {
            'repo_id': repo_id,
            'reporter_id': None,
            'pull_request': None,
            'pull_request_id': None,
            'created_at': issue['created_at'],
            'issue_title': str(issue['title']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
                issue['title']
            ) else None,
            # 'issue_body': issue['body'].replace('0x00', '____') if issue['body'] else None,
            'issue_body': str(issue['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
                issue['body']
            ) else None,
            'comment_count': issue['comments'],
            'updated_at': issue['updated_at'],
            'closed_at': issue['closed_at'],
            'repository_url': issue['repository_url'],
            'issue_url': issue['url'],
            'labels_url': issue['labels_url'],
            'comments_url': issue['comments_url'],
            'events_url': issue['events_url'],
            'html_url': issue['html_url'],
            'issue_state': issue['state'],
            'issue_node_id': issue['node_id'],
            'gh_issue_id': issue['id'],
            'gh_issue_number': issue['number'],
            'gh_user_id': issue['user']['id'],
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source
        }

        super().__init__(dict_data)



start("chaoss", "augur")
# start("grafana", "oncall")



