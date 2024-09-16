import logging
import re
import sqlalchemy as s

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.github.util.github_graphql_data_access import GithubGraphQlDataAccess
from augur.application.db.lib import get_group_by_name, get_repo_group_by_name, get_repo_by_repo_git, get_repo_by_src_id
from augur.tasks.github.util.util import get_owner_repo
from augur.application.db.models.augur_operations import retrieve_owner_repos, FRONTEND_REPO_GROUP_NAME, RepoGroup, UserGroup

from augur.application.db.models import UserRepo, Repo, User

def parse_org_name(string):

    match = re.match(r'^\/?([a-zA-Z0-9_-]+)\/?$', string)
    return match

def parse_org_and_repo_name(string):

    match = re.match(r'^\/?([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)\/?$', string)
    return match

# TODO: Add support for gitlab
@celery.task
def add_orgs_and_repos(user_id, group_name, orgs, repo_urls):

    logger = logging.getLogger(add_orgs_and_repos.__name__)

    with GithubTaskSession(logger) as session:
     
        # determine group id from name
        group = get_group_by_name(user_id, group_name)
        if not group:
            logger.error(f"Error while adding repo. Invalid group name of {group_name}. Cannot insert repos")
            return
        
        group_id = group.group_id

        # get frontend repo group
        frontend_repo_group = RepoGroup.get_by_name(session, FRONTEND_REPO_GROUP_NAME)
        if not frontend_repo_group:
            logger.error("Error while adding repo: Could not find frontend repo group so repos cannot be inserted")
            return

        repo_group_id = frontend_repo_group.repo_group_id


        # define repo_data and assoicate repos with frontend repo group
        repo_data = [(url, repo_group_id) for url in repo_urls]

        for org in orgs:

            # create repo group for org if it doesn't exist
            repo_group = RepoGroup.get_by_name(session, org)
            if not repo_group:
                repo_group = create_repo_group(session, org)

            # retrieve repo urls for org
            org_repos, _ = retrieve_owner_repos(session, org)
            if not org_repos:
                continue

            # define urls and repo_group_id of org and then add to repo_data
            org_repo_data = [(url, repo_group.repo_group_id) for url in org_repos]
            repo_data.extend(org_repo_data)


        # get data for repos to determine type, src id, and if they exist
        data = get_repos_data(repo_data, session, logger)

        for url, repo_group_id in repo_data:

            repo_data = data[url]
            if not repo_data:
                # skip since cause the repo is not valid (doesn't exist likely)
                continue

            repo_src_id = repo_data["databaseId"]
            repo_type = repo_data["owner"]["__typename"]

            repo = get_repo_by_src_id(repo_src_id)
            if repo:
                # TODO: add logic to update the existing records repo_group_id if it isn't equal to the existing record
                add_existing_repo_to_group(logger, session, user_id, group_name, repo.repo_id)
                continue     

            repo = get_repo_by_repo_git(session, url)
            if repo:
                # TODO: add logic to update the existing records repo_group_id if it isn't equal to the existing record
                add_existing_repo_to_group(logger, session, user_id, group_name, repo.repo_id)
                continue

            add_repo(logger, session, url, repo_group_id, group_id, repo_type, repo_src_id)

        return 


# TODO: Make it only get like 100 at a time
def get_repos_data(repo_data, session, logger):

    repo_urls = [x[0] for x in repo_data]

    github_graphql_data_access = GithubGraphQlDataAccess(session.oauths, logger, ingore_not_found_error=True)
    
    query_parts = []
    repo_map = {}
    for i, url in enumerate(repo_urls):
        owner, repo = get_owner_repo(url)
        query_parts.append(f"""repo_{i}: repository(owner: "{owner}", name: "{repo}") {{ 
                                databaseId, owner {{ __typename }} 
                        }}""")
        repo_map[url] = f"repo_{i}"
    
    query = f"query GetRepoIds {{    {'    '.join(query_parts)}}}"

    data = github_graphql_data_access.get_resource(query, {}, [])

    result_data = {}
    for url in repo_urls:
        key =repo_map[url]
        repo_data = data[key]

        result_data[url] = repo_data
    
    return result_data

def get_repo_by_repo_git(session, url):

    return session.query(Repo).filter(Repo.repo_git == url).first()


def add_existing_repo_to_group(logger, session, user_id, group_name, repo_id):

    logger.info("Adding existing repo to group")

    group_id = UserGroup.convert_group_name_to_id(session, user_id, group_name)
    if group_id is None:
        return False
    
    result = UserRepo.insert(session, repo_id, group_id)
    if not result:
        return False
    
def create_repo_group(session, owner):

    repo_group = RepoGroup(rg_name=owner.lower(), rg_description="", rg_website="", rg_recache=0, rg_type="Unknown",
            tool_source="Loaded by user", tool_version="1.0", data_source="Git")
    session.add(repo_group)
    session.commit()

    return repo_group

def add_repo(logger, session, url, repo_group_id, group_id, repo_type, repo_src_id):

    # These two things really need to be done in one commit in the future to prevent one existing without the other
    repo_id = Repo.insert_github_repo(session, url, repo_group_id, "Frontend", repo_type, repo_src_id)
    if not repo_id:
        logger.error("Error while adding repo: Failed to insert github repo")
        return

    result = UserRepo.insert(session, repo_id, group_id)
    if not result:
        logger.error(f"Error while adding repo: Failed to insert user repo record. A record with a repo_id of {repo_id} and a group id of {group_id} needs to be added to the user repo table so that this repo shows up in the users group")
        return

# @celery.task
# def add_org_repo_list(user_id, group_name, urls):

#     logger = logging.getLogger(add_org_repo_list.__name__)

#     with GithubTaskSession(logger) as session:
     
#         user = User.get_by_id(session, user_id)

#     invalid_urls = []
#     valid_orgs = []
#     valid_repos = []
#     for url in urls:

#         # matches https://github.com/{org}/ or http://github.com/{org}
#         if Repo.parse_github_org_url(url):
#             added = user.add_github_org(group_name, url)[0]
#             if added:
#                 valid_orgs.append(url)

#         # matches https://github.com/{org}/{repo}/ or http://github.com/{org}/{repo}
#         elif Repo.parse_github_repo_url(url)[0]:
#             added = user.add_github_repo(group_name, url)[0]
#             if added:
#                 valid_repos.append(url)

#         # matches /{org}/{repo}/ or /{org}/{repo} or {org}/{repo}/ or {org}/{repo}
#         elif (match := parse_org_and_repo_name(url)):
#             org, repo = match.groups()
#             repo_url = f"https://github.com/{org}/{repo}/"
#             added = user.add_github_repo(group_name, repo_url)[0]
#             if added:
#                 valid_repos.append(url)

#         # matches /{org}/ or /{org} or {org}/ or {org}
#         elif (match := parse_org_name(url)):
#             org = match.group(1)
#             org_url = f"https://github.com/{org}/"
#             added = user.add_github_org(group_name, org_url)[0]
#             if added:
#                 valid_orgs.append(url)

#         # matches https://gitlab.com/{org}/{repo}/ or http://gitlab.com/{org}/{repo}
#         elif Repo.parse_gitlab_repo_url(url)[0]:

#             added = user.add_gitlab_repo(group_name, url)[0]
#             if added:
#                 valid_repos.append(url)

#         else:
#             invalid_urls.append(url)

#     return valid_orgs, valid_repos, invalid_urls


    


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












