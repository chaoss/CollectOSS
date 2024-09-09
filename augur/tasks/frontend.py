import logging
import re
import sqlalchemy as s

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.util.github_graphql_data_access import GithubGraphQlDataAccess
from augur.application.db.lib import get_group_by_name, get_repo_group_by_name, get_repo_by_repo_git, get_repo_by_src_id
from augur.tasks.github.util.util import get_owner_repo
from augur.application.db.models.augur_operations import retrieve_owner_repos, FRONTEND_REPO_GROUP_NAME

from augur.application.db.models import UserRepo, Repo, User

def parse_org_name(string):

    match = re.match(r'^\/?([a-zA-Z0-9_-]+)\/?$', string)
    return match

def parse_org_and_repo_name(string):

    match = re.match(r'^\/?([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)\/?$', string)
    return match

@celery.task
def add_orgs_and_repos(user_id, group_name, org_urls, repo_urls):

    logger = logging.getLogger(add_org_repo_list.__name__)

    with GithubTaskSession(logger) as session:
     
        user = User.get_by_id(session, user_id)

        group = get_group_by_name(session, user_id, group_name)
        if not group:
            return False, {"status": "Invalid group name"}
        
        group_id = group.group_id

        for url in org_urls:
            org_repos, _ = retrieve_owner_repos(url)
            if not org_repos:
                continue

            repo_urls.extend(org_repos)


        data = get_repos_data(repo_urls, session, logger)

        for url in repo_urls:

            repo_data = data[url]
            if not repo_data:
                # skip since the repo doesn't exists
                continue

            repo_type = repo_data["databaseId"]
            repo_src_id = repo_data["owner"]["__typename"]

            try:
                repo = get_repo_by_repo_git(url)
            except s.orm.exc.NoResultFound:
                # log a warning 
                continue

            repo = get_repo_by_src_id(repo_src_id)
            if repo:
                #    log a warning
                continue        

            frontend_repo_group = get_repo_group_by_name(FRONTEND_REPO_GROUP_NAME)
            if not frontend_repo_group:
                return False, {"status": "Could not find repo group with name 'Frontend Repos'", "repo_url": url}

            repo_group_id = frontend_repo_group.repo_group_id


            # These two things really need to be done in one commit
            repo_id = Repo.insert_github_repo(session, url, repo_group_id, "Frontend", repo_type)
            if not repo_id:
                #    log a warning
                continue

            result = UserRepo.insert(session, repo_id, group_id)
            if not result:
                #    log a warning
                continue


        # repo_id = Repo.insert_github_repo(session, url, repo_group_id, "Frontend", repo_type)
        # if not repo_id:
        #     return False, {"status": "Repo insertion failed", "repo_url": url}

        # result = UserRepo.insert(session, repo_id, group_id)
        # if not result:
        #     return False, {"status": "repo_user insertion failed", "repo_url": url}

        #collection_status records are now only added during collection -IM 5/1/23
        #status = CollectionStatus.insert(session, repo_id)
        #if not status:
        #    return False, {"status": "Failed to create status for repo", "repo_url": url}

        return True, {"status": "Repo Added", "repo_url": url}

@celery.task
def add_org():

    pass    


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
# @celery.task
# def add_repo(user_id, group_name, repo_url):

#     logger = logging.getLogger(add_org.__name__) 

#     with GithubTaskSession(logger) as session:
#         result = UserRepo.add_github_repo(session, repo_url, user_id, group_name)

#     print(repo_url, result)


# # TODO: Change to github specific
# @celery.task
# def add_org(user_id, group_name, org_url):

#     logger = logging.getLogger(add_org.__name__) 

#     with GithubTaskSession(logger) as session:
#             result = UserRepo.add_github_org_repos(session, org_url, user_id, group_name)

#     print(org_url, result)











def get_repos_data(repo_urls, session, logger):

    github_graphql_data_access = GithubGraphQlDataAccess(session.oauths, logger, ingore_not_found_error=True)
    
    query_parts = []
    repo_map = {}
    for i, url in enumerate(repo_urls):
        owner, repo = get_owner_repo(url)
        query_parts.append(f"""{i}: repository(owner: "{owner}", name: "{repo}") {{ 
                                databaseId, owner {{ __typename }} 
                        }}""")
        repo_map[url] = i
    
    query = f"query GetRepoIds {{    {'    '.join(query_parts)}}}"

    data = github_graphql_data_access.get_resource(query, {}, [])

    result_data = {}
    for url in repo_urls:
        key =repo_map[url]
        repo_data = data[key]

        result_data[url] = repo_data
    
    return result_data

