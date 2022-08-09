import pytest
import logging
import httpx

from augur.tasks.github.util.github_paginator import GithubPaginator
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.tasks.util.random_key_auth import RandomKeyAuth
from augur.application.db.session import DatabaseSession

logger = logging.getLogger(__name__)


@pytest.fixture
def key_auth():
    
    session = DatabaseSession(logger)

    key_auth =  GithubRandomKeyAuth(session)

    yield key_auth

def test_github_paginator_get_item(key_auth):

    first_augur_pr_id = 102777299

    url = "https://api.github.com/repos/chaoss/augur/pulls?state=all&direction=asc&per_page=100"

    prs = GithubPaginator(url, key_auth, logger)

    assert prs is not None
    assert prs[0] is not None

    assert first_augur_pr_id == prs[0]["id"]


def test_github_paginator_retrieve_data_valid_url(key_auth):

    url = "https://api.github.com/repos/chaoss/augur/pulls?state=all&direction=asc&per_page=100"

    prs, response = GithubPaginator(url, key_auth, logger).retrieve_data(url)

    assert prs is not None
    assert response is not None

    assert type(prs) == list
    assert len(prs) == 100
    assert response.status_code == 200

def test_github_paginator_retrieve_data_bad_url(key_auth):

    url = "https://api.github.com/repos/chaoss/whitepaper/pulls?state=all&direction=asc&per_page=100"

    prs, response = GithubPaginator(url, key_auth, logger).retrieve_data(url)

    assert prs == None
    assert response == None


def test_github_paginator_hit_api(key_auth):


    url = "https://api.github.com/repos/chaoss/whitepaper/pulls?state=all&direction=asc&per_page=100"

    response = GithubPaginator(url, key_auth, logger).hit_api(url, timeout=10)

    assert isinstance(response, httpx.Response)
    assert response.status_code == 404

def test_github_paginator_hit_api_timeout(key_auth):

    url = "https://api.github.com/repos/chaoss/whitepaper/pulls?state=all&direction=asc&per_page=100"

    response = GithubPaginator(url, key_auth, logger).hit_api(url, timeout=0.001)

    assert response == None

