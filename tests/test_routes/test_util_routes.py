#SPDX-License-Identifier: MIT
import requests
import pytest
import re

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

util_routes = [\
"repos",\
"repo-groups",\
"repo-groups/<default_repo_group_id>/repos",\
"dosocs/repos",\
"repo-groups/<default_repo_group_id>/aggregate-summary",\
"repo-groups/<default_repo_group_id>/repos/<default_repo_id>/aggregate-summary",\
]

@pytest.mark.parametrize("endpoint", create_full_routes(util_routes))
def test_base_test(client, endpoint):
    response = client.get(endpoint)
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) >= 1
