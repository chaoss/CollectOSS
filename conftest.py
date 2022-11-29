#SPDX-License-Identifier: MIT
import pytest
import re
import logging
import sqlalchemy as s

from augur.application.db.session import DatabaseSession
from augur.application.config import AugurConfig
from augur.application.db.engine import get_database_string

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
