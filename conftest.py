#SPDX-License-Identifier: MIT
import pytest
import re
import logging
import sqlalchemy as s
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import uuid
from sqlalchemy.pool import StaticPool


from augur.application.db.session import DatabaseSession
from augur.application.config import AugurConfig
from augur.application.db.engine import get_database_string, create_database_engine, parse_database_string, execute_sql_file


logger = logging.getLogger(__name__)

default_repo_id = "25430"
default_repo_group_id = "10"

def create_full_routes(routes):
    full_routes = []
    for route in routes:
        route = re.sub("<default_repo_id>", default_repo_id, route)
        route = re.sub("<default_repo_group_id>", default_repo_group_id, route)
        route = "http://localhost:5000/api/unstable/" + route
        full_routes.append(route)
    return full_routes

@pytest.fixture
def database():

    db_string = get_database_string()

    user, password, host, port, _ = parse_database_string(db_string)

    # Connect to the default 'postgres' database
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname='postgres'
    )

    # Set the isolation level to AUTOCOMMIT because CREATE DATABASE 
    # cannot be executed in a transaction block
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    test_db_name = "test_db_" + uuid.uuid4().hex

    # remove database_name and add test_db_name
    test_db_string = db_string[:db_string.rfind("/")+1] + test_db_name
    
    # create the temporary database
    cursor.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(test_db_name)))

    # Commit changes
    conn.commit()

    # Install schema
    execute_sql_file("tests/entire_db.sql", test_db_name, user, password, host, port)

    # create engine to connect to db
    engine = create_database_engine(test_db_string, poolclass=StaticPool)

    yield engine

    # dispose engine
    engine.dispose()

    # ensure connections are removed
    cursor.execute(sql.SQL("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{}';".format(test_db_name)))

    # drop temporary database
    cursor.execute(sql.SQL("DROP DATABASE {};").format(sql.Identifier(test_db_name)))

    # Close the cursor and the connection
    cursor.close()
    conn.close()


@pytest.fixture
def test_db_engine():

    # creates database engine the normal way and then gets the database string
    db_string = get_database_string()

    db_string_without_db_name = re.search(r"(.+:\/\/.+\/).+", db_string).groups()[0]

    testing_db_string = db_string_without_db_name + "augur-test"

    yield s.create_engine(testing_db_string)

@pytest.fixture
def test_db_session(test_db_engine):
    session = DatabaseSession(logger, test_db_engine)

    yield session

    session.close()

@pytest.fixture
def test_db_config(test_db_session):
    return AugurConfig(logger, test_db_session)


# @pytest.fixture(scope="session")
# def augur_app():
#     augur_app = Application(disable_logs=True)
#     return augur_app

# @pytest.fixture(scope="session")
# def metrics(augur_app):
#     return augur_app.metrics

# @pytest.fixture(scope="session")
# def client(augur_app):
#     flask_client = initialize_components(augur_app, disable_housekeeper=True).load()
#     return flask_client.test_client()
