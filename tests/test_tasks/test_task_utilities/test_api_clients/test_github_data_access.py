# SPDX-License-Identifier: MIT
import pytest
from unittest.mock import Mock, patch

from collectoss.tasks.github.util.github_data_access import GithubDataAccess


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
