import logging
import pytest
import uuid
import sqlalchemy as s


from augur.application.cli._repo_load_controller import RepoLoadController

from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Contributor, Issue

logger = logging.getLogger(__name__)


def test_is_valid_repo(engine):

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

def test_get_repo_id(engine):

    with engine.connect() as connection:

        query = s.text("""DELETE FROM "augur_data"."repo";
                          DELETE FROM "augur_data"."repo_groups";
                          INSERT INTO "augur_data"."repo_groups" ("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (1, 'Default Repo Group', 'The default repo group created by the schema generation script', '', 0, '2019-06-03 15:55:20', 'GitHub Organization', 'load', 'one', 'git', '2019-06-05 13:36:25');
                          INSERT INTO "augur_data"."repo_groups" ("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (-1, 'User Repo Group', 'The default repo group created by the schema generation script', '', 0, '2019-06-03 15:55:20', 'GitHub Organization', 'load', 'one', 'git', '2019-06-05 13:36:25');
                          INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "repo_archived_date_collected", "repo_archived", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (1, -1, 'https://github.com/18f/procurement-glossary', NULL, NULL, '2022-08-15 21:08:07', 'Complete', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2022-08-15 21:08:07');
                          INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "repo_archived_date_collected", "repo_archived", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (2, 1, 'https://github.com/chaoss/augur', NULL, NULL, '2022-08-15 21:08:07', 'Complete', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2022-08-15 21:08:07');""")
                          
        connection.execute(query)   

    with DatabaseSession(logger, engine) as session:

        controller = RepoLoadController(session)

        assert controller.get_repo_id("") is None
        assert controller.get_repo_id("chaoss/augur") is None

        # test with valid repo
        assert controller.get_repo_id("https://github.com/18f/procurement-glossary") == 1

        # test with repo that is present but isn't apart of the user repos
        assert controller.get_repo_id("https://github.com/choass/augur") is None


def test_add_repo_row(engine):

    try:

        with engine.connect() as connection:

            query = s.text("""DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                INSERT INTO "augur_data"."repo_groups" ("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (1, 'Default Repo Group', 'The default repo group created by the schema generation script', '', 0, '2019-06-03 15:55:20', 'GitHub Organization', 'load', 'one', 'git', '2019-06-05 13:36:25');
                                INSERT INTO "augur_data"."repo_groups" ("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (-1, 'User Repo Group', 'The default repo group created by the schema generation script', '', 0, '2019-06-03 15:55:20', 'GitHub Organization', 'load', 'one', 'git', '2019-06-05 13:36:25');
                                INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "repo_archived_date_collected", "repo_archived", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (1, 1, 'https://github.com/chaoss/augur', NULL, NULL, '2022-08-15 21:08:07', 'Complete', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2022-08-15 21:08:07');""")

            connection.execute(query)

        with DatabaseSession(logger, engine) as session:

            controller = RepoLoadController(session)

            controller.add_repo_row("https://github.com/chaoss/augur")

        with engine.connect() as connection:

            data = {"rg_id": -1, "repo_id": 1}

            query = s.text(
                """SELECT * FROM "augur_data"."repo" WHERE "repo_group_id"=:rg_id AND "repo_git"='https://github.com/chaoss/augur';""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) > 0

    finally:
        
        with engine.connect() as connection:

            connection.execute("""DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";""")


def test_add_repo_to_user(engine):

    try:

        with engine.connect() as connection:

            data = {"repo_id": 1, "user_id": 1, "user_repo_group_id": -1}

            query = s.text("""DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                INSERT INTO "augur_data"."repo_groups" ("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (:user_repo_group_id, 'User Repo Group', 'The default repo group created by the schema generation script', '', 0, '2019-06-03 15:55:20', 'GitHub Organization', 'load', 'one', 'git', '2019-06-05 13:36:25');
                                INSERT INTO "augur_data"."repo" ("repo_id", "repo_group_id", "repo_git", "repo_path", "repo_name", "repo_added", "repo_status", "repo_type", "url", "owner_id", "description", "primary_language", "created_at", "forked_from", "updated_at", "repo_archived_date_collected", "repo_archived", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (:repo_id, :user_repo_group_id, 'https://github.com/chaoss/augur', NULL, NULL, '2022-08-15 21:08:07', 'Complete', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CLI', '1.0', 'Git', '2022-08-15 21:08:07');
                                INSERT INTO "augur_operations"."users" ("user_id", "login_name", "login_hashword", "email", "first_name", "last_name", "admin") VALUES (:user_id, 'bil', 'pass', 'b@gmil.com', 'bill', 'bob', false);""")

            connection.execute(query, **data)

        with DatabaseSession(logger, engine) as session:

            controller = RepoLoadController(session)

            controller.add_repo_to_user(data["user_id"], data["repo_id"])

        with engine.connect() as connection:

            query = s.text("""SELECT * FROM "augur_operations"."user_repos" WHERE "user_id"=:user_id AND "repo_id"=:repo_id""")

            result = connection.execute(query, **data).fetchall()

            assert result is not None
            assert len(result) > 0

    finally:

        with engine.connect() as connection:

            connection.execute("""DELETE FROM "augur_data"."repo";
                                DELETE FROM "augur_data"."repo_groups";
                                DELETE FROM "augur_operations"."users";
                                DELETE FROM "augur_operations"."user_repos";""")








    


    
