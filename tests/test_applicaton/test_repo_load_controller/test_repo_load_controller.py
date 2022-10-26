import logging
import pytest
import uuid
import sqlalchemy as s


from augur.util.repo_load_controller import RepoLoadController

from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Contributor, Issue, Config
from augur.tasks.github.util.github_paginator import hit_api


logger = logging.getLogger(__name__)




def get_delete_statement(schema, table):

    return """DELETE FROM "{}"."{}";""".format(schema, table)

def get_repo_delete_statement():

    return get_delete_statement("augur_data", "repo")

def get_repo_group_delete_statement():

    return get_delete_statement("augur_data", "repo_groups")

def get_user_delete_statement():

    return get_delete_statement("augur_operations", "users")

def add_keys_to_test_db(test_db_engine):

    row = None
    section_name = "Keys"
    setting_name = "github_api_key"
    with DatabaseSession(logger) as session:
        row = session.query(Config).filter(Config.section_name==section_name, Config.setting_name==setting_name).one()

    with DatabaseSession(logger, test_db_engine) as test_session:
       test_session.add(row)
       test_session.commit()


def remove_keys_from_test_db(test_db_engine):

     with test_db_engine.connect() as connection:

            query = s.text(get_delete_statement("augur_operations", "config"))

            connection.execute(query)

def get_repo_insert_statement(repo_id, rg_id, repo_url="place holder url", repo_status="New"):

    return """INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "repo_archived_date_collected", "repo_archived", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES ({}, {}, '{}', NULL, NULL, '2022-08-15 21:08:07', '{}', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2022-08-15 21:08:07');""".format(repo_id, rg_id, repo_url, repo_status)

def get_repo_group_insert_statement(rg_id):

    return """INSERT INTO "augur_data"."repo_groups" ("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES ({}, 'Default Repo Group', 'The default repo group created by the schema generation script', '', 0, '2019-06-03 15:55:20', 'GitHub Organization', 'load', 'one', 'git', '2019-06-05 13:36:25');""".format(rg_id)

def get_user_insert_statement(user_id):

    return """INSERT INTO "augur_operations"."users" ("user_id", "login_name", "login_hashword", "email", "first_name", "last_name", "admin") VALUES ({}, 'bil', 'pass', 'b@gmil.com', 'bill', 'bob', false);""".format(user_id)


def test_is_valid_repo():

    with GithubTaskSession(logger) as session:

        controller = RepoLoadController(session)

        # test invalid repo git url
        assert controller.is_valid_repo("hello world") is False

        #  test correct org with invalid repo
        assert controller.is_valid_repo("https://github.com/chaoss/hello") is False

        # test invalid org with correct repo
        assert controller.is_valid_repo("https://github.com/hello124/augur") is False

        # test empty org
        assert controller.is_valid_repo("https://github.com//augur") is False

        # test empty repo
        assert controller.is_valid_repo("https://github.com/chaoss/") is False

        # test empty org and repo
        assert controller.is_valid_repo("https://github.com//") is False

        # test correct repo git
        assert controller.is_valid_repo("https://github.com/chaoss/augur") is True

        assert controller.is_valid_repo("https://github.com/chaoss/augur/") is True

        assert controller.is_valid_repo("https://github.com/chaoss/augur.git") is True


def test_add_repo_row(test_db_engine):

    try:
        data = {"rg_id": 1, "repo_id": 1, "tool_source": "Frontend",
                "repo_url": "https://github.com/chaoss/augur"}

        with test_db_engine.connect() as connection:

            query_statements = []
            query_statements.append(get_repo_delete_statement())
            query_statements.append(get_repo_group_delete_statement())
            query_statements.append(get_repo_group_insert_statement(data["rg_id"]))

            query = s.text("".join(query_statements))

            connection.execute(query)

        with DatabaseSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            assert controller.add_repo_row(data["repo_url"], data["rg_id"], data["tool_source"]) is not None

        with test_db_engine.connect() as connection:

            query = s.text(
                """SELECT * FROM "augur_data"."repo" WHERE "repo_git"=:repo_url;""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) > 0

    finally:
        
        with test_db_engine.connect() as connection:

            connection.execute("""DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";""")



def test_add_repo_row_with_updates(test_db_engine):

    try:
        data = {"old_rg_id": 1, "new_rg_id": 2, "repo_id": 1, "repo_id_2": 2, "tool_source": "CLI",
                "repo_url": "https://github.com/chaoss/augur", "repo_url_2": "https://github.com/chaoss/grimoirelab-perceval-opnfv",  "repo_status": "Complete"}

        with test_db_engine.connect() as connection:

            query_statements = []
            query_statements.append(get_repo_delete_statement())
            query_statements.append(get_repo_group_delete_statement())
            query_statements.append(get_repo_group_insert_statement(data["old_rg_id"]))
            query_statements.append(get_repo_group_insert_statement(data["new_rg_id"]))
            query_statements.append(get_repo_insert_statement(data["repo_id"], data["old_rg_id"], repo_url=data["repo_url"], repo_status=data["repo_status"]))

            query = s.text("".join(query_statements))

            connection.execute(query)

        with DatabaseSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            result = controller.add_repo_row(data["repo_url"], data["new_rg_id"], data["tool_source"]) is not None
            assert result == data["repo_id"]

        with test_db_engine.connect() as connection:

            query = s.text(
                """SELECT * FROM "augur_data"."repo" WHERE "repo_git"=:repo_url;""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) == 1

            value = dict(result[0])
            assert value["repo_status"] == data["repo_status"]
            assert value["repo_group_id"] == data["new_rg_id"]



    finally:

        with test_db_engine.connect() as connection:

            connection.execute("""DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";""")


def test_add_repo_to_user(test_db_engine):

    try:
        with test_db_engine.connect() as connection:

            data = {"repo_id": 1, "user_id": 2, "user_repo_group_id": 1}

            query_statements = []
            query_statements.append(get_repo_delete_statement())
            query_statements.append(get_repo_group_delete_statement())
            query_statements.append(get_repo_group_insert_statement(data["user_repo_group_id"]))
            query_statements.append(get_repo_insert_statement(data["repo_id"], data["user_repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))

            connection.execute("".join(query_statements))

        with DatabaseSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            controller.add_repo_to_user(data["repo_id"], data["user_id"])

        with test_db_engine.connect() as connection:

            query = s.text("""SELECT * FROM "augur_operations"."user_repos" WHERE "user_id"=:user_id AND "repo_id"=:repo_id""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) > 0

    finally:
        with test_db_engine.connect() as connection:

            connection.execute("""
                                DELETE FROM "augur_operations"."user_repos";
                                DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                DELETE FROM "augur_operations"."users";
                                """)


def test_add_frontend_repos_with_duplicates(test_db_engine):

    try:
        with test_db_engine.connect() as connection:

            url = "https://github.com/operate-first/operate-first-twitter"

            data = {"user_id": 2, "default_repo_group_id": 1}

            query_statements = []
            query_statements.append(get_repo_delete_statement())
            query_statements.append(get_repo_group_delete_statement())
            query_statements.append(get_repo_group_insert_statement(data["default_repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))

            connection.execute("".join(query_statements))
        
        add_keys_to_test_db(test_db_engine)

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            controller.add_frontend_repo(url, data["user_id"])
            controller.add_frontend_repo(url, data["user_id"])

        with test_db_engine.connect() as connection:

            query = s.text(
                """SELECT * FROM "augur_data"."repo";""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) == 1

            assert dict(result[0])["repo_git"] == url

    finally:
        with test_db_engine.connect() as connection:

            connection.execute("""
                                DELETE FROM "augur_operations"."user_repos";
                                DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                DELETE FROM "augur_operations"."users" WHERE user_id=2;
                                """)


def test_add_frontend_repos_with_invalid_repo(test_db_engine):

    try:
        with test_db_engine.connect() as connection:

            url = "https://github.com/chaoss/whitepaper"

            data = {"user_id": 2, "default_repo_group_id": 1}

            query_statements = []
            query_statements.append(get_repo_delete_statement())
            query_statements.append(get_repo_group_delete_statement())
            query_statements.append(get_repo_group_insert_statement(data["default_repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))

            connection.execute("".join(query_statements))

        add_keys_to_test_db(test_db_engine)

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            controller.add_frontend_repo(url, data["user_id"])

        with test_db_engine.connect() as connection:

            query = s.text(
                """SELECT * FROM "augur_data"."repo";""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) == 0

    finally:
        with test_db_engine.connect() as connection:

            connection.execute("""
                                DELETE FROM "augur_operations"."user_repos";
                                DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                DELETE FROM "augur_operations"."users" WHERE user_id=2;
                                """)


def test_add_frontend_org_with_invalid_org(test_db_engine):

    try:
        with test_db_engine.connect() as connection:

            url = "https://github.com/chaosssss/"

            data = {"user_id": 2, "default_repo_group_id": 1}

            query_statements = []
            query_statements.append(get_repo_delete_statement())
            query_statements.append(get_repo_group_delete_statement())
            query_statements.append(get_repo_group_insert_statement(data["default_repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))

            connection.execute("".join(query_statements))

        add_keys_to_test_db(test_db_engine)

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            controller.add_frontend_org(url, data["user_id"])

        with test_db_engine.connect() as connection:

            query = s.text(
                """SELECT * FROM "augur_data"."repo";""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) == 0

    finally:
        with test_db_engine.connect() as connection:

            connection.execute("""
                                DELETE FROM "augur_operations"."user_repos";
                                DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                DELETE FROM "augur_operations"."users" WHERE user_id=2;
                                """)


def test_add_frontend_org_with_valid_org(test_db_engine):

    try:
        with test_db_engine.connect() as connection:

            url = "https://github.com/chaoss/"


            data = {"user_id": 2, "default_repo_group_id": 1}

            query_statements = []
            query_statements.append(get_repo_delete_statement())
            query_statements.append(get_repo_group_delete_statement())
            query_statements.append(get_repo_group_insert_statement(data["default_repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))

            connection.execute("".join(query_statements))

        repo_count = None

        add_keys_to_test_db(test_db_engine)

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            controller.add_frontend_org(url, data["user_id"])

            attempts = 0
            while attempts < 10:
                result = hit_api(session.oauths, "https://api.github.com/orgs/chaoss/repos?per_page=100", logger)

                # if result is None try again
                if not result:
                    attempts += 1
                    continue

                response = result.json()

                if response:
                    repo_count = len(response)
                    break


        with test_db_engine.connect() as connection:

            query = s.text(
                """SELECT * FROM "augur_data"."repo";""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) == repo_count

            user_repo_query = s.text(
                """SELECT * FROM "augur_operations"."user_repos";""")

            user_repo_result = connection.execute(user_repo_query, **data).fetchall()

            assert user_repo_result is not None
            assert len(user_repo_result) == repo_count
            
    finally:

        with test_db_engine.connect() as connection:

            connection.execute("""
                                DELETE FROM "augur_operations"."user_repos";
                                DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                DELETE FROM "augur_operations"."users" WHERE user_id=2;
                                """)


def test_add_cli_org_with_valid_org(test_db_engine):

    try:
        with test_db_engine.connect() as connection:

            data = {"user_id": 1, "default_repo_group_id": 1, "org_name": "chaoss"}

            query_statements = []
            query_statements.append(get_repo_delete_statement())
            query_statements.append(get_repo_group_delete_statement())
            query_statements.append(get_repo_group_insert_statement(data["default_repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))

            connection.execute("".join(query_statements))

        repo_count = None

        add_keys_to_test_db(test_db_engine)

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            controller.add_cli_org(data["org_name"])

            attempts = 0
            while attempts < 10:
                result = hit_api(
                    session.oauths, f"https://api.github.com/orgs/{data['org_name']}/repos?per_page=100", logger)

                # if result is None try again
                if not result:
                    attempts += 1
                    continue

                response = result.json()

                if response:
                    repo_count = len(response)
                    break

        with test_db_engine.connect() as connection:

            query = s.text(
                """SELECT * FROM "augur_data"."repo";""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) == repo_count

            user_repo_query = s.text(
                """SELECT * FROM "augur_operations"."user_repos";""")

            user_repo_result = connection.execute(
                user_repo_query, **data).fetchall()

            assert user_repo_result is not None
            assert len(user_repo_result) == repo_count

    finally:

        with test_db_engine.connect() as connection:

            connection.execute("""
                                DELETE FROM "augur_operations"."user_repos";
                                DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                DELETE FROM "augur_operations"."users" WHERE user_id=1;
                                """)


def test_add_cli_repos_with_duplicates(test_db_engine):

    try:
        with test_db_engine.connect() as connection:

            url = "https://github.com/operate-first/operate-first-twitter"

            data = {"user_id": 1, "default_repo_group_id": 1}


            query_statements = []
            query_statements.append(get_repo_delete_statement())
            query_statements.append(get_repo_group_delete_statement())
            query_statements.append(get_repo_group_insert_statement(data["default_repo_group_id"]))
            query_statements.append(get_user_insert_statement(data["user_id"]))

            connection.execute("".join(query_statements))

        add_keys_to_test_db(test_db_engine)

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            repo_data = {"url": url,
                         "repo_group_id": data["default_repo_group_id"]}
            controller.add_cli_repo(repo_data)
            controller.add_cli_repo(repo_data)

        with test_db_engine.connect() as connection:

            query = s.text(
                """SELECT * FROM "augur_data"."repo";""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) == 1

            assert dict(result[0])["repo_git"] == url

    finally:
        with test_db_engine.connect() as connection:

            connection.execute("""
                                DELETE FROM "augur_operations"."user_repos";
                                DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                DELETE FROM "augur_operations"."users";
                                """)


