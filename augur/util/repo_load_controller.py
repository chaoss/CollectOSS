import re
import logging

import sqlalchemy as s
import pandas as pd
import base64

from typing import List, Any, Dict

from augur.application.db.engine import DatabaseEngine
from augur.application.db.models import Repo, UserRepo, RepoGroup, UserGroup, User, CollectionStatus
from augur.application.db.models.augur_operations import retrieve_org_repos
from augur.application.db.util import execute_session_query


logger = logging.getLogger(__name__)

REPO_ENDPOINT = "https://api.github.com/repos/{}/{}"
ORG_REPOS_ENDPOINT = "https://api.github.com/orgs/{}/repos?per_page=100"
DEFAULT_REPO_GROUP_IDS = [1, 10]
CLI_USER_ID = 1

def parse_repo_url(url: str) -> tuple:
    """ Gets the owner and repo from a url.

    Args:
        url: Github url

    Returns:
        Tuple of owner and repo. Or a tuple of None and None if the url is invalid.
    """

    if url.endswith(".github") or url.endswith(".io") or url.endswith(".js"):

        result = re.search(r"https?:\/\/github\.com\/([A-Za-z0-9 \- _]+)\/([A-Za-z0-9 \- _ \.]+)(.git)?\/?$", url)
    else:

        result = re.search(r"https?:\/\/github\.com\/([A-Za-z0-9 \- _]+)\/([A-Za-z0-9 \- _]+)(.git)?\/?$", url)

    if not result:
        return None, None

    capturing_groups = result.groups()


    owner = capturing_groups[0]
    repo = capturing_groups[1]

    return owner, repo

def parse_org_url(url):
    """ Gets the owner from a org url.

    Args:
        url: Github org url

    Returns:
        Org name. Or None if the url is invalid.
    """

    result = re.search(r"https?:\/\/github\.com\/([A-Za-z0-9 \- _]+)\/?$", url)

    if not result:
        return None

    # if the result is not None then the groups should be valid so we don't worry about index errors here
    return result.groups()[0]


class RepoLoadController:

    def __init__(self, gh_session):
        self.session = gh_session


    def add_cli_repo(self, repo_data: Dict[str, Any], valid_repo=False):
        """Add list of repos to specified repo_groups

        Args:
            url_data: dict with repo_group_id and repo urls
        """

        url = repo_data["url"]
        repo_group_id = repo_data["repo_group_id"]

        if valid_repo or Repo.is_valid_github_repo(self.session, url)[0]:

            # if the repo doesn't exist it adds it
            # if the repo does exist it updates the repo_group_id
            repo_id = Repo.insert(self.session, url, repo_group_id, "CLI")

            if not repo_id:
                logger.warning(f"Invalid repo group id specified for {url}, skipping.")
                return {"status": f"Invalid repo group id specified for {url}, skipping."}

            UserRepo.insert(self.session, repo_id)

            CollectionStatus.insert(self.session, repo_id)

    def add_cli_org(self, org_name):
        """Add list of orgs and their repos to specified repo_groups

        Args:
            org_data: dict with repo_group_id and org urls
        """

        url = f"https://github.com/{org_name}"
        repos = retrieve_org_repos(self.session, url)[0]
        if not repos:
            print(
                f"No organization with name {org_name} could be found")
            return {"status": "No organization found"}

        # check if the repo group already exists
        query = self.session.query(RepoGroup).filter(RepoGroup.rg_name == org_name)
        rg = execute_session_query(query, 'first')
        if rg:
            print(f"{rg.rg_name} is already a repo group")

            return {"status": "Already a repo group"}

        print(f'Organization "{org_name}" found')

        rg = RepoGroup(rg_name=org_name, rg_description="", rg_website="", rg_recache=0, rg_type="Unknown",
                    tool_source="Loaded by user", tool_version="1.0", data_source="Git")
        self.session.add(rg)
        self.session.commit()
        repo_group_id = rg.repo_group_id
        logger.info(f"{org_name} repo group created")

        for repo_url in repos:
            logger.info(
                f"Adding {repo_url}")
            self.add_cli_repo({"url": repo_url, "repo_group_id": repo_group_id}, valid_repo=True)

        return {"status": "Org added"}


    def paginate_repos(self, source, page=0, page_size=25, sort="repo_id", direction="ASC", **kwargs):

        if not source:
            print("Func: paginate_repos. Error: Source Required")
            return None, {"status": "Source Required"}

        if source not in ["all", "user", "group"]:
            print("Func: paginate_repos. Error: Invalid source")
            return None, {"Invalid source"}

        if direction and direction != "ASC" and direction != "DESC":
            print("Func: paginate_repos. Error: Invalid direction")
            return None, {"status": "Invalid direction"}

        try:
            page = int(page) if page else 0
            page_size = int(page_size) if page else 25
        except TypeError:
            print("Func: paginate_repos. Error: Page size and page should be integers")
            return None, {"status": "Page size and page should be integers"}

        if page < 0 or page_size < 0:
            print("Func: paginate_repos. Error: Page size and page should be positive")
            return None, {"status": "Page size and page should be postive"}

        order_by = sort if sort else "repo_id"
        order_direction = direction if direction else "ASC"

        query = self.generate_repo_query(source, count=False, order_by=order_by, direction=order_direction, 
                                    page=page, page_size=page_size, **kwargs)
        if not query[0]:
            return None, {"status": query[1]["status"]}

        if query[1]["status"] == "No data":
            return [], {"status": "No data"}

        get_page_of_repos_sql = s.sql.text(query[0])

        with DatabaseEngine(connection_pool_size=1) as engine:

            results = pd.read_sql(get_page_of_repos_sql, engine)

        results['url'] = results['url'].apply(lambda datum: datum.split('//')[1])

        b64_urls = []
        for i in results.index:
            b64_urls.append(base64.b64encode((results.at[i, 'url']).encode()))
        results['base64_url'] = b64_urls

        data = results.to_dict(orient="records")

        # The SELECT statement in generate_repo_query has been updated to include `repo_name`
        # for row in data:
        #     row["repo_name"] = re.search(r"github\.com\/[A-Za-z0-9 \- _]+\/([A-Za-z0-9 \- _ .]+)$", row["url"]).groups()[0]

        return data, {"status": "success"}

    def get_repo_count(self, source, **kwargs):

        if not source:
            print("Func: get_repo_count. Error: Source Required")
            return None, {"status": "Source Required"}

        if source not in ["all", "user", "group"]:
            print("Func: get_repo_count. Error: Invalid source")
            return None, {"status": "Invalid source"}

        user = kwargs.get("user")
        group_name = kwargs.get("group_name")

        query = self.generate_repo_query(source, count=True, user=user, group_name=group_name)
        if not query[0]:
            return None, query[1]

        if query[1]["status"] == "No data":
            return 0, {"status": "No data"}

        # surround query with count query so we just get the count of the rows
        final_query = f"SELECT count(*) FROM ({query[0]}) a;"
           
        get_page_of_repos_sql = s.sql.text(final_query)

        result = self.session.fetchall_data_from_sql_text(get_page_of_repos_sql)
            
        return result[0]["count"], {"status": "success"}

        return query, {"status": "success"}

    def generate_repo_query(self, source, count, **kwargs):

        if count:
            # only query for repos ids so the query is faster for getting the count
            select = "    DISTINCT(augur_data.repo.repo_id)"
        else:

            select = """    DISTINCT(augur_data.repo.repo_id),
                    augur_data.repo.description,
                    augur_data.repo.repo_git AS url,
                    a.commits_all_time,
                    b.issues_all_time,
                    rg_name,
                    repo_name,
                    augur_data.repo.repo_group_id"""

        query = f"""
            SELECT
                {select}
            FROM
                    augur_data.repo
                    LEFT OUTER JOIN augur_data.api_get_all_repos_commits a ON augur_data.repo.repo_id = a.repo_id
                    LEFT OUTER JOIN augur_data.api_get_all_repos_issues b ON augur_data.repo.repo_id = b.repo_id
                    JOIN augur_data.repo_groups ON augur_data.repo.repo_group_id = augur_data.repo_groups.repo_group_id\n"""

        if source == "user":
            
            user = kwargs.get("user")
            if not user:
                print("Func: generate_repo_query. Error: User not passed when trying to get user repos")
                return None, {"status": "User not passed when trying to get user repos"}
                
            if not user.groups:
                return None, {"status": "No data"}

            query += "\t\t    JOIN augur_operations.user_repos ON augur_data.repo.repo_id = augur_operations.user_repos.repo_id\n"
            query += "\t\t    JOIN augur_operations.user_groups ON augur_operations.user_repos.group_id = augur_operations.user_groups.group_id\n"
            query += f"\t\t    WHERE augur_operations.user_groups.user_id = {user.user_id}\n"

        elif source == "group":

            user = kwargs.get("user")
            if not user:
                print("Func: generate_repo_query. Error: User not specified")
                return None, {"status": "User not specified"}

            group_name = kwargs.get("group_name")
            if not group_name:
                print("Func: generate_repo_query. Error: Group name not specified")
                return None, {"status": "Group name not specified"}

            group_id = UserGroup.convert_group_name_to_id(self.session, user.user_id, group_name)
            if group_id is None:
                print("Func: generate_repo_query. Error: Group does not exist")
                return None, {"status": "Group does not exists"}

            query += "\t\t    JOIN augur_operations.user_repos ON augur_data.repo.repo_id = augur_operations.user_repos.repo_id\n"
            query += f"\t\t    WHERE augur_operations.user_repos.group_id = {group_id}\n"

        if not count:
            order_by = kwargs.get("order_by") or "repo_id"
            direction = kwargs.get("direction") or "ASC"
            page = kwargs.get("page") or 0
            page_size = kwargs.get("page_size") or 25

            query += f"\t    ORDER BY {order_by} {direction}\n"
            query += f"\t    LIMIT {page_size}\n"
            query += f"\t    OFFSET {page*page_size};\n"

        return query, {"status": "success"}

