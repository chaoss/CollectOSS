#SPDX-License-Identifier: MIT

import pytest

@pytest.fixture(scope="module")
def metrics():
    import augur
    augur_app = augur.Application()
    return augur_app.metrics

# def test_get_repos_for_dosocs(metrics):
#     assert metrics.get_repos_for_dosocs().isin(
#         ['/home/sean/git-repos/23/github.com/rails/rails-dom-testing']).any().any()

