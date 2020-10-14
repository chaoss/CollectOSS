#SPDX-License-Identifier: MIT
import pytest
import re

from augur.application import Application
from augur.cli.backend import initialize_components

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

@pytest.fixture(scope="session")
def augur_app():
    augur_app = Application(disable_logs=True)
    return augur_app

@pytest.fixture(scope="session")
def metrics(augur_app):
    return augur_app.metrics

@pytest.fixture(scope="session")
def client(augur_app):
    flask_client = initialize_components(augur_app, disable_housekeeper=True).load()
    return flask_client.test_client()
