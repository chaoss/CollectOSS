import re
import logging

import sqlalchemy as s
import pandas as pd
import base64

from typing import List, Any, Dict

from augur.application.db.engine import DatabaseEngine
from augur.application.db.models import Repo, UserRepo, RepoGroup, UserGroup, User, CollectionStatus
from augur.application.db.models.augur_operations import retrieve_owner_repos
from augur.application.db.util import execute_session_query


logger = logging.getLogger(__name__)


class RepoLoadController:

    def __init__(self, gh_session):
        self.session = gh_session


    def add_cli_repo(self, repo_data: Dict[str, Any], from_org_list=False, repo_type=None):
        """Add list of repos to specified repo_groups

        Args:
            url_data: dict with repo_group_id and repo urls
        """

        # if the repo is from an org list then 
        # the repo type must be passed in
        # so we don't have to hit an endpoint 
        # for every repo to get its type
        if from_org_list and not repo_type:
            return False, {"status": "Repo type must be passed if the repo is from an organization's list of repos"}

        url = repo_data["url"]
        repo_group_id = repo_data["repo_group_id"]

        # if it is from not from an org list then we need to check its validity, and get the repo type
        if not from_org_list:
            result = Repo.is_valid_github_repo(self.session, url)
            if not result[0]:
                return False, {"status": result[1]["status"], "repo_url": url}
            
            repo_type = result[1]["repo_type"]


        # if the repo doesn't exist it adds it
        repo_id = Repo.insert(self.session, url, repo_group_id, "CLI", repo_type)

        if not repo_id:
            logger.warning(f"Invalid repo group id specified for {url}, skipping.")
            return False, {"status": f"Invalid repo group id specified for {url}, skipping."}

        UserRepo.insert(self.session, repo_id)

        #collection_status records are now only added during collection -IM 5/1/23
        #CollectionStatus.insert(self.session, repo_id)

        return True, {"status": "Repo added", "repo_url": url}

    def add_cli_org(self, org_name):
        """Add list of orgs and their repos to specified repo_groups

        Args:
            org_data: dict with repo_group_id and org urls
        """
        
        result = retrieve_owner_repos(self.session, org_name)
        repos = result[0]
        type = result[1]["owner_type"]
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
        print(f"{org_name} repo group created")

        for repo_url in repos:
            print(f"Adding {repo_url}")
            result, status = self.add_cli_repo({"url": repo_url, "repo_group_id": repo_group_id}, from_org_list=True, repo_type=type)
            if not result:
                print(status["status"])

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

        query, query_args, result = self.generate_repo_query(source, count=False, order_by=order_by, direction=order_direction, 
                                    page=page, page_size=page_size, **kwargs)
        if not query:
            return None, {"status": result["status"]}

        if result["status"] == "No data":
            return [], {"status": "No data"}

        get_page_of_repos_sql = s.sql.text(query)

        with DatabaseEngine(connection_pool_size=1) as engine:

            results = pd.read_sql(get_page_of_repos_sql, engine, params=query_args)

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

        query, query_args, result = self.generate_repo_query(source, count=True, **kwargs)
        if not query:
            return None, result

        if result["status"] == "No data":
            return 0, {"status": "No data"}

        # surround query with count query so we just get the count of the rows
        final_query = f"SELECT count(*) FROM ({query}) a;"
           
        get_page_of_repos_sql = s.sql.text(final_query)

        result = self.session.execute(get_page_of_repos_sql, query_args).fetchall()
            
        return result[0]["count"], {"status": "success"}

    def generate_repo_query(self, source, count, **kwargs):
        # TODO: need more flexible way of calculating count for variable column queries

        query_args = {}

        if count:
            # only query for repos ids so the query is faster for getting the count
            select = """    DISTINCT(augur_data.repo.repo_id),
                (regexp_match(augur_data.repo.repo_git, 'github\.com\/[A-Za-z0-9 \- _]+\/([A-Za-z0-9 \- _ .]+)$'))[1] as repo_name,
                (regexp_match(augur_data.repo.repo_git, 'github\.com\/([A-Za-z0-9 \- _]+)\/[A-Za-z0-9 \- _ .]+$'))[1] as repo_owner"""
        else:

            select = """    DISTINCT(augur_data.repo.repo_id),
                    augur_data.repo.description,
                    augur_data.repo.repo_git AS url,
                    COALESCE(a.commits_all_time, 0) as commits_all_time,
                    COALESCE(b.issues_all_time, 0) as issues_all_time,
                    rg_name,
                    (regexp_match(augur_data.repo.repo_git, 'github\.com\/[A-Za-z0-9 \- _]+\/([A-Za-z0-9 \- _ .]+)$'))[1] as repo_name,
                    (regexp_match(augur_data.repo.repo_git, 'github\.com\/([A-Za-z0-9 \- _]+)\/[A-Za-z0-9 \- _ .]+$'))[1] as repo_owner,
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
            query += "\t\t    WHERE augur_operations.user_groups.user_id = :user_id\n"

            query_args["user_id"] = user.user_id

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
            query += "\t\t    WHERE augur_operations.user_repos.group_id = :group_id \n"

            query_args["group_id"] = group_id
        
        # implement sorting by query_key
        search = kwargs.get("search")
        qkey = kwargs.get("query_key") or ["repo_name", "repo_owner"]

        if search:
            # The WHERE clause cannot use a column alias created in the directly preceeding SELECT clause
            # We must wrap the query in an additional SELECT with a table alias
            # This way, we can use WHERE with the computed repo_name column alias
            query = f"""\tSELECT * from (
                {query}
            ) res\n"""
            # This is done so repos with a NULL repo_name can still be sorted.
            # "res" here is a randomly chosen table alias, short for "result"
            # It is only included because it is required by the SQL syntax

            if isinstance(qkey, list) and len(qkey) > 0:
                query += f"\tWHERE :qkey_where ilike :search\n"
                query_args["qkey_where"] = qkey.pop(0)

                for i, key in enumerate(qkey):
                    param_name = f"qkey_or_{i}"
                    query += f"OR :{param_name} ilike :search\n"
                    query_args[param_name] = key
            else:
                query += f"\tWHERE :qkey ilike :search\n"
                query_args["qkey"] = qkey
            
            query_args["search"] = f'%{search}%'


        if not count:
            order_by = kwargs.get("order_by") or "repo_id"
            page = kwargs.get("page") or 0
            page_size = kwargs.get("page_size") or 25
            direction = kwargs.get("direction") or "ASC"

            if direction not in ["ASC", "DESC"]:
                return None, None, {"status": "Invalid direction"}
            
            if order_by not in ["repo_id", "repo_name", "repo_owner", "commits_all_time", "issues_all_time"]:
                return None, None, {"status": "Invalid order by"}

            offset = page*page_size

            query += f"\tORDER BY {order_by} {direction}\n"
            query += "\tLIMIT :page_size\n"
            query += "\tOFFSET :offset;\n"

            query_args["page_size"] = page_size
            query_args["offset"] = offset

        return query, query_args, {"status": "success"}

