import re
import logging

import sqlalchemy as s

from augur.tasks.github.util.github_paginator import hit_api
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Repo


logger = logging.getLogger(__name__)


REPO_ENDPOINT = "https://api.github.com/repos/{}/{}"


class RepoLoadController:

    def __init__(self, gh_session):
        self.session = gh_session


    def is_valid_repo(self, url):

        result = re.search(r"https:\/\/github\.com\/(.+)\/(.+)$", url)

        if not result:
            return False

        capturing_groups = result.groups()

        owner = capturing_groups[0]
        repo = capturing_groups[1]

        if not owner or not repo:
            return False

        url = REPO_ENDPOINT.format(owner, repo)

        attempts = 0
        while attempts < 10:
            result = hit_api(self.session.oauths, url, logger)

            if not result:
                attempts+=1
                continue

            if "message" in result.json().keys():
                return False
            
            return True


    def get_repo_id(self, url):

        query = s.sql.text(f"""SELECT * FROM augur_data.repo WHERE repo_git='{url}' AND repo_group_id=-1;""")

        result = self.session.execute_sql(query).fetchall()

        if len(result) == 0:
            return None

        else:
            return dict(result[0])["repo_id"]

        # query repo table for repo
        # if repo exists return the repo_id
        # else add repo_row and return the repo_id

        return None

    def add_repo_row(self, url):

        repo_group_id = -1

        # insert the repo into the table
        insertSQL = s.sql.text(
            f"""
                INSERT INTO augur_data.repo(repo_group_id, repo_git, repo_status,
                tool_source, tool_version, data_source, data_collection_date)
                VALUES ({repo_group_id}, '{url}', 'New', 'CLI', 1.0, 'Git', CURRENT_TIMESTAMP)
            """
        )

        self.session.execute_sql(insertSQL)


    def add_repo_to_user(self, user_id, repo_id):

        pass

    def add_repos(self, url_list):

        for url in url_list:

            if self.is_valid_repo(url):

                repo_id = self.get_repo_id(url)

                if not repo_id:
                    repo_id = self.add_repo_row(url)

                self.add_repo_to_user(repo_id)











