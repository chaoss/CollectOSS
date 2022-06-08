from celery import Celery
import redis
from github_paginator import GithubPaginator
import ..worker_base import TaskSession
import json
from celery.utils.log import get_task_logger



BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL)

r = redis.from_url('redis://localhost:6379/1', decode_responses=True)
# r.set('mykey', 'thevalueofmykey')
# print(r.get('mykey'))
# r.delete('mykey')
# print(r.get('mykey'))


config_path = '../../augur.config.json'

with open(config_path, 'r') as f:
    config = json.load(f)

logger = get_task_logger(__name__)

session = TaskSession(logger, config)

print(session.config)

@app.task
def repo_info(owner, repo):
    print(f"Collecting repo info for {owner}/{repo}")


@app.task
def pull_requests(owner, repo):
    print(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&"
    "direction=desc"

    prs = GithubPaginator(url, config_path)

    repo_pr_labels = []
    repo_pr_assignees = []
    repo_pr_reviewers = []
    repo_pr_meta_data = []
    repo_pr_numbers = []

    for pr in prs:

        repo_pr_labels += pr["labels"]
        repo_pr_assignees += pr["assignees"]
        repo_pr_reviewers += pr["requested_reviewers"]
        repo_pr_numbers.append(pr["number"])
        repo_pr_meta_data += [pr['head'], pr['base']]

    pull_request_comments(owner, repo)
    pull_request_events(owner, repo)

    pull_request_meta(owner, repo, repo_pr_meta_data)
    pull_request_reviews(owner, repo, repo_pr_numbers)
    pull_request_labels(owner, repo, repo_pr_labels)
    pull_request_assignees(owner, repo, repo_pr_assignees)

    
@app.task
def pull_request_comments(owner, repo):
    print(f"Collecting pull request comments for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/comments"

    pr_comments = GithubPaginator(url, config_path)

    for comment in pr_comments:
        print(comment["url"])


@app.task
def pull_request_events(owner, repo):
    print(f"Collecting pull request events for {owner}/{repo}")
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"
    
    pr_events = GithubPaginator(url, config_path)

    for event in pr_events:
        print(event['url'])
    

# test with pr_id 1793 which has one review
@app.task
def pull_request_reviews(owner, repo, pr_number):
    print(f"Collecting pull request reviews for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

    reviews = GithubPaginator(url, config_path)

    for review in reviews:
        print(review["id"])


@app.task
def pull_request_labels(owner, repo, labels):
    print(f"Handling pull request labels for {owner}/{repo}")


@app.task
def pull_request_assignees(owner, repo, assignees):
    print(f"Handling pull request labels for {owner}/{repo}")


@app.task
def pull_request_reviewers(owner, repo, reviewers):
    print(f"Handling reviewers for {owner}/{repo}")


@app.task
def pull_request_meta(owner, repo, meta_data):
    print(f"Handling reviewers for {owner}/{repo}")

    for data in meta_data:
        print(data)


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


# pull_requests("chaoss", "augur")



