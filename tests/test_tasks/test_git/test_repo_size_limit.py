import unittest
from unittest.mock import MagicMock, patch
import collectoss.tasks.github.util.github_data_access
from collectoss.tasks.git.util.facade_worker.facade_worker.repofetch import check_repo_size_limit, GitCloneError


class TestRepoSizeLimit(unittest.TestCase):

    def setUp(self):
        self.github_access_patcher = patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.__init__", return_value=None)
        self.mock_github_init = self.github_access_patcher.start()

    def tearDown(self):
        self.github_access_patcher.stop()

    def test_size_limit_disabled(self):
        allowed, reported_kb = check_repo_size_limit("https://github.com/chaoss/CollectOSS", 0)
        self.assertTrue(allowed)
        self.assertIsNone(reported_kb)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_github_repo_under_limit(self, mock_get_resource):
        mock_get_resource.return_value = {"size": 1000}
        allowed, reported_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=2000
        )
        self.assertTrue(allowed)
        self.assertEqual(reported_kb, 1000)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_github_repo_exceeds_limit(self, mock_get_resource):
        mock_get_resource.return_value = {"size": 2001}
        allowed, reported_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=2000
        )
        self.assertFalse(allowed)
        self.assertEqual(reported_kb, 2001)

    @patch("httpx.get")
    def test_gitlab_repo_exceeds_limit(self, mock_httpx_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"statistics": {"repository_size": 5242880}}  # 5120 KB
        mock_httpx_get.return_value = mock_response

        allowed, reported_kb = check_repo_size_limit(
            "https://gitlab.com/group/project", max_clone_size_kb=5000
        )
        self.assertFalse(allowed)
        self.assertEqual(reported_kb, 5120)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_api_error_fallback(self, mock_get_resource):
        mock_get_resource.side_effect = Exception("API rate limit exceeded")
        allowed, reported_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=1000
        )
        self.assertTrue(allowed)
        self.assertIsNone(reported_kb)

    def test_is_valid_searchable_email(self):
        from collectoss.tasks.github.facade_github.contributor_interfaceable.contributor_interface import is_valid_searchable_email
        self.assertTrue(is_valid_searchable_email("user@example.org"))
        self.assertTrue(is_valid_searchable_email("john.doe@company.co.uk"))

        self.assertFalse(is_valid_searchable_email("root@augur"))
        self.assertFalse(is_valid_searchable_email("michaelwoodruff@mwc-021001.dhcp.missouri.edu"))
        self.assertFalse(is_valid_searchable_email("user@localhost"))
        self.assertFalse(is_valid_searchable_email("invalid_email"))
        self.assertFalse(is_valid_searchable_email(""))
        self.assertFalse(is_valid_searchable_email(None))


if __name__ == "__main__":
    unittest.main()
