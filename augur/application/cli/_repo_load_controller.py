import re
import logging

import sqlalchemy as s

from typing import List, Any, Dict


from augur.tasks.github.util.github_paginator import hit_api
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Repo, UserRepo


logger = logging.getLogger(__name__)


REPO_ENDPOINT = "https://api.github.com/repos/{}/{}"
ORG_REPOS_ENDPOINT = "https://api.github.com/orgs/{}/repos"
DEFAULT_REPO_GROUP_ID = 1
CLI_USER_ID = 1


class RepoLoadController:

    def __init__(self, gh_session):
        self.session = gh_session


    def is_valid_repo(self, url: str) -> bool:
        """Determine whether repo url is valid.
        
        Args:
            url: repo_url

        Returns
            True if repo url is valid and False if not
        """

        result = re.search(r"https:\/\/github\.com\/(.+)\/(.+)$", url)

        if not result:
            return False

        capturing_groups = result.groups()

        owner = capturing_groups[0]
        repo = capturing_groups[1]

        if not owner or not repo:
            return False

        if repo.endswith(".git"):
                # removes .git
            repo = repo[:-4]

        if repo.endswith("/"):
            # reomves /
            repo = repo[:-1]

        url = REPO_ENDPOINT.format(owner, repo)

        attempts = 0
        while attempts < 10:
            result = hit_api(self.session.oauths, url, logger)

            # if result is None try again
            if not result:
                attempts+=1
                continue

            # if there was an error return False
            if "message" in result.json().keys():
                return False
            
            return True


    def retrieve_org_repos(self, url: str) -> List[str]:
        """Get the repos for an org.

        Note:
            If the org url is not valid it will return []
        
        Args:
            url: org url

        Returns
            List of valid repo urls or empty list if invalid org
        """

        result = re.search(r"https:\/\/github\.com\/(.+)$", url)

        if not result:
            return False

        capturing_groups = result.groups()

        owner = capturing_groups[0]

        if not owner:
            return False

        if owner.endswith("/"):
            # reomves /
            owner = owner[:-1]

        url = ORG_REPOS_ENDPOINT.format(owner)


        attempts = 0
        while attempts < 10:
            result = hit_api(self.session.oauths, url, logger)

            # if result is None try again
            if not result:
                attempts += 1
                continue

            data = result.json()

            # if there are no repos return []
            if not data:
                return []

            repos = result.json()
            repo_urls = [repo["html_url"] for repo in repos]

            return repo_urls


    # def get_repo_id(self, url: str) -> int:
    #     """Retrieve repo id of given url from repo table

    #     Note:
    #         If a repo doesn't exist is table, None is returned

    #     Args:
    #         url: repo url

    #     Returns
    #         The repo id or None if repo doesn't exist
    #     """

    #     query = s.sql.text(f"""SELECT * FROM augur_data.repo WHERE repo_git='{url}';""")

    #     result = self.session.execute_sql(query).fetchall()

    #     if len(result) == 0:
    #         return None

    #     else:
    #         return dict(result[0])["repo_id"]

    def add_repo_row(self, url: str, repo_group_id: int, tool_source):
        """Add a repo to the repo table.

        Args:
            url: repo url
            repo_group_id: group to assign repo to
        """

        repo_data = {
            "repo_group_id": repo_group_id,
            "repo_git": url,
            "repo_status": "New",
            "tool_source": tool_source,
            "tool_version": "1.0",
            "data_source": "Git"
        }

    

        repo_unique = ["repo_git"]
        return_columns = ["repo_id"]
        result = self.session.insert_data(repo_data, Repo, repo_unique, return_columns)

        return result[0]["repo_id"]


    def add_repo_to_user(self, repo_id, user_id=1):
        """Add a repo to a user in the user_repos table.

        Args:
            repo_id: id of repo from repo table
            user_id: id of user_id from users table
        """

        repo_user_data = {
            "user_id": user_id,
            "repo_id": repo_id
        }
            
            
        repo_user_unique = ["user_id", "repo_id"]
        self.session.insert_data(repo_user_data, UserRepo, repo_user_unique)

    def add_frontend_repos(self, urls: List[str], user_id: int):
        """Add list of repos to a users repos.

        Args:
            urls: list of repo urls
            user_id: id of user_id from users table
        """

        for url in urls:

            if self.is_valid_repo(url):

                repo_id = self.add_repo_row(url, DEFAULT_REPO_GROUP_ID, "Frontend")

                self.add_repo_to_user(repo_id, user_id)


    def add_frontend_orgs(self, urls: List[str], user_id: int):
        """Add list of orgs and their repos to a users repos.

        Args:
            urls: list of org urls
            user_id: id of user_id from users table
        """

        for url in urls:

            repos = self.retrieve_org_repos(url)
            
            if repos:
                self.add_frontend_repos(repos, user_id)

    def add_cli_repos(self, url_data: Dict[str, Any]):
        """Add list of repos to specified repo_groups

        Args:
            url_data: dict with repo_group_id and repo urls
        """

        for data in url_data:

            url = data["url"]
            repo_group_id = data["repo_group_id"]

            if self.is_valid_repo(url):

                # if the repo doesn't exist it adds it
                # if the repo does exist it updates the repo_group_id
                repo_id = self.add_repo_row(url, repo_group_id, "CLI")

                self.add_repo_to_user(repo_id, CLI_USER_ID)

    def add_cli_orgs(self, org_data):
        """Add list of orgs and their repos to specified repo_groups

        Args:
            org_data: dict with repo_group_id and org urls
        """

        for data in org_data:

            url = data[0]
            repo_group_id = data[1]

            repos = self.retrieve_org_repos(url)

            if repos:

                data = [{"url": repo_url, "repo_group_id": repo_group_id} for repo_url in repos]
                self.add_cli_repos(data)


    def get_user_repo_ids(self, user_id: int) -> List[int]:
        """Retrieve a list of repos_id for the given user_id.

        Args:
            user_id: id of the user

        Returns:
            list of repo ids
        """

        user_repo_id_query = s.sql.text(f"""SELECT * FROM augur_data.user_repo WHERE user_id={user_id};""")


        result = self.session.execute_sql(user_repo_id_query).fetchall()

        if len(result) == 0:
            return []

        repo_ids = [dict(row)["repo_id"] for row in result]

        return repo_ids

