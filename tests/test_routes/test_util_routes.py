#SPDX-License-Identifier: MIT
import requests
import pytest

from conftest import create_full_routes

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
