import logging
import pytest
import sqlalchemy as s


from augur.util.repo_load_controller import RepoLoadController, DEFAULT_REPO_GROUP_IDS, CLI_USER_ID

from augur.application.db.session import DatabaseSession
from augur.tasks.github.util.github_task_session import GithubTaskSession
from tests.test_applicaton.test_repo_load_controller.helper import *

logger = logging.getLogger(__name__)


def test_parse_repo_url():

    with DatabaseSession(logger) as session:

        controller = RepoLoadController(session)

        assert controller.parse_repo_url("hello world") == (None, None)
        assert controller.parse_repo_url("https://github.com/chaoss/hello") == ("chaoss", "hello")
        assert controller.parse_repo_url("https://github.com/hello124/augur") == ("hello124", "augur")
        assert controller.parse_repo_url("https://github.com//augur") == (None, None)
        assert controller.parse_repo_url("https://github.com/chaoss/") == (None, None)
        assert controller.parse_repo_url("https://github.com//") == (None, None)
        assert controller.parse_repo_url("https://github.com/chaoss/augur") == ("chaoss", "augur")
        assert controller.parse_repo_url("https://github.com/chaoss/augur/") == ("chaoss", "augur")
        assert controller.parse_repo_url("https://github.com/chaoss/augur.git") == ("chaoss", "augur")


def test_parse_org_url():

    with DatabaseSession(logger) as session:

        controller = RepoLoadController(session)

        assert controller.parse_org_url("hello world") == None, None
        assert controller.parse_org_url("https://github.com/chaoss/") == "chaoss"
        assert controller.parse_org_url("https://github.com/chaoss") == "chaoss"
        assert controller.parse_org_url("https://github.com/hello124/augur") == None
        assert controller.parse_org_url("https://github.com//augur") == None, None
        assert controller.parse_org_url("https://github.com//") == None
        assert controller.parse_org_url("https://github.com/chaoss/augur") == None


def test_is_valid_repo():

    with GithubTaskSession(logger) as session:

        controller = RepoLoadController(session)

        assert controller.is_valid_repo("hello world") is False
        assert controller.is_valid_repo("https://github.com/chaoss/hello") is False
        assert controller.is_valid_repo("https://github.com/hello124/augur") is False
        assert controller.is_valid_repo("https://github.com//augur") is False
        assert controller.is_valid_repo("https://github.com/chaoss/") is False
        assert controller.is_valid_repo("https://github.com//") is False
        assert controller.is_valid_repo("https://github.com/chaoss/augur") is True
        assert controller.is_valid_repo("https://github.com/chaoss/augur/") is True
        assert controller.is_valid_repo("https://github.com/chaoss/augur.git") is True
        assert controller.is_valid_repo("https://github.com/chaoss/augur/") is True

def test_is_valid_repo_group_id(test_db_engine):

    clear_tables = ["repo_groups"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:


        data = {"rg_ids": [1, 2, 3], "repo_id": 1, "tool_source": "Frontend",
                "repo_url": "https://github.com/chaoss/augur"}

        with test_db_engine.connect() as connection:

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_repo_group_insert_statement(data["rg_ids"][0]))
            query_statements.append(get_repo_group_insert_statement(data["rg_ids"][1]))
            query_statements.append(get_repo_group_insert_statement(data["rg_ids"][2]))
            query = s.text("".join(query_statements))

            connection.execute(query)

        with DatabaseSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            # valid 
            assert controller.is_valid_repo_group_id(data["rg_ids"][0]) is True
            assert controller.is_valid_repo_group_id(data["rg_ids"][1]) is True
            assert controller.is_valid_repo_group_id(data["rg_ids"][2]) is True


            # invalid
            assert controller.is_valid_repo_group_id(-1) is False
            assert controller.is_valid_repo_group_id(12) is False
            assert controller.is_valid_repo_group_id(11111) is False


    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)


def test_add_repo_row(test_db_engine):

    clear_tables = ["repo", "repo_groups"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        data = {"rg_id": 1, 
                "tool_source": "Frontend",
                "repo_urls": ["https://github.com/chaoss/augur", "https://github.com/chaoss/grimoirelab-sortinghat"]
                }

        with test_db_engine.connect() as connection:

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_repo_group_insert_statement(data["rg_id"]))
            query = s.text("".join(query_statements))

            connection.execute(query)

        with DatabaseSession(logger, test_db_engine) as session:

            assert RepoLoadController(session).add_repo_row(data["repo_urls"][0], data["rg_id"], data["tool_source"]) is not None
            assert RepoLoadController(session).add_repo_row(data["repo_urls"][1], data["rg_id"], data["tool_source"]) is not None

            # invalid rg_id
            assert RepoLoadController(session).add_repo_row(data["repo_urls"][0], 12, data["tool_source"]) is None

            # invalid type for repo url
            assert RepoLoadController(session).add_repo_row(1, data["rg_id"], data["tool_source"]) is None

            # invalid type for rg_id
            assert RepoLoadController(session).add_repo_row(data["repo_urls"][1], "1", data["tool_source"]) is None

            # invalid type for tool_source
            assert RepoLoadController(session).add_repo_row(data["repo_urls"][1], data["rg_id"], 52) is None

        with test_db_engine.connect() as connection:

            result = get_repos(connection)
            assert result is not None
            assert len(result) == len(data["repo_urls"])

    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)


def test_add_repo_row_with_updates(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        data = {"old_rg_id": 1, "new_rg_id": 2, "repo_id": 1, "repo_id_2": 2, "tool_source": "Test",
                "repo_url": "https://github.com/chaoss/augur", "repo_url_2": "https://github.com/chaoss/grimoirelab-perceval-opnfv",  "repo_status": "Complete"}

        with test_db_engine.connect() as connection:

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_repo_group_insert_statement(data["old_rg_id"]))
            query_statements.append(get_repo_group_insert_statement(data["new_rg_id"]))
            query_statements.append(get_repo_insert_statement(data["repo_id"], data["old_rg_id"], repo_url=data["repo_url"], repo_status=data["repo_status"]))
            query = s.text("".join(query_statements))

            connection.execute(query)

        with DatabaseSession(logger, test_db_engine) as session:

            result =  RepoLoadController(session).add_repo_row(data["repo_url"], data["new_rg_id"], data["tool_source"]) is not None
            assert result == data["repo_id"]

        with test_db_engine.connect() as connection:

            result = get_repos(connection, where_string=f"WHERE repo_git='{data['repo_url']}'")
            assert result is not None
            assert len(result) == 1

            value = dict(result[0])
            assert value["repo_status"] == data["repo_status"]
            assert value["repo_group_id"] == data["new_rg_id"]

    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)


def test_add_repo_to_user_group(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        with test_db_engine.connect() as connection:

            data = {"repo_ids": [1, 2, 3], "repo_urls":["url 1", "url2", "url3"], "user_id": 2, "user_repo_group_id": 1, "user_group_ids": [1, 2], "user_group_names": ["test_group", "test_group_2"]}

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_repo_group_insert_statement(data["user_repo_group_id"]))

            for i in range(0, len(data["repo_ids"])):
                query_statements.append(get_repo_insert_statement(data["repo_ids"][i], data["user_repo_group_id"], data["repo_urls"][i]))

            query_statements.append(get_user_insert_statement(data["user_id"]))

            for i in range(0, len(data["user_group_ids"])):
                query_statements.append(get_user_group_insert_statement(data["user_id"], data["user_group_names"][i], data["user_group_ids"][i]))
            
            query = s.text("".join(query_statements))

            connection.execute(query)

        with DatabaseSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            # add valid repo to group 0
            assert controller.add_repo_to_user_group(data["repo_ids"][0], data["user_group_ids"][0]) is True

            # add repo again to group 0 ... should be 1 repo row still
            assert controller.add_repo_to_user_group(data["repo_ids"][0], data["user_group_ids"][0]) is True

            # add another valid repo to group 0
            assert controller.add_repo_to_user_group(data["repo_ids"][1], data["user_group_ids"][0]) is True

            # add same repo to group 1
            assert controller.add_repo_to_user_group(data["repo_ids"][0], data["user_group_ids"][1]) is True

            # add different repo to group 1
            assert controller.add_repo_to_user_group(data["repo_ids"][2], data["user_group_ids"][1]) is True

            # add with invalid repo id
            assert controller.add_repo_to_user_group(130000, data["user_group_ids"][1]) is False

            # add with invalid group_id
            assert controller.add_repo_to_user_group(data["repo_ids"][0], 133333) is False

            # pass invalid tpyes
            assert controller.add_repo_to_user_group("130000", data["user_group_ids"][1]) is False
            assert controller.add_repo_to_user_group(data["repo_ids"][0], "133333") is False


            # end result
            # 4 rows in table
            # 2 rows in each group


        with test_db_engine.connect() as connection:

            query = s.text("""SELECT * FROM "augur_operations"."user_repos";""")
            # WHERE "group_id"=:user_group_id AND "repo_id"=:repo_id

            result = connection.execute(query).fetchall()
            assert result is not None
            assert len(result) == 4


            query = s.text("""SELECT * FROM "augur_operations"."user_repos" WHERE "group_id"={};""".format(data["user_group_ids"][0]))

            result = connection.execute(query).fetchall()
            assert result is not None
            assert len(result) == 2


            query = s.text("""SELECT * FROM "augur_operations"."user_repos" WHERE "group_id"={};""".format(data["user_group_ids"][0]))

            result = connection.execute(query).fetchall()
            assert result is not None
            assert len(result) == 2

    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)


def test_add_user_group(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        with test_db_engine.connect() as connection:

            data = {
                "users": [
                    {
                        "id": 0,
                        "username": "user 1",
                        "email": "email 1"
                    },
                    {
                        "id": 1,
                        "username": "user 2",
                        "email": "email 2"
                    }
                ],
                "group_names": ["test_group", "test_group_2"]}

            query_statements = []
            query_statements.append(clear_tables_statement)

            for user in data["users"]:
                query_statements.append(get_user_insert_statement(user["id"], user["username"], user["email"]))
            
            query = s.text("".join(query_statements))

            connection.execute(query)

        with DatabaseSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            # add valid group to user 0
            assert controller.add_user_group(data["users"][0]["id"], data["group_names"][0])["status"] == "Group created"

            # add group again to user 0 ... should be 1 group row still
            assert controller.add_user_group(data["users"][0]["id"], data["group_names"][0])["status"] == "Group created"

            # add another valid group to user 0
            assert controller.add_user_group(data["users"][0]["id"], data["group_names"][1])["status"] == "Group created"

            # add same group to user 1
            assert controller.add_user_group(data["users"][1]["id"], data["group_names"][0])["status"] == "Group created"


            # add with invalid user id
            assert controller.add_user_group(130000, data["group_names"][0])["status"] == "Error: User id does not exist"

            # pass invalid tpyes
            assert controller.add_user_group("130000", data["group_names"][0])["status"] == "Invalid input"
            assert controller.add_user_group(data["users"][0]["id"], 133333)["status"] == "Invalid input"


            # end result
            # 3 groups in table
            # 1 row for user 1
            # 2 rows for user 0


        with test_db_engine.connect() as connection:

            query = s.text("""SELECT * FROM "augur_operations"."user_groups";""")

            result = connection.execute(query).fetchall()
            assert result is not None
            assert len(result) == 3

            query = s.text("""SELECT * FROM "augur_operations"."user_groups" WHERE "user_id"={};""".format(data["users"][0]["id"]))

            result = connection.execute(query).fetchall()
            assert result is not None
            assert len(result) == 2

            query = s.text("""SELECT * FROM "augur_operations"."user_groups" WHERE "user_id"={};""".format(data["users"][1]["id"]))

            result = connection.execute(query).fetchall()
            assert result is not None
            assert len(result) == 1


    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)



def test_convert_group_name_to_id(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        with test_db_engine.connect() as connection:

            user_id =1

            groups = [
                {
                    "group_name": "test group 1",
                    "group_id": 1
                },
                {
                    "group_name": "test group 2",
                    "group_id": 2
                },
                {
                    "group_name": "test group 3",
                    "group_id": 3
                },
            ]

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_user_insert_statement(user_id))

            for group in groups:
                query_statements.append(get_user_group_insert_statement(user_id, group["group_name"], group["group_id"]))

            connection.execute("".join(query_statements))

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            for group in groups:
                assert controller.convert_group_name_to_id(user_id, group["group_name"]) == group["group_id"]

            # test invalid group name 
            assert controller.convert_group_name_to_id(user_id, "hello") is None

            # test invalid user id 
            assert controller.convert_group_name_to_id(user_id*2, groups[0]["group_name"]) is None

            # test invalid types
            assert controller.convert_group_name_to_id(user_id, 5) is None
            assert controller.convert_group_name_to_id("5", groups[0]["group_name"]) is None

    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)


def test_remove_user_group(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        with test_db_engine.connect() as connection:

            user_id =1
            repo_id = 1
            rg_id = 1

            groups = [
                {
                    "group_name": "test group 1",
                    "group_id": 1
                },
                {
                    "group_name": "test group 2",
                    "group_id": 2
                },
                {
                    "group_name": "test group 3",
                    "group_id": 3
                },
                {
                    "group_name": "test group 4",
                    "group_id": 4
                },
                {
                    "group_name": "test group 5",
                    "group_id": 5
                }
            ]

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_user_insert_statement(user_id))

            for group in groups:
                query_statements.append(get_user_group_insert_statement(user_id, group["group_name"], group["group_id"]))

            query_statements.append(get_repo_group_insert_statement(rg_id))
            query_statements.append(get_repo_insert_statement(repo_id, rg_id))
            query_statements.append(get_user_repo_insert_statement(repo_id, groups[0]["group_id"]))

            connection.execute("".join(query_statements))

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            assert controller.remove_user_group(user_id, "hello")["status"] == "WARNING: Trying to delete group that does not exist"

            i = 0
            while(i < len(groups)-2):
                assert controller.remove_user_group(user_id, groups[i]["group_name"])["status"] == "Group deleted"
                i += 1


            with test_db_engine.connect() as connection:

                query = s.text("""SELECT * FROM "augur_operations"."user_groups";""")

                result = connection.execute(query).fetchall()
                assert result is not None
                assert len(result) == len(groups)-i


            while(i < len(groups)):

                assert controller.remove_user_group(user_id, groups[i]["group_name"])["status"] == "Group deleted"
                i += 1

            with test_db_engine.connect() as connection:

                query = s.text("""SELECT * FROM "augur_operations"."user_groups";""")

                result = connection.execute(query).fetchall()
                assert result is not None
                assert len(result) == 0

    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)




def test_get_user_groups(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        with test_db_engine.connect() as connection:

            user_id_1 = 1
            user_id_2 = 2
            

            groups = [
                {
                    "group_name": "test group 1",
                    "group_id": 1
                },
                {
                    "group_name": "test group 2",
                    "group_id": 2
                },
                {
                    "group_name": "test group 3",
                    "group_id": 3
                },
                {
                    "group_name": "test group 4",
                    "group_id": 4
                },
                {
                    "group_name": "test group 5",
                    "group_id": 5
                }
            ]

            query_statements = []
            query_statements.append(clear_tables_statement)
            query_statements.append(get_user_insert_statement(user_id_1))

            # add user with no user groups
            query_statements.append(get_user_insert_statement(user_id_2, username="hello", email="hello@gmail.com"))

            for group in groups:
                query_statements.append(get_user_group_insert_statement(user_id_1, group["group_name"], group["group_id"]))

            connection.execute("".join(query_statements))

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            assert len(controller.get_user_groups(user_id_1)) == len(groups)

            assert len(controller.get_user_groups(user_id_2)) == 0


            with test_db_engine.connect() as connection:

                user_group_delete_statement = get_user_group_delete_statement()
                query = s.text(user_group_delete_statement)

                result = connection.execute(query)
 
    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)


def test_get_user_group_repos(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        with test_db_engine.connect() as connection:

            user_id =1
            user_id_2 = 2
            group_id = 1
            group_id_2 = 2
            rg_id = 1
            group_name = "test_group 1"
            repo_ids = [1, 2, 3, 4, 5]
            repo_urls = ["url1", "url2", "url3", "url4", "url5"]

            query_statements = []
            query_statements.append(clear_tables_statement)

            # add user with a group that has multiple repos
            query_statements.append(get_user_insert_statement(user_id))
            query_statements.append(get_user_group_insert_statement(user_id, group_name, group_id))

            # add user with a group that has no repos
            query_statements.append(get_user_insert_statement(user_id_2, username="hello", email="hello@gmail.com"))
            query_statements.append(get_user_group_insert_statement(user_id_2, group_name, group_id_2))

            query_statements.append(get_repo_group_insert_statement(rg_id))
            
            for i in range(0, len(repo_ids)):
                query_statements.append(get_repo_insert_statement(repo_ids[i], rg_id, repo_urls[i]))
                query_statements.append(get_user_repo_insert_statement(repo_ids[i], group_id))

            connection.execute("".join(query_statements))

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            result = controller.get_user_group_repos(group_id)

            assert len(result) == len(repo_ids)
            assert set([repo.repo_id for repo in result]) == set(repo_ids)

            result = controller.get_user_group_repos(group_id_2)

            assert len(result) == 0


            with test_db_engine.connect() as connection:

                user_repo_delete_statement = get_user_repo_delete_statement()
                query = s.text(user_repo_delete_statement)

                result = connection.execute(query)

            assert len(controller.get_user_group_repos(group_id)) == 0
 
    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)


def test_get_user_group_repos(test_db_engine):

    clear_tables = ["user_repos", "user_groups", "repo", "repo_groups", "users"]
    clear_tables_statement = get_repo_related_delete_statements(clear_tables)

    try:
        with test_db_engine.connect() as connection:

            user_id =1
            user_id_2 = 2
            group_id = 1
            group_id_2 = 2
            rg_id = 1
            group_name = "test_group 1"
            repo_ids = [1, 2, 3, 4, 5]
            repo_urls = ["url1", "url2", "url3", "url4", "url5"]

            query_statements = []
            query_statements.append(clear_tables_statement)

            # add user with a group that has multiple repos
            query_statements.append(get_user_insert_statement(user_id))
            query_statements.append(get_user_group_insert_statement(user_id, group_name, group_id))

            # add user with a group that has no repos
            query_statements.append(get_user_insert_statement(user_id_2, username="hello", email="hello@gmail.com"))

            query_statements.append(get_repo_group_insert_statement(rg_id))
            
            for i in range(0, len(repo_ids)):
                query_statements.append(get_repo_insert_statement(repo_ids[i], rg_id, repo_urls[i]))
                query_statements.append(get_user_repo_insert_statement(repo_ids[i], group_id))

            connection.execute("".join(query_statements))

        with GithubTaskSession(logger, test_db_engine) as session:

            controller = RepoLoadController(session)

            # test user with a group that has multiple repos
            result = controller.get_user_repo_ids(user_id)

            assert len(result) == len(repo_ids)
            assert set(result) == set(repo_ids)


            # test user without any groups or repos
            result = controller.get_user_repo_ids(user_id_2)

            assert len(result) == 0

            query_statements.append(get_user_group_insert_statement(user_id_2, group_name, group_id_2))


            # test user with a group that doesn't have any repos
            result = controller.get_user_repo_ids(user_id_2)

            assert len(result) == 0

            with test_db_engine.connect() as connection:

                user_repo_delete_statement = get_user_repo_delete_statement()
                query = s.text(user_repo_delete_statement)

                result = connection.execute(query)

            assert len(controller.get_user_group_repos(group_id)) == 0
 
    finally:
        with test_db_engine.connect() as connection:
            connection.execute(clear_tables_statement)




