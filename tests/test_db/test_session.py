import logging
import pytest
import uuid
import sqlalchemy as s

from augur.application.db.session import DatabaseSession
from augur.application.db.models import Contributor

logger = logging.getLogger(__name__)
not_provided_cntrb_id = '00000000-0000-0000-0000-000000000000'
nan_cntrb_id = '01000000-0000-0000-0000-000000000000'




def test_execute_sql(engine):

    data_1 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "bob", "cntrb_id": "01003f7a-8500-0000-0000-000000000000"}
    data_2 = {"cntrb_login": "amazing", "gh_user_id": 1700, "gh_login": "hello", "cntrb_id": "01003f7a-8500-0000-0000-000123002000"}
    data_3 = {"cntrb_login": "cool_guy", "gh_user_id": 230, "gh_login": "lame_guy", "cntrb_id": "01003f7a-8511-0000-0000-000123875000"}
    data_4 = {"cntrb_login": "great", "gh_user_id": 230, "gh_login": "boring", "cntrb_id": "01003f7a-8511-0000-0000-000123000000"}
    all_data = [data_1, data_2, data_3, data_4]

    try:

        session = DatabaseSession(logger, engine=engine)

        with engine.connect() as connection:

            for data in all_data:

                statement = s.sql.text("""INSERT INTO "augur_data"."contributors" ("cntrb_login", "cntrb_email", "cntrb_full_name", "cntrb_company", "cntrb_created_at", "cntrb_type", "cntrb_fake", "cntrb_deleted", "cntrb_long", "cntrb_lat", "cntrb_country_code", "cntrb_state", "cntrb_city", "cntrb_location", "cntrb_canonical", "cntrb_last_used", "gh_user_id", "gh_login", "gh_url", "gh_html_url", "gh_node_id", "gh_avatar_url", "gh_gravatar_id", "gh_followers_url", "gh_following_url", "gh_gists_url", "gh_starred_url", "gh_subscriptions_url", "gh_organizations_url", "gh_repos_url", "gh_events_url", "gh_received_events_url", "gh_type", "gh_site_admin", "gl_web_url", "gl_avatar_url", "gl_state", "gl_username", "gl_full_name", "gl_id", "tool_source", "tool_version", "data_source", "data_collection_date", "cntrb_id") VALUES (:cntrb_login, NULL, NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, :gh_user_id, :gh_login, 'https://api.github.com/users/ivanayov', 'https://github.com/ivanayov', 'MDQ6VXNlcjQxNjAxMzM=', 'https://avatars.githubusercontent.com/u/4160133?v=4', '', 'https://api.github.com/users/ivanayov/followers', 'https://api.github.com/users/ivanayov/following{/other_user}', 'https://api.github.com/users/ivanayov/gists{/gist_id}', 'https://api.github.com/users/ivanayov/starred{/owner}{/repo}', 'https://api.github.com/users/ivanayov/subscriptions', 'https://api.github.com/users/ivanayov/orgs', 'https://api.github.com/users/ivanayov/repos', 'https://api.github.com/users/ivanayov/events{/privacy}', 'https://api.github.com/users/ivanayov/received_events', 'User', 'false', NULL, NULL, NULL, NULL, NULL, NULL, 'Pr Task', '2.0', 'Github API', '2022-08-05 09:06:39', :cntrb_id);""")

                connection.execute(statement, **data)

        for data in all_data:

            cntrb_id = data['cntrb_id']
            result = session.execute_sql(f"SELECT * FROM augur_data.contributors WHERE cntrb_id='{cntrb_id}'").fetchall()

            assert result is not None
            assert isinstance(result[0], s.engine.result.RowProxy)

            result_dict = dict(result[0])

            for key in data.keys():

                if key == 'cntrb_id':
                    assert result_dict[key] == uuid.UUID(data[key])
                    continue

                assert result_dict[key] == data[key]

    finally:

        with engine.connect() as connection:

            for data in all_data:

                cntrb_id = data["cntrb_id"]
                connection.execute(f"DELETE FROM augur_data.contributors WHERE cntrb_id='{cntrb_id}';")


def test_insert_data_with_duplicates(engine):

    data_1 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "bob", "cntrb_id": "01003f7a-8500-0000-0000-000000000000"}
    data_2 = {"cntrb_login": "amazing", "gh_user_id": 1700, "gh_login": "hello", "cntrb_id": "01003f7a-8500-0000-0000-000123002000"}
    data_3 = {"cntrb_login": "cool_guy", "gh_user_id": 230, "gh_login": "lame_guy", "cntrb_id": "01003f7a-8511-0000-0000-000123875000"}

    duplicate_data_list = [data_1, data_1, data_2, data_2, data_3]

    try:

        session = DatabaseSession(logger, engine=engine)

        for data in duplicate_data_list:

            session.insert_data(data, Contributor, ["cntrb_login"])


        
        cntrb_id = data_1['cntrb_id']
        result = session.execute_sql(f"SELECT * FROM augur_data.contributors WHERE cntrb_id!='{not_provided_cntrb_id}' AND cntrb_id!='{nan_cntrb_id}'").fetchall()

        assert result is not None
        assert len(result) == 3

        for row in result:
            assert isinstance(row, s.engine.result.RowProxy)
    
    finally:

        with engine.connect() as connection:

            for data in duplicate_data_list:

                cntrb_id = data["cntrb_id"]
                connection.execute(f"DELETE FROM augur_data.contributors WHERE cntrb_id='{cntrb_id}';")

def test_insert_data_with_updates(engine):

    data_1 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "bob", "cntrb_id": "01003f7a-8500-0000-0000-000000000000"}
    data_2 = data_1.copy()
    data_2["gh_user_id"] = 6
    
    try:

        with engine.connect() as connection:

            statement = s.sql.text("""INSERT INTO "augur_data"."contributors" ("cntrb_login", "cntrb_email", "cntrb_full_name", "cntrb_company", "cntrb_created_at", "cntrb_type", "cntrb_fake", "cntrb_deleted", "cntrb_long", "cntrb_lat", "cntrb_country_code", "cntrb_state", "cntrb_city", "cntrb_location", "cntrb_canonical", "cntrb_last_used", "gh_user_id", "gh_login", "gh_url", "gh_html_url", "gh_node_id", "gh_avatar_url", "gh_gravatar_id", "gh_followers_url", "gh_following_url", "gh_gists_url", "gh_starred_url", "gh_subscriptions_url", "gh_organizations_url", "gh_repos_url", "gh_events_url", "gh_received_events_url", "gh_type", "gh_site_admin", "gl_web_url", "gl_avatar_url", "gl_state", "gl_username", "gl_full_name", "gl_id", "tool_source", "tool_version", "data_source", "data_collection_date", "cntrb_id") VALUES (:cntrb_login, NULL, NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, :gh_user_id, :gh_login, 'https://api.github.com/users/ivanayov', 'https://github.com/ivanayov', 'MDQ6VXNlcjQxNjAxMzM=', 'https://avatars.githubusercontent.com/u/4160133?v=4', '', 'https://api.github.com/users/ivanayov/followers', 'https://api.github.com/users/ivanayov/following{/other_user}', 'https://api.github.com/users/ivanayov/gists{/gist_id}', 'https://api.github.com/users/ivanayov/starred{/owner}{/repo}', 'https://api.github.com/users/ivanayov/subscriptions', 'https://api.github.com/users/ivanayov/orgs', 'https://api.github.com/users/ivanayov/repos', 'https://api.github.com/users/ivanayov/events{/privacy}', 'https://api.github.com/users/ivanayov/received_events', 'User', 'false', NULL, NULL, NULL, NULL, NULL, NULL, 'Pr Task', '2.0', 'Github API', '2022-08-05 09:06:39', :cntrb_id);""")

            connection.execute(statement, **data_1)

        session = DatabaseSession(logger, engine=engine)

        session.insert_data(data_2, Contributor, ["cntrb_login"])

        with engine.connect() as connection:

            cntrb_id = data_1['cntrb_id']
            result = connection.execute(f"SELECT * FROM augur_data.contributors WHERE cntrb_id='{cntrb_id}'").fetchall()

        assert result is not None
        assert dict(result[0])["gh_user_id"] == 6 
    
    finally:

        with engine.connect() as connection:

            cntrb_id = data_1["cntrb_id"]
            connection.execute(f"DELETE FROM augur_data.contributors WHERE cntrb_id='{cntrb_id}';")


def test_insert_data_with_bulk(engine):

    data_1 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "bob", "cntrb_id": "01003f7a-8500-0000-0000-000000000000"}
    data_2 = {"cntrb_login": "amazing", "gh_user_id": 1700, "gh_login": "hello", "cntrb_id": "01003f7a-8500-0000-0000-000123002000"}
    data_3 = {"cntrb_login": "cool_guy", "gh_user_id": 230, "gh_login": "lame_guy", "cntrb_id": "01003f7a-8511-0000-0000-000123875000"}
    data_4 = {"cntrb_login": "great", "gh_user_id": 230, "gh_login": "boring", "cntrb_id": "01003f7a-8511-0000-0000-000123000000"}
    all_data = [data_1, data_2, data_3, data_4]


    try:
        session = DatabaseSession(logger, engine=engine)
        session.insert_data(all_data, Contributor, ["cntrb_login"])

        with engine.connect() as connection:

            result = session.execute_sql(f"SELECT * FROM augur_data.contributors WHERE cntrb_id!='{not_provided_cntrb_id}' AND cntrb_id!='{nan_cntrb_id}'").fetchall()

            assert result is not None
            assert len(result) == 4

            for data in result:
                dict_data = dict(data)

                for key in dict_data.keys():
                    assert data[key] == dict_data[key]
    finally:

        with engine.connect() as connection:

            cntrb_id = data_1["cntrb_id"]
            connection.execute(f"DELETE FROM augur_data.contributors WHERE cntrb_id!='{not_provided_cntrb_id}' AND cntrb_id!='{nan_cntrb_id}';")



def test_insert_data_partial_update(engine):

    data_1 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "bob", "cntrb_id": "01003f7a-8500-0000-0000-000000000000"}
    data_2 = {"cntrb_login": "Bob", "gh_user_id": 6, "cntrb_id": "01003f7a-8500-0000-0000-000000000000"}
    
    try:
        with engine.connect() as connection:

            statement = s.sql.text("""INSERT INTO "augur_data"."contributors" ("cntrb_login", "cntrb_email", "cntrb_full_name", "cntrb_company", "cntrb_created_at", "cntrb_type", "cntrb_fake", "cntrb_deleted", "cntrb_long", "cntrb_lat", "cntrb_country_code", "cntrb_state", "cntrb_city", "cntrb_location", "cntrb_canonical", "cntrb_last_used", "gh_user_id", "gh_login", "gh_url", "gh_html_url", "gh_node_id", "gh_avatar_url", "gh_gravatar_id", "gh_followers_url", "gh_following_url", "gh_gists_url", "gh_starred_url", "gh_subscriptions_url", "gh_organizations_url", "gh_repos_url", "gh_events_url", "gh_received_events_url", "gh_type", "gh_site_admin", "gl_web_url", "gl_avatar_url", "gl_state", "gl_username", "gl_full_name", "gl_id", "tool_source", "tool_version", "data_source", "data_collection_date", "cntrb_id") VALUES (:cntrb_login, NULL, NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, :gh_user_id, :gh_login, 'https://api.github.com/users/ivanayov', 'https://github.com/ivanayov', 'MDQ6VXNlcjQxNjAxMzM=', 'https://avatars.githubusercontent.com/u/4160133?v=4', '', 'https://api.github.com/users/ivanayov/followers', 'https://api.github.com/users/ivanayov/following{/other_user}', 'https://api.github.com/users/ivanayov/gists{/gist_id}', 'https://api.github.com/users/ivanayov/starred{/owner}{/repo}', 'https://api.github.com/users/ivanayov/subscriptions', 'https://api.github.com/users/ivanayov/orgs', 'https://api.github.com/users/ivanayov/repos', 'https://api.github.com/users/ivanayov/events{/privacy}', 'https://api.github.com/users/ivanayov/received_events', 'User', 'false', NULL, NULL, NULL, NULL, NULL, NULL, 'Pr Task', '2.0', 'Github API', '2022-08-05 09:06:39', :cntrb_id);""")

            connection.execute(statement, **data_1)

        session = DatabaseSession(logger, engine=engine)

        session.insert_data(data_2, Contributor, ["cntrb_login"])

        with engine.connect() as connection:

            cntrb_id = data_1['cntrb_id']
            result = connection.execute(f"SELECT * FROM augur_data.contributors WHERE cntrb_id='{cntrb_id}'").fetchall()

        assert result is not None
        assert dict(result[0])["gh_user_id"] == 6 
    
    finally:

        with engine.connect() as connection:

            cntrb_id = data_1["cntrb_id"]
            connection.execute(f"DELETE FROM augur_data.contributors WHERE cntrb_id='{cntrb_id}';")



