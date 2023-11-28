import logging
import re

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.application.db.models import UserRepo, Repo, User

def parse_org_name(string):

    match = re.match(r'^\/?([a-zA-Z0-9_-]+)\/?$', string)
    return match

def parse_org_and_repo_name(string):

    match = re.match(r'^\/?([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)\/?$', string)
    return match


@celery.task
def add_org_repo_list(user_id, group_name, urls):

    logger = logging.getLogger(add_org_repo_list.__name__)

    with GithubTaskSession(logger) as session:
     
        user = User.get_by_id(session, user_id)

    invalid_urls = []
    valid_orgs = []
    valid_repos = []
    for url in urls:

        # matches https://github.com/{org}/ or http://github.com/{org}
        if Repo.parse_github_org_url(url):
            added = user.add_github_org(group_name, url)[0]
            if added:
                valid_orgs.append(url)

        # matches https://github.com/{org}/{repo}/ or http://github.com/{org}/{repo}
        elif Repo.parse_github_repo_url(url)[0]:
            added = user.add_github_repo(group_name, url)[0]
            if added:
                valid_repos.append(url)

        # matches /{org}/{repo}/ or /{org}/{repo} or {org}/{repo}/ or {org}/{repo}
        elif (match := parse_org_and_repo_name(url)):
            org, repo = match.groups()
            repo_url = f"https://github.com/{org}/{repo}/"
            added = user.add_github_repo(group_name, repo_url)[0]
            if added:
                valid_repos.append(url)

        # matches /{org}/ or /{org} or {org}/ or {org}
        elif (match := parse_org_name(url)):
            org = match.group(1)
            org_url = f"https://github.com/{org}/"
            added = user.add_github_org(group_name, org_url)[0]
            if added:
                valid_orgs.append(url)

        # matches https://gitlab.com/{org}/{repo}/ or http://gitlab.com/{org}/{repo}
        elif Repo.parse_gitlab_repo_url(url)[0]:

            added = user.add_gitlab_repo(group_name, url)[0]
            if added:
                valid_repos.append(url)

        else:
            invalid_urls.append(url)

    return valid_orgs, valid_repos, invalid_urls


    


# TODO: Change to github specific
@celery.task
def add_repo(user_id, group_name, repo_url):

    logger = logging.getLogger(add_org.__name__) 

    with GithubTaskSession(logger) as session:
        result = UserRepo.add_github_repo(session, repo_url, user_id, group_name)

    print(repo_url, result)


# TODO: Change to github specific
@celery.task
def add_org(user_id, group_name, org_url):

    logger = logging.getLogger(add_org.__name__) 

    with GithubTaskSession(logger) as session:
            result = UserRepo.add_github_org_repos(session, org_url, user_id, group_name)

    print(org_url, result)
