import logging
import json
import redis
from celery import Celery, group
from celery.utils.log import get_task_logger
import time


from db_models import PullRequests, Message, PullRequestReviews, PullRequestLabels, PullRequestReviewers, PullRequestEvents, PullRequestMeta, PullRequestAssignees


from github_paginator import GithubPaginator
from worker_base import TaskSession


BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL)

r = redis.from_url('redis://localhost:6379/2', decode_responses=True)
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
    platform_id = 25150
    data_source = "Github API"

    pr_natural_keys = ["pr_url"]


    # returns an iterable of all prs at this url
    prs = GithubPaginator(url, session.oauths)

    pr_label_objects = []
    pr_assignee_objects = []
    pr_reviewer_objects = []
    pr_metadata_objects = []

    repo_pr_numbers = []

    # creating a list, because we would like to bulk insert in the future

    for pr in prs:

        pr['head'].update(
            {'pr_head_or_base': 'head'}
        )
        pr['base'].update(
            {'pr_head_or_base': 'base'}
        )

        # print(f"Processing {pr["url"]}")
        pr_object = create_pull_request_object(
            pr, repo_id, tool_source, tool_version)

        print(pr_object.labels)

        # when the object gets inserted the pull_request_id is automatically added
        # session.insert_data(pr_object, PullRequests, pr_natural_keys)

        # print(pr_object.labels)

        # pr_label_objects.append(
        #     create_pr_label_objects(pr["labels"], pr_object.pull_request_id,  platform_id, repo_id,
        #                            tool_source, tool_version, data_source)
        # )

        # pr_assignee_objects.append(
        #     create_pr_assignee_objects(pr["assignees"], pr_object.pull_request_id, platform_id, repo_id,
        #                             tool_source, tool_version, data_source)
        # )

        # pr_reviewer_objects.append(
        #     create_pr_reviewer_objects(pr["requested_reviewers"], pr_object.pull_request_id, platform_id, repo_id,
        #                               tool_source, tool_version, data_source)
        # )



        # pr_metadata_objects.append(
        #     create_pr_meta_objects(pr['head'] + pr['base'], pr_object.pull_request_id, platform_id, repo_id,
        #                           tool_source, tool_version, data_source)
        # )

        # # get a list of pr numbers to pass for the pr reviews task
        # repo_pr_numbers.append(pr["number"])


    # print("Inserting pr labels")
    # session.insert_data(pr_label_objects, PullRequestLabels, pr_natural_keys)

    # print("Inserting pr assignees")
    # session.insert_data(pr_assignee_objects, PullRequestAssignees, pr_natural_keys)


    # print("Inserting pr reviewers")
    # session.insert_data(pr_reviewer_objects, PullRequestReviewers, pr_natural_keys)

    # print("Inserting pr reviewers")
    # session.insert_data(pr_metadata_objects, PullRequestMeta, pr_natural_keys)

            
    # print("Prepping to start pr comments, pr events, and pr reviews")
    # task_list = []
    # task_list.append(pull_request_comments.s(owner, repo))
    # task_list.append(pull_request_events.s(owner, repo))
    # task_list.append(pull_request_reviews.s(owner, repo, repo_pr_numbers))

    # pr_task_group = group(task_list)

    # # executes all the tasks in the group in parallel
    # print("Starting pr comments, pr events, and pr reviews")
    # pr_task_group()

    

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
        pr_issue_url=pr['issue_url'],  # derivable but needed so we can relate a pr event back to a specific pr
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
        data_source='GitHub API',
        labels = pr['labels'],
        assignees = pr['assignees'],
        metadata = [pr["head"], pr["base"]]
    )


def create_pr_label_objects(labels, pr_id, platform_id, repo_id, tool_source, tool_version, data_source):

    if len(labels) == 0:
        return []

    label_objects = []
    for label in labels:

        label_obj = PullRequestLabels(
            pull_request_id=pr_id,
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

    label_objects.append(label_obj)

    return label_objects


def create_pr_assignee_objects(assignees, pr_id, platform_id, repo_id, tool_source, tool_version, data_source):

    if len(assignees) == 0:
        return []

    assignee_objects = []
    for assignee in assignees:

        label_obj = PullRequestAssignees(
            pull_request_id=pr_id,
            contrib_id=assignee['cntrb_id'],
            pr_assignee_src_id=int(assignee['id']),
            tool_source=tool_source,
            tool_version=tool_version,
            data_source=data_source,
            repo_id=repo_id
        )

    assignee_objects.append(label_obj)

    return assignee_objects


def create_pr_reviewer_objects(reviewers, pr_id, platform_id, repo_id, tool_source, tool_version, data_source):

    if len(reviewers) == 0:
        return []

    reviewer_objects = []
    for reviewer in reviewers:

        reviewer_obj = PullRequestReviewers(
            pull_request_id=pr_id,
            cntrb_id=None,
            pr_reviewer_src_id=int(float(reviewer['id'])),
            tool_source=tool_source,
            tool_version=tool_version,
            data_source=data_source,
            repo_id=repo_id
        )

    reviewer_objects.append(reviewer_obj)

    return reviewer_objects


def create_pr_meta_objects(metadata_list, pr_id, platform_id, repo_id, tool_source, tool_version, data_source):

    if len(metadata_list) == 0:
        return []

    metadata_objects = []
    for meta in metadata_list:

        metadata_obj = PullRequestMeta(
            pull_request_id=pr_id,
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

    metadata_objects.append(metadata_obj)

    return metadata_objects



    
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

    print("Inserting pr comments")
    # session.insert_data(pr_comment_objects, PullRequestMeta, pr_natural_keys)

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

    # for event in pr_events:

    #     stmt = select(PullRequests).where(
    #         PullRequests.pr_issue_url == event["issue"]["url"]))
    #     pr_event_objects.append(
    #         create_pr_comment_object(event, platform_id, repo_id,
    #                                  tool_source, tool_version, data_source)
    #     )

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
def issues(owner, repo):
    
    url =  f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"
    


@app.task
def issue_comments():
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments"


@app.task
def issue_events():
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"


@app.task
def issue_labels():
    pass


@app.task
def issue_assignees():
    pass


def create_pull_request_label_objects(labels):


    if len(labels) == 0:
        return []

    label_objects=[]
    for label in labels:

        label_obj=IssueLabels(
            pull_request_id = pr_id,
            pr_src_id = int(label['id']),
            pr_src_node_id = label['node_id'],
            pr_src_url = label['url'],
            pr_src_description = label['name'],
            pr_src_color = label['color'],
            pr_src_default_bool = label['default'],
            tool_source = tool_source,
            tool_version = tool_version,
            data_source = data_source,
            repo_id = repo_id
        )

    label_objects.append(label_obj)

    return label_objects

    {
        'issue_id': issue_id,
        'label_text': label['name'],
        'label_description': label['description'] if 'description' in label else None,
        'label_color': label['color'],
        'tool_source': self.tool_source,
        'tool_version': self.tool_version,
        'data_source': self.data_source,
        'label_src_id': int(label['id']),
        'label_src_node_id': label['node_id'],
        'repo_id': self.repo_id
    }

pull_requests("chaoss", "augur")



