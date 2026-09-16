# SPDX-License-Identifier: MIT
import pytest
from unittest.mock import Mock, patch

from collectoss.tasks.github.util.github_api_key_handler import GithubApiKeyHandler


github_whitespace_api_keys_list = ["", "    "]
github_none_api_key = None
github_valid_api_key = "ghp_1234567890abcdef1234567890abcdef12345678"

def build_handler(config_key, db_keys):
    logger = Mock()

    with patch("collectoss.tasks.github.util.github_api_key_handler.RedisList"), \
         patch.object(GithubApiKeyHandler, "get_config_key", return_value=config_key), \
         patch.object(GithubApiKeyHandler, "get_api_keys_from_database", return_value=db_keys), \
         patch.object(GithubApiKeyHandler, "is_bad_api_key", return_value=False) as probe:
        handler = GithubApiKeyHandler(logger)

    return handler, probe, logger

@pytest.mark.unit
class TestConfigKeys:

    @pytest.mark.parametrize("github_whitespace_api_key", github_whitespace_api_keys_list)
    def test_whitespace_config_key_with_no_db_keys(self, github_whitespace_api_key):
        db_keys = []
        handler, probe, logger = build_handler(github_whitespace_api_key, db_keys)

        assert handler.keys == []
        assert probe.call_count == 0
        logger.warning.assert_called_once()

    def test_none_config_key_with_no_db_keys(self):
        db_keys = []
        handler, probe, logger = build_handler(github_none_api_key, db_keys)

        assert handler.keys == []
        assert probe.call_count == 0
        logger.warning.assert_not_called()

    def test_valid_config_key_with_no_db_keys(self):
        db_keys = []
        handler, probe, logger = build_handler(github_valid_api_key, db_keys)

        assert handler.keys == [github_valid_api_key]
        assert probe.call_count == 1
        logger.warning.assert_not_called()

    @pytest.mark.parametrize("github_whitespace_api_key", github_whitespace_api_keys_list)
    def test_whitespace_config_key_with_db_keys(self, github_whitespace_api_key):
        db_keys = ["ghp_abcdef1234567890abcdef1234567890abcdef12"]
        handler, probe, logger = build_handler(github_whitespace_api_key, db_keys)

        assert handler.keys == db_keys
        assert probe.call_count == 1
        logger.warning.assert_called_once()
