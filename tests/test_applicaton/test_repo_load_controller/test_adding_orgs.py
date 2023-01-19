import pytest
import logging

from tests.test_applicaton.test_repo_load_controller.helper import *
from augur.tasks.github.util.github_task_session import GithubTaskSession

from augur.util.repo_load_controller import RepoLoadController, DEFAULT_REPO_GROUP_IDS, CLI_USER_ID


logger = logging.getLogger(__name__)


VALID_ORG = {"org": "CDCgov", "repo_count": 246}


def test_add_frontend_org_with_invalid_org(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users", "config"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:

        data = {"user_id": 2, "repo_group_id": DEFAULT_REPO_GROUP_IDS[0], "org_name": "chaosssss", "user_group_name": "test_group", "user_group_id": 1}

        with test_db_engine.connect() as connection:

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_repo_group_insert_statement(data["repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))
            query_statements.append(get_user_group_insert_statement(data["user_id"], data["user_group_name"], data["user_group_id"]))

            connection.execute("".join(query_statements))

        add_keys_to_test_db(test_db_engine)
        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            url = f"https://github.com/{data['org_name']}/"
            result = controller.add_frontend_org(url, data["user_id"], data["user_group_name"])
            assert result["status"] == "Invalid org"

            # test with invalid group name
            result = controller.add_frontend_org(url, data["user_id"], "Invalid group name")
            assert result["status"] == "Invalid group name"

        with test_db_engine.connect() as connection:

            result = get_repos(connection)
            assert result is not None
            assert len(result) == 0

    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)


def test_add_frontend_org_with_valid_org(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users", "config"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        with test_db_engine.connect() as connection:

            data = {"user_id": 2, "repo_group_id": DEFAULT_REPO_GROUP_IDS[0], "org_name": VALID_ORG["org"], "user_group_name": "test_group", "user_group_id": 1}

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_repo_group_insert_statement(data["repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))
            query_statements.append(get_user_group_insert_statement(data["user_id"], data["user_group_name"], data["user_group_id"]))

            connection.execute("".join(query_statements))

        add_keys_to_test_db(test_db_engine)

        with GithubTaskSession(logger, test_db_engine) as session:

            url = "https://github.com/{}/".format(data["org_name"])
            result = RepoLoadController(session).add_frontend_org(url, data["user_id"], data["user_group_name"])
            assert result["status"] == "Org repos added"

        with test_db_engine.connect() as connection:

            result = get_repos(connection)
            assert result is not None
            assert len(result) == VALID_ORG["repo_count"]

            user_repo_result = get_user_repos(connection)
            assert user_repo_result is not None
            assert len(user_repo_result) == VALID_ORG["repo_count"]
            
    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)


def test_add_cli_org_with_valid_org(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users", "config"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        with test_db_engine.connect() as connection:

            data = {"user_id": CLI_USER_ID, "repo_group_id": 5, "org_name": VALID_ORG["org"], "user_group_name": "test_group", "user_group_id": 1}

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_repo_group_insert_statement(data["repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))
            query_statements.append(get_user_group_insert_statement(data["user_id"], data["user_group_name"], data["user_group_id"]))

            connection.execute("".join(query_statements))

        repo_count = None

        add_keys_to_test_db(test_db_engine)

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            result = controller.add_cli_org(data["org_name"])

            assert result["status"] == "Org added"
            
            result2 = controller.add_cli_org("Invalid org")
            assert result2["status"] == "No organization found"


        with test_db_engine.connect() as connection:

            result = get_repos(connection)
            assert result is not None
            assert len(result) == VALID_ORG["repo_count"]

            user_repo_result = get_user_repos(connection)
            assert user_repo_result is not None
            assert len(user_repo_result) == VALID_ORG["repo_count"]

    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)

    
