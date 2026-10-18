# SPDX-License-Identifier: MIT
import pytest
from unittest.mock import Mock, patch

from collectoss.tasks.github.util.github_data_access import (
    GithubDataAccess,
    ResourceUnprocessable,
)
from collectoss.tasks.github.facade_github.contributor_interfaceable.contributor_interface import (
    get_login_with_commit_hash,
)

@pytest.fixture
def mock_logger():
    return Mock()


@pytest.fixture
def mock_key_manager():
    return Mock()


@pytest.fixture
def gda(mock_key_manager, mock_logger):
    with patch("collectoss.tasks.github.util.github_data_access.KeyClient"):
        return GithubDataAccess(mock_key_manager, mock_logger)

@pytest.mark.unit
class TestEndpointUrl:

    def test_basic_path(self, gda):
        result = gda.endpoint_url("/users/MoralCode")
        assert result == "https://api.github.com/users/MoralCode"

    def test_path_without_leading_slash(self, gda):
        result = gda.endpoint_url("repos/owner/repo")
        assert result == "https://api.github.com/repos/owner/repo"

    def test_with_single_param(self, gda):
        result = gda.endpoint_url("/users/MoralCode", {"per_page": "100"})
        assert "per_page=100" in result
        assert result.startswith("https://api.github.com/users/MoralCode")

    def test_with_multiple_params(self, gda):
        result = gda.endpoint_url("/repos/owner/repo/pulls", {"per_page": "50", "state": "open"})
        assert "per_page=50" in result
        assert "state=open" in result
        assert result.startswith("https://api.github.com/repos/owner/repo/pulls")

    def test_none_params_produces_no_query_string(self, gda):
        result = gda.endpoint_url("/users/MoralCode", None)
        assert result == "https://api.github.com/users/MoralCode"

    def test_empty_params_produces_no_query_string(self, gda):
        result = gda.endpoint_url("/users/MoralCode", {})
        assert result == "https://api.github.com/users/MoralCode"

    def test_path_with_existing_query_params(self, gda):
        result = gda.endpoint_url("/search/repositories?q=python", {"per_page": "10"})
        assert "q=python" in result
        assert "per_page=10" in result
        assert result.startswith("https://api.github.com/search/repositories")

@pytest.mark.unit
class TestResponseErrors:

    def test_422_response_is_not_retried(self):
        exception = ResourceUnprocessable(
            "GitHub returned HTTP 422"
        )

        assert not GithubDataAccess._decide_retry_policy(exception)
def test_422_commit_lookup_raises_resource_unprocessable():
    logger = Mock()
    auth = Mock()
    commit_data = {"hash": "1f5270431bc8556cf6dfee1905e07abcc45e20d2"}

    error = ResourceUnprocessable(
        "GitHub returned HTTP 422"
    )

    with patch(
        "collectoss.tasks.github.facade_github.contributor_interfaceable.contributor_interface.create_endpoint_from_commit_sha",
        return_value="https://api.github.com/repos/Azure/Avere/commits/test",
    ), patch(
        "collectoss.tasks.github.facade_github.contributor_interfaceable.contributor_interface.GithubDataAccess"
    ) as mock_gda:
        mock_gda.return_value.get_resource.side_effect = error

        with pytest.raises(ResourceUnprocessable):
            get_login_with_commit_hash(
                logger, auth, commit_data, repo_id=1
            )

