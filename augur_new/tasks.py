import logging
import json
import redis
from celery import Celery, group
from celery.utils.log import get_task_logger
import time

from db_models import PullRequests, Message, PullRequestReviews, PullRequestLabels, PullRequestReviewers, PullRequestEvents, PullRequestMeta


from github_paginator import GithubPaginator
from worker_base import TaskSession


BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL)

r = redis.from_url('redis://localhost:6379/1', decode_responses=True)
r.set('mykey', 'thevalueofmykey')
r.delete('mykey')

config_path = '../augur.config.json'

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

    # returns an iterable of all prs at this url
    prs = GithubPaginator(url, session.oauths)

    repo_pr_labels = []
    repo_pr_assignees = []
    repo_pr_reviewers = []
    repo_pr_meta_data = []
    repo_pr_numbers = []
    pr_object_list = []

    for pr in prs:

        # get labels, assigness, and reviewers to pass to their respective tasks  
        repo_pr_labels += pr["labels"]
        repo_pr_assignees += pr["assignees"]
        repo_pr_reviewers += pr["requested_reviewers"]

        # get a list of pr numbers to pass for the pr reviews task
        repo_pr_numbers.append(pr["number"])

        # add pr_head_or_base to be able to differentiate between the two in the pr_meta task
        pr['head'].update(
            {'pr_head_or_base': 'head'}
        )
        pr['base'].update(
            {'pr_head_or_base': 'base'}
        )
        repo_pr_meta_data += [pr['head'], pr['base']]

        # get needed data for prs and add to list
        pr_object = create_pull_request_object(pr, repo_id, tool_source, tool_version)
        pr_object_list.append(pr_object)

 
    task_list = []

    task_list.append(pull_request_comments.s(owner, repo))
    task_list.append(pull_request_events.s(owner, repo))
    task_list.append(pull_request_reviews.s(owner, repo, repo_pr_numbers))
    task_list.append(pull_request_labels.s(owner, repo, repo_pr_labels))
    task_list.append(pull_request_assignees.s(owner, repo, repo_pr_assignees))
    task_list.append(pull_request_reviewers.s(owner, repo, repo_pr_reviewers))
    task_list.append(pull_request_meta.s(owner, repo, repo_pr_meta_data))

    pr_task_group = group(task_list)

    # executes all the tasks in the group in parallel
    pr_task_group()

    # insert prs into db or cache

# func to get the data we need for prs
# added to separate func so it doesn't clutter the pr task
def create_pull_request_object(pr, repo_id, tool_source, tool_version):

    # in the table 2 times
        # pr['comments_url'] 
        # pr['commits_url'] 
        # pr['issue_url'] 
        # pr['review_comments_url'] 
        # pr['statuses_url'] 


    # add pr["head"]["sha"]

    return PullRequests(
        repo_id=repo_id,
        pr_url=pr['url'],
        pr_src_id=int(str(pr['id']).encode(
            encoding='UTF-8').decode(encoding='UTF-8')),
        pr_src_node_id=pr['node_id'],
        pr_html_url=pr['html_url'], # derivable
        pr_diff_url=pr['diff_url'],  # derivable
        pr_patch_url=pr['patch_url'],  # derivable
        pr_issue_url=pr['issue_url'],  # derivable
        pr_augur_issue_id=None, # always none why keep?
        pr_src_number=pr['number'],
        pr_src_state=pr['state'],
        pr_src_locked=pr['locked'],
        pr_src_title=str(pr['title']),
        pr_augur_contributor_id=None,
        pr_body=str(pr['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
            pr['body']
        ) else None,
        pr_created_at=pr['created_at'],
        pr_updated_at=pr['updated_at'],
        pr_closed_at=None if not (
            pr['closed_at']
        ) else pr['closed_at'],
        pr_merged_at=None if not (
            pr['merged_at']
        ) else pr['merged_at'],
        pr_merge_commit_sha=pr['merge_commit_sha'],
        pr_teams=None,  # always none why keep?
        pr_milestone=None,  # always none why keep?
        pr_commits_url=pr['commits_url'],  # derivable
        pr_review_comments_url=pr['review_comments_url'],  # derivable
        pr_review_comment_url=pr['review_comment_url'],  # derivable
        pr_comments_url=pr['comments_url'],# derivable with addition of pr["head"]["sha"]
        pr_statuses_url=pr['statuses_url'],
        pr_meta_head_id=None if not ( # accessible in the pr_meta table
            pr['head']
        ) else pr['head']['label'],
        pr_meta_base_id=None if not (  # accessible in the pr_meta table
            pr['base']
        ) else pr['base']['label'],
        pr_src_issue_url=pr['issue_url'], # derivable
        pr_src_comments_url=pr['comments_url'], # derivable
        pr_src_review_comments_url=pr['review_comments_url'], # derivable
        pr_src_commits_url=pr['commits_url'], # derivable with addition of pr["head"]["sha"]
        pr_src_statuses_url=pr['statuses_url'],
        pr_src_author_association=pr['author_association'],
        tool_source=tool_source,
        tool_version=tool_version,
        data_source='GitHub API'
    )
    
@app.task
def pull_request_comments(owner, repo):
    print(f"Collecting pull request comments for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/comments"

    pr_comments = GithubPaginator(url, session.oauths)

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"
    

    pr_comment_objects = []

    for comment in pr_comments:
        pr_comment_objects.append(
            create_pr_comment_object(comment, platform_id, repo_id, 
                    tool_source, tool_version, data_source)
            )

    # insert pr comments into database or cache

def create_pr_comment_object(comment, platform_id, repo_id, tool_source, tool_version, data_source):

    return Message(
            pltfrm_id = platform_id,
            msg_text = str(comment['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
                comment['body']
            ) else None,
            msg_timestamp = comment['created_at'],
            cntrb_id = None,
            tool_source = tool_source,
            tool_version = tool_version,
            data_source = data_source,
            repo_id = repo_id,
            platform_msg_id = int(comment['id']),
            platform_node_id = comment['node_id']
    )


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

    pr_event_objects = []

    for event in pr_events:
        pr_event_objects.append(
            create_pr_comment_object(event, platform_id, repo_id,
                                     tool_source, tool_version, data_source)
        )

    # insert pr events into database or cache
    

def create_pr_event_object(event, platform_id, repo_id, tool_source, tool_version, data_source):

    # TODO: Add db pull request id

    return PullRequestEvents(
        # pull_request_id=event['pull_request_id'],
        cntrb_id=None,
        action=event['event'],
        action_commit_hash=None,
        created_at=event['created_at'],
        issue_event_src_id=int(event['issue.id']),
        node_id=event['node_id'],
        node_url=event['url'],
        tool_source=tool_source,
        tool_version=tool_version,
        data_source=data_source,
        pr_platform_event_id=int(event['issue.id']),
        platform_id=platform_id,
        repo_id=repo_id
    )

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
        cntrb_id=review['cntrb_id'],
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


@app.task
def pull_request_labels(owner, repo, labels):
    print(f"Handling pull request labels for {owner}/{repo}")
    
    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"

    pr_label_objects = []

    for label in labels:
        pr_label_objects.append(
            create_pr_label_object(label, platform_id, repo_id,
                                     tool_source, tool_version, data_source)
        )


def create_pr_label_object(label, platform_id, repo_id, tool_source, tool_version, data_source):

    # TODO: Add db pull request id

    return PullRequestReviews(
        #pull_request_id=label['pull_request_id'],
        pr_src_id=int(label['id']),
        pr_src_node_id=label['node_id'],
        pr_src_url=label['url'],
        pr_src_description=label['name'],
        pr_src_color=label['color'],
        pr_src_default_bool=label['default'],
        tool_source=tool_source,
        tool_version=tool_version,
        data_source=data_source,
        repo_id=repo_id
    )


@app.task
def pull_request_assignees(owner, repo, assignees):
    print(f"Handling pull request labels for {owner}/{repo}")

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr assignee task"
    tool_version = "2.0"
    data_source = "Github API"

    pr_assinee_objects = []

    for assignee in assignees:
        pr_assinee_objects.append(
            create_pr_assignee_object(assignee, platform_id, repo_id,
                                   tool_source, tool_version, data_source)
        )


def create_pr_assignee_object(assignee, platform_id, repo_id, tool_source, tool_version, data_source):

    # TODO: Add db pull request id

    return PullRequestReviews(
        #pull_request_id=assignee['pull_request_id'],
        contrib_id=assignee['cntrb_id'],
        pr_assignee_src_id=int(assignee['id']),
        tool_source=tool_source,
        tool_version=tool_version,
        data_source=data_source,
        repo_id=repo_id
    )  


@app.task
def pull_request_reviewers(owner, repo, reviewers):
    print(f"Handling reviewers for {owner}/{repo}")

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr reviewer task"
    tool_version = "2.0"
    data_source = "Github API"

    pr_reviewer_objects = []

    for reviewer in reviewers:
        pr_reviewer_objects.append(
            create_pr_reviewer_object(reviewer, platform_id, repo_id,
                                      tool_source, tool_version, data_source)
        )


def create_pr_reviewer_object(reviewer, platform_id, repo_id, tool_source, tool_version, data_source):

    # TODO: Add db pull request id

    return PullRequestReviewers(
        #pull_request_id=reviewer['pull_request_id'],
        cntrb_id=None,
        pr_reviewer_src_id=int(float(reviewer['id'])),
        tool_source=tool_source,
        tool_version=tool_version,
        data_source=data_source,
        repo_id=repo_id
    )

@app.task
def pull_request_meta(owner, repo, metadata):
    print(f"Handling metadata for {owner}/{repo}")

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr metadata task"
    tool_version = "2.0"
    data_source = "Github API"

    pr_metadata_objects = []

    for data in metadata:
        pr_metadata_objects.append(
            create_pr_meta_object(data, platform_id, repo_id,
                                      tool_source, tool_version, data_source)
        )


def create_pr_meta_object(meta, platform_id, repo_id, tool_source, tool_version, data_source):

    # TODO: Add db pull request id

    return PullRequestMeta(
        #pull_request_id=meta['pull_request_id'],
        pr_head_or_base=meta['pr_head_or_base'],
        pr_src_meta_label=meta['label'],
        pr_src_meta_ref=meta['ref'],
        pr_sha=meta['sha'],
        # Cast as int for the `nan` user by SPG on 11/28/2021; removed 12/6/2021
        cntrb_id=meta['cntrb_id'],
        tool_source=tool_source,
        tool_version=tool_version,
        data_source=data_source,
        repo_id=repo_id
    )


@app.task
def issues():
    pass


@app.task
def issue_comments():
    pass


@app.task
def issue_events():
    pass


@app.task
def issue_labels():
    pass


@app.task
def issue_assignees():
    pass


pull_requests("chaoss", "augur")



