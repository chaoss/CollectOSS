import logging
import json
import redis
from celery import group
from celery.utils.log import get_task_logger
import time
import traceback

from .main import app
# from .pr_object import PrObject

from .db_models import PullRequests, Message, PullRequestReviews, PullRequestLabels, PullRequestReviewers, PullRequestEvents, PullRequestMeta, PullRequestAssignees, PullRequestMessageRef


from .github_paginator import GithubPaginator
from .worker_base import TaskSession


r = redis.from_url('redis://localhost:6379/2', decode_responses=True)


config_path = '../augur/augur.config.json'

with open(config_path, 'r') as f:
    config = json.load(f)

logger = get_task_logger(__name__)

# creates a class that is sub class of the sqlalchemy.orm.Session class that additional methods and fields added to it. 
session = TaskSession(logger, config)

@app.task
def repo_info(owner, repo):
    print(f"Collecting repo info for {owner}/{repo}")


@app.task
def pull_requests(owner, repo):
    print(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&"
    "direction=desc"

    # get repo_id or have it passed
    repo_id = 1
    tool_source = "Pr Task"
    tool_version = "2.0"
    platform_id = 25150
    data_source = "Github API"

    pr_natural_keys = ["pr_url"]

    print("About to collect pages")

    labels = [
        {
            "id": 2573284717,
            "node_id": "MDU6TGFiZWwyNTczMjg0NzE3",
            "url": "https://api.github.com/repos/chaoss/augur/labels/dependencies",
            "name": "dependencies",
            "color": "0366d6",
            "default": False,
            "description": "Pull requests that update a dependency file"
        },
        {
            "id": 2573284724,
            "node_id": "MDU6TGFiZWwyNTczMjg0NzI0",
            "url": "https://api.github.com/repos/chaoss/augur/labels/javascript",
            "name": "javascript",
            "color": "168700",
            "default": False,
            "description": "Pull requests that update Javascript code"
        }
    ]

    # session.insert_data(labels, PullRequests, pr_natural_keys)


    # returns an iterable of all prs at this url
    prs = GithubPaginator(url, session.oauths)

    # print(f"Pages collected: length: {len(prs)}")

    pr_label_dicts = []
    pr_assignee_dicts = []
    pr_reviewer_dicts = []
    pr_metadata_dicts = []

    repo_pr_numbers = []

    # creating a list, because we would like to bulk insert in the future

    len_prs = len(prs)
    for index, pr in enumerate(prs):

        pr['head'].update(
            {'pr_head_or_base': 'head'}
        )
        pr['base'].update(
            {'pr_head_or_base': 'base'}
        )

        print(f"Inserting pr {index + 1} of {len_prs}")
        pr_object = PrObject(pr, repo_id, tool_source,
                             tool_version)

        # when the object gets inserted the db_row is added to the object which is a PullRequests orm object (so it contains all the column values)
        session.insert_data([pr_object], PullRequests, pr_natural_keys)

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


    print(f"\nInserting pr labels of length: {len(pr_label_dicts)}")
    pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
    session.insert_data(pr_label_dicts, PullRequestLabels, pr_label_natural_keys)
  

    print(f"\nInserting pr assignees of length: {len(pr_assignee_dicts)}")
    pr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
    session.insert_data(pr_assignee_dicts, PullRequestAssignees, pr_assignee_natural_keys)
 

    print(f"\nInserting pr reviewers of length: {len(pr_reviewer_dicts)}")
    pr_reviewer_natural_keys = ["pr_reviewer_src_id", "pull_request_id"]
    session.insert_data(pr_reviewer_dicts, PullRequestReviewers, pr_reviewer_natural_keys)
    
    print(f"\nInserting pr metadata of length: {len(pr_metadata_dicts)}")
    pr_metadata_natural_keys = ['pull_request_id', 'pr_sha', 'pr_head_or_base']
    session.insert_data(pr_metadata_dicts, PullRequestMeta, pr_metadata_natural_keys)




            
    print("Prepping to start pr comments, pr events, and pr reviews")
    # task_list = []
    # task_list.append(pull_request_review_comments.s(owner, repo))
    # task_list.append(pull_request_events.s(owner, repo))
    # task_list.append(pull_request_reviews.s(owner, repo, repo_pr_numbers))

    # pr_task_group = group(task_list)

    # executes all the tasks in the group in parallel
    print("Starting pr comments, pr events, and pr reviews")
    # pr_task_group()


def extract_needed_pr_label_data(labels, pr_id, platform_id, repo_id, tool_source, tool_version, data_source):

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


def extract_needed_pr_assignee_data(assignees, pr_id, platform_id, repo_id, tool_source, tool_version, data_source):

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


def extract_needed_pr_reviewer_data(reviewers, pr_id, platform_id, repo_id, tool_source, tool_version, data_source):

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


def extract_needed_pr_metadata(metadata_list, pr_id, platform_id, repo_id, tool_source, tool_version, data_source):

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



@app.task
def pull_request_review_comments(owner, repo):
    print(f"Collecting pull request comments for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/comments"

    pr_comments = GithubPaginator(url, session.oauths)

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"
    pr_comment_natural_keys = []
    pr_comment_ref_natural_keys = []

    pr_comment_ref_dicts = []

    pr_comment_len = len(pr_comments)

    for index, comment in enumerate(pr_comments):

        # pr url associated with this comment
        comment_pr_url = comment["pull_request_url"]

        related_pr = PullRequests.query.filter_by(PullRequests.pr_url == comment_pr_url).one()

        if not related_pr:
            print(
                f"Error can't find pr for pr comment with id: {comment['id']}")
            continue

        pr_id = related_pr.pull_request_id

        pr_comment_object = PrCommentObject(comment, platform_id, repo_id, tool_source, tool_version, data_source)

        print(f"Inserting pr review comment {index + 1} of {len(pr_comment_len)}")
        session.insert_data([pr_comment_object], Message, pr_comment_natural_keys)

        msg_id = pr_comment_object.db_row.msg_id

        pr_comment_ref_dicts.append(
            extract_pr_comment_ref_data(comment, pr_id, msg_id, repo_id, tool_source, tool_version, data_source)
        )

    print(f"Insert pr comment refs")
    session.insert_data(pr_comment_ref_dicts, PullRequestMessageRef, pr_comment_ref_natural_keys)


def extract_pr_comment_ref_data(comment, pr_id, msg_id, repo_id, tool_source, tool_version, data_source):

    pr_comment_msg_ref = {
        'pull_request_id': comment['pull_request_id'],
        # to cast, or not to cast. That is the question. 12/6/2021
        'msg_id': comment['msg_id'],
        'pr_message_ref_src_comment_id': int(comment['id']),
        'pr_message_ref_src_node_id': comment['node_id'],
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': data_source,
        'repo_id': repo_id
    }

    return pr_comment_msg_ref

@app.task
def pull_request_events(owner, repo):
    print(f"Collecting pull request events for {owner}/{repo}")
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"
    
    pr_events = GithubPaginator(url, session.oauths)

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"
    # TODO: Add natural keys
    pr_event_natural_keys = []

    pr_event_dicts = []
    for event in pr_events:

        event_pr_url = event["issues"]["pull_request"]["url"]

        related_pr = PullRequests.query.filter_by(PullRequests.pr_url == event_pr_url).one()

        if not related_pr:
            print(f"Error can't find pr for event with id: {event['url']}")
            continue


        pr_event_dicts.append(
            extract_pr_event_data(event, related_pr.pull_request_id, platform_id, repo_id,
                                        tool_source, tool_version, data_source)
        )

    print("Inserting pr events")
    session.insert_data(pr_event_dicts, PullRequestEvents, pr_event_natural_keys)

def extract_pr_event_data(event, pr_id, platform_id, repo_id, tool_source, tool_version, data_source):

    # TODO: Add db pull request id

    pr_event = {
        'pull_request_id': pr_id,
        'cntrb_id': None,
        'action': event['event'],
        'action_commit_hash': None,
        'created_at': event['created_at'],
        'issue_event_src_id': int(event['issue.id']),
        'node_id': event['node_id'],
        'node_url': event['url'],
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': data_source,
        'pr_platform_event_id': int(event['issue.id']),
        'platform_id': platform_id,
        'repo_id': repo_id
    }

    return pr_event

# do this task after others because we need to add the multi threading like we did it before
@app.task
def pull_request_reviews(owner, repo, pr_number_list):
    print(f"Collecting pull request reviews for {owner}/{repo}")

    # for pr_number in pr_number_list:

    #     url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

        # add pr review


def create_pr_review_object(review, platform_id, repo_id, tool_version, data_source):

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

    def __init__(self, data):

        self.data = data
        self.db_row = None

    def set_db_row(self, row):
        self.db_row = row

    def get_dict(self):
        return self.data


class PrObject(GithubObject):
    def __init__(self, pr, repo_id, tool_source, tool_version):

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
    def __init__(self, comment, platform_id, repo_id, tool_source, tool_version, data_source):

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

pull_requests("chaoss", "augur")



