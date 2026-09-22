# SPDX-License-Identifier: MIT
import pytest
from unittest.mock import Mock, patch

from collectoss.tasks.github.util.github_api_key_handler import GithubApiKeyHandler


github_whitespace_api_keys_list = ["", "    "]
github_none_api_key = None
github_valid_api_key = "ghp_1234567890abcdef1234567890abcdef12345678"
github_valid_db_api_key = "ghp_abcdef1234567890abcdef1234567890abcdef12"

def build_handler(config_key, db_keys):
    logger = Mock()

    with patch("collectoss.tasks.github.util.github_api_key_handler.RedisList"), \
         patch.object(GithubApiKeyHandler, "get_config_key", return_value=config_key), \
         patch.object(GithubApiKeyHandler, "get_api_keys_from_database", return_value=db_keys), \
         patch.object(GithubApiKeyHandler, "is_bad_api_key", return_value=False) as mock_is_bad_api_key:
        handler = GithubApiKeyHandler(logger)

    return handler, mock_is_bad_api_key, logger

@pytest.mark.unit
class TestConfigKeys:

    @pytest.mark.parametrize("github_whitespace_api_key", github_whitespace_api_keys_list)
    def test_whitespace_config_key_with_no_db_keys(self, github_whitespace_api_key):
        db_keys = []
        handler, mock_is_bad_api_key, logger = build_handler(github_whitespace_api_key, db_keys)

        assert handler.keys == []
        assert mock_is_bad_api_key.call_count == 0
        # with no keys left, get_api_keys returns before it reaches redis
        handler.redis_key_list.clear.assert_not_called()
        handler.redis_key_list.extend.assert_not_called()
        logger.warning.assert_called_once()

    def test_none_config_key_with_no_db_keys(self):
        db_keys = []
        handler, mock_is_bad_api_key, logger = build_handler(github_none_api_key, db_keys)

        assert handler.keys == []
        assert mock_is_bad_api_key.call_count == 0
        handler.redis_key_list.clear.assert_not_called()
        handler.redis_key_list.extend.assert_not_called()
        logger.warning.assert_not_called()

    def test_valid_config_key_with_no_db_keys(self):
        db_keys = []
        handler, mock_is_bad_api_key, logger = build_handler(github_valid_api_key, db_keys)

        assert handler.keys == [github_valid_api_key]
        assert mock_is_bad_api_key.call_count == 1
        handler.redis_key_list.extend.assert_called_once_with([github_valid_api_key])
        logger.warning.assert_not_called()

    @pytest.mark.parametrize("github_whitespace_api_key", github_whitespace_api_keys_list)
    def test_whitespace_config_key_with_db_keys(self, github_whitespace_api_key):
        expected_keys = [github_valid_db_api_key]
        # get_api_keys appends to the list it gets back, so hand it a copy
        handler, mock_is_bad_api_key, logger = build_handler(github_whitespace_api_key, list(expected_keys))

        assert handler.keys == expected_keys
        assert mock_is_bad_api_key.call_count == 1
        handler.redis_key_list.extend.assert_called_once_with(expected_keys)
        logger.warning.assert_called_once()
