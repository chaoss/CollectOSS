import pytest
import httpx
import logging

from sqlalchemy.sql import text

from augur.tasks.github.pull_requests.core import *
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Config 
from augur.tasks.util.AugurUUID import GithubUUID
from augur.application.db.data_parse import extract_needed_contributor_data
from augur.application.db.engine import create_database_engine
from augur.application.db.util import execute_session_query

logger = logging.getLogger(__name__)
not_provided_cntrb_id = '00000000-0000-0000-0000-000000000000'
nan_cntrb_id = '01000000-0000-0000-0000-000000000000'

@pytest.fixture
def github_api_key_headers():

    with DatabaseSession(logger) as session:

        query = session.query(Config).filter(Config.section_name == "Keys", Config.setting_name == "github_api_key")
        api_key = execute_session_query(query, 'one').value

        headers = {"Authorization": f'token {api_key}'}

        yield headers


@pytest.mark.parametrize("pr_number", [1, 2, 26])
def test_extract_data_from_pr(github_api_key_headers, pr_number):
    
    url = f"https://api.github.com/repos/operate-first/blueprint/pulls/{str(pr_number)}" 

    with httpx.Client() as client:

        data = client.request(method="GET", url=url, headers=github_api_key_headers, timeout=180).json()

        metadata_keys = ["head", "base"]

        meatadata_len = 0
        contributors_len = 0

        try:
            data["user"]
            contributors_len +=1
        except KeyError:
            pass

        for key in metadata_keys:

            try:
                metadata = data[key]
                meatadata_len += 1
            except KeyError:
                continue

            # if login exists on metadata then add count to contributors
            try:
                data[key]["user"]["login"]
                contributors_len += 1
            except KeyError:
                pass

        # count one contributor for every reviewer and assignee
        for value in data["requested_reviewers"] + data["assignees"]:

            try:
                value["login"]
                contributors_len += 1
            except KeyError:
                continue


        labels_len = len(data["labels"])
        requested_reviewers_len = len(data["requested_reviewers"])
        assignees_len = len(data["assignees"])        

        # print(f"Pr number: {pr_number}")
        # print(f"Metadata: {meatadata_len}")
        # print(f"Labels: {labels_len}")
        # print(f"Reviewers: {requested_reviewers_len}")
        # print(f"Assignees: {assignees_len}")
        # print(f"Contributors: {contributors_len}")

        repo_id = -1
        tool_source = "Pr Task"
        tool_version = "2.0"
        data_source = "Github API"

        pr, labels, assignees, reviewers, metadata, contributors = extract_data_from_pr(data, repo_id, tool_source, tool_version, data_source)

        assert pr is not None
        assert labels is not None
        assert assignees is not None
        assert reviewers is not None
        assert metadata is not None
        assert contributors is not None

        assert type(pr) == dict
        assert len(labels) == labels_len
        assert len(assignees) == assignees_len
        assert len(reviewers) == requested_reviewers_len
        assert len(metadata) == meatadata_len
        assert len(contributors) == contributors_len
        

def test_extract_data_from_pr_list(github_api_key_headers):

    base_url = f"https://api.github.com/repos/operate-first/blueprint/pulls/" 

    contributor_count = 0
    metadata_count = 0
    reviewer_count = 0
    assignee_count = 0
    label_count = 0

    raw_pr_data = []

    numbers = [1, 2, 3, 4, 5, 6, 7, 26]
    for pr_number in numbers:

        url = base_url + str(pr_number)

        with httpx.Client() as client:

            data = client.request(method="GET", url=url, headers=github_api_key_headers, timeout=180).json()

            raw_pr_data.append(data)

            metadata_keys = ["head", "base"]

            try:
                data["user"]
                contributor_count +=1
            except KeyError:
                pass

            for key in metadata_keys:

                # if "head" or "base" exist add one ot metadata_len
                if data[key]:

                    metadata_count += 1
                
                    # if login exists on metadata then add count to contributors
                    try:
                        data[key]["user"]["login"]
                        contributor_count += 1
                    except KeyError:
                        pass

            # count one contributor for every reviewer and assignee
            for value in data["requested_reviewers"] + data["assignees"]:

                try:
                    value["login"]
                    contributor_count += 1
                except KeyError:
                    continue

            label_count += len(data["labels"])
            reviewer_count += len(data["requested_reviewers"])
            assignee_count += len(data["assignees"])

    repo_id = -1
    tool_source = "Pr Task"
    tool_version = "2.0"
    data_source = "Github API"

    pr_dicts, pr_mapping_data, pr_numbers, contributors = extract_data_from_pr_list(raw_pr_data, repo_id, tool_source, tool_version, data_source)

    assert pr_dicts is not None
    assert pr_mapping_data is not None
    assert pr_numbers is not None
    assert contributors is not None 

    assert len(pr_dicts) == len(numbers)
    assert len(pr_mapping_data) == len(numbers)
    assert len(pr_numbers) == len(numbers)
    assert contributor_count == len(contributors)

    

    urls = [base_url + str(pr_number) for pr_number in numbers]

    returned_metadata_count = 0
    returned_reviewer_count = 0
    returned_assignee_count = 0
    returned_label_count = 0 

    for pr_number in numbers:

        url = base_url + str(pr_number)

        other_pr_data = pr_mapping_data[url]


        returned_metadata_count += len(other_pr_data["metadata"])
        returned_reviewer_count += len(other_pr_data["reviewers"])
        returned_assignee_count += len(other_pr_data["assignees"])
        returned_label_count += len(other_pr_data["labels"])      

    assert metadata_count == returned_metadata_count
    assert reviewer_count == returned_reviewer_count
    assert assignee_count == returned_assignee_count
    assert label_count == returned_label_count
        



@pytest.mark.parametrize("pr_number", [1, 2, 3, 4, 5, 6, 7, 26])
def test_insert_pr_contributors(github_api_key_headers, test_db_session, pr_number):

    try:

        url = f"https://api.github.com/repos/operate-first/blueprint/pulls/{str(pr_number)}" 

        contributors = []
        with httpx.Client() as client:

            data = client.request(method="GET", url=url, headers=github_api_key_headers, timeout=180).json()

            metadata_keys = ["head", "base"]

            try:
                contributors.append(data["user"])
            except KeyError:
                pass

            for key in metadata_keys:

                # if login exists on metadata then add count to contributors
                try:
                    contributors.append(data[key]["user"])
                except KeyError:
                    pass

            # count one contributor for every reviewer and assignee
            for value in data["requested_reviewers"] + data["assignees"]:

                try:
                    contributors.append(value)
                except KeyError:
                    continue

        tool_source = "Pr Task"
        tool_version = "2.0"
        data_source = "Github API"

        contributors_to_pass_to_insert = []
        unique_contributors = []
        for cntrb in contributors:

            contributors_to_pass_to_insert.append(
                extract_needed_contributor_data(cntrb, tool_source, tool_version, data_source)
            )

            if cntrb["login"] not in unique_contributors:
                unique_contributors.append(cntrb["login"])
        

        insert_pr_contributors(contributors_to_pass_to_insert, test_db_session, "Insert contrbibutors test")

        with test_db_session.engine.connect() as connection:

            result = connection.execute(f"SELECT * FROM augur_data.contributors WHERE cntrb_id!='{not_provided_cntrb_id}' AND cntrb_id!='{nan_cntrb_id}'").fetchall()

            assert result is not None
            assert len(result) == len(unique_contributors)

            for row_tuple in result:
                row = dict(row_tuple)

                assert row["cntrb_login"] in unique_contributors

    finally:

         with test_db_session.engine.connect() as connection:

                connection.execute(f"DELETE FROM augur_data.contributors WHERE cntrb_id!='{not_provided_cntrb_id}' AND cntrb_id!='{nan_cntrb_id}';")

repos = []
repos.append({"owner": "chaoss", "repo": "augur"})
repos.append({"owner": "operate-first", "repo": "blueprint"})
@pytest.mark.parametrize("repo", repos)
def test_insert_prs(github_api_key_headers, test_db_session, repo):

    url = f"https://api.github.com/repos/{repo['owner']}/{repo['repo']}/pulls?state=all&direction=asc"

    try:
        with httpx.Client() as client:

            prs = client.request(method="GET", url=url, headers=github_api_key_headers, timeout=180).json()

            urls = [pr["url"] for pr in prs]

            repo_id = 1
            tool_source = "Pr Task"
            tool_version = "2.0"
            data_source = "Github API"

            prs_insert = []
            contributors_inserted = []
            for pr in prs:

                contributor = extract_needed_contributor_data(pr["user"], tool_source, tool_version, data_source)

                # ensure we don't try to insert same contributor twice
                if pr["user"]["login"] not in contributors_inserted:

                    with test_db_session.engine.connect() as connection:

                        # insert the cntrb_id and cntrb_login into the contributors table so the contributor is present. 
                        # This is so we don't get a foreign key error on the cntrb_id when we insert the prs
                        query = text("""INSERT INTO "augur_data"."contributors" ("cntrb_login", "cntrb_email", "cntrb_full_name", "cntrb_company", "cntrb_created_at", "cntrb_type", "cntrb_fake", "cntrb_deleted", "cntrb_long", "cntrb_lat", "cntrb_country_code", "cntrb_state", "cntrb_city", "cntrb_location", "cntrb_canonical", "cntrb_last_used", "gh_user_id", "gh_login", "gh_url", "gh_html_url", "gh_node_id", "gh_avatar_url", "gh_gravatar_id", "gh_followers_url", "gh_following_url", "gh_gists_url", "gh_starred_url", "gh_subscriptions_url", "gh_organizations_url", "gh_repos_url", "gh_events_url", "gh_received_events_url", "gh_type", "gh_site_admin", "gl_web_url", "gl_avatar_url", "gl_state", "gl_username", "gl_full_name", "gl_id", "tool_source", "tool_version", "data_source", "data_collection_date", "cntrb_id") VALUES (:cntrb_login, 'kannayoshihiro@gmail.com', 'KANNA Yoshihiro', 'UTMC', '2009-04-17 12:43:58', NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, 'kannayoshihiro@gmail.com', '2021-01-28 21:56:10-06', 74832, :gh_login, 'https://api.github.com/users/nan', 'https://github.com/nan', 'MDQ6VXNlcjc0ODMy', 'https://avatars.githubusercontent.com/u/74832?v=4', '', 'https://api.github.com/users/nan/followers', 'https://api.github.com/users/nan/following{/other_user}', 'https://api.github.com/users/nan/gists{/gist_id}', 'https://api.github.com/users/nan/starred{/owner}{/repo}', 'https://api.github.com/users/nan/subscriptions', 'https://api.github.com/users/nan/orgs', 'https://api.github.com/users/nan/repos', 'https://api.github.com/users/nan/events{/privacy}', 'https://api.github.com/users/nan/received_events', 'User', 'false', NULL, NULL, NULL, NULL, NULL, NULL, 'GitHub API Worker', '1.0.0', 'GitHub API', '2021-10-28 15:23:46', :cntrb_id);

                        DELETE FROM "augur_data"."repo";
                        DELETE FROM "augur_data"."repo_groups";
                        INSERT INTO "augur_data"."repo_groups" ("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (1, 'Default Repo Group', 'The default repo group created by the schema generation script', '', 0, '2019-06-03 15:55:20', 'GitHub Organization', 'load', 'one', 'git', '2019-06-05 13:36:25');
                        
                        INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "repo_archived_date_collected", "repo_archived", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (1, 1, 'https://github.com/chaoss/augur', NULL, NULL, '2022-08-15 21:08:07', 'New', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2022-08-15 21:08:07');
                        """)

                        connection.execute(query, **contributor)

                        contributors_inserted.append(pr["user"]["login"])
                
                pr["cntrb_id"] = contributor["cntrb_id"]
                
                prs_insert.append(
                        extract_needed_pr_data(pr, repo_id, tool_source, tool_version)
                )
               

            return_data = insert_prs(prs_insert, test_db_session, "Insert contrbibutors test")

            with test_db_session.engine.connect() as connection:

                result = connection.execute(f"SELECT * FROM augur_data.pull_requests;").fetchall()

                assert result is not None
                assert len(result) == len(prs) == len(return_data)

                if len(return_data) > 0:
                    assert type(return_data[0]) == dict

                for row_tuple in result:
                    row = dict(row_tuple)

                    assert row["pr_url"] in urls

    finally:

         with test_db_session.engine.connect() as connection:

            connection.execute(f"DELETE FROM augur_data.pull_requests;")
            connection.execute("""DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                """)
            connection.execute(f"DELETE FROM augur_data.contributors WHERE cntrb_id!='{not_provided_cntrb_id}' AND cntrb_id!='{nan_cntrb_id}';")



def test_map_other_pr_data_to_pr(github_api_key_headers):

    pr_numbers = [1, 2, 3, 4, 5, 6]
    base_url = "https://api.github.com/repos/operate-first/blueprint/pulls/"

    pr_return_data = []
    raw_pr_data = []
    pr_mapping_data = {}

    for number in pr_numbers:

        url = base_url + str(number)

        pr_return_data.append({f'pull_request_id': number, 'pr_url': url})
        
        with httpx.Client() as client:

            pr = client.request(method="GET", url=url, headers=github_api_key_headers, timeout=180).json()

            raw_pr_data.append(pr)

            mapping_data_key = pr["url"]
            pr_mapping_data[mapping_data_key] = {
                                                "labels": pr["labels"],
                                                "assignees": pr["assignees"],
                                                "reviewers": pr["requested_reviewers"],
                                                "metadata": [pr["head"], pr["base"]]
                                                }      

    labels, assignees, reviewers, metadata  = map_other_pr_data_to_pr(pr_return_data, pr_mapping_data, logger)


    for pr in raw_pr_data:

        pr_number = pr["number"]

        pr_labels = pr["labels"]
        pr_assignees = pr["assignees"]
        pr_reviewers = pr["requested_reviewers"]
        pr_metadata = [pr["head"], pr["base"]]

        related_labels = [label for label in labels if label["pull_request_id"] == pr_number]
        related_assignees = [assignee for assignee in assignees if assignee["pull_request_id"] == pr_number]
        related_reviewers = [reviewer for reviewer in reviewers if reviewer["pull_request_id"] == pr_number]
        related_metadata = [meta for meta in metadata if meta["pull_request_id"] == pr_number]

        for label in related_labels:

            assert label["id"] in [pr_label["id"] for pr_label in pr_labels]
    
        for assignee in related_assignees:

            assert assignee["id"] in [pr_assignee["id"] for pr_assignee in pr_assignees]

        for reviewer in related_reviewers:

            assert reviewer["id"] in [pr_reviewer["id"] for pr_reviewer in pr_reviewers]

        for related_meta in related_metadata:

            assert related_meta["sha"] in [pr_meta["sha"] for pr_meta in pr_metadata]



# def test_insert_other_pr_data():

#     pass

