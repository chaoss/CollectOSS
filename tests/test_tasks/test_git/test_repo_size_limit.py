import unittest
from unittest.mock import MagicMock, patch, call
import collectoss.tasks.github.util.github_data_access
from collectoss.tasks.git.util.facade_worker.facade_worker.repofetch import check_repo_size_limit, GitCloneError


class TestRepoSizeLimit(unittest.TestCase):

    def setUp(self):
        self.github_access_patcher = patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.__init__", return_value=None)
        self.mock_github_init = self.github_access_patcher.start()

    def tearDown(self):
        self.github_access_patcher.stop()

    def test_size_limit_disabled(self):
        allowed, estimated_kb = check_repo_size_limit("https://github.com/chaoss/CollectOSS", 0)
        self.assertTrue(allowed)
        self.assertIsNone(estimated_kb)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_github_repo_under_limit_combined(self, mock_get_resource):
        # bare size: 1000 KB, file tree: 500,000 bytes (~488 KB)
        # estimated = 1000 + 488 = 1488 KB < 2000 KB limit
        mock_get_resource.side_effect = [
            {"size": 1000},  # repo info call
            {"truncated": False, "tree": [
                {"type": "blob", "size": 300000},
                {"type": "blob", "size": 200000},
                {"type": "tree", "size": None},  # directories are ignored
            ]}  # git tree call
        ]
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=2000
        )
        self.assertTrue(allowed)
        self.assertAlmostEqual(estimated_kb, 1000 + (500000 / 1024), places=1)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_github_repo_exceeds_limit_combined(self, mock_get_resource):
        # bare size: 1000 KB, file tree: 1,500,000 bytes (~1465 KB)
        # estimated = 1000 + 1465 = 2465 KB > 2000 KB limit
        mock_get_resource.side_effect = [
            {"size": 1000},
            {"truncated": False, "tree": [
                {"type": "blob", "size": 1500000},
            ]}
        ]
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=2000
        )
        self.assertFalse(allowed)
        self.assertAlmostEqual(estimated_kb, 1000 + (1500000 / 1024), places=1)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_github_truncated_tree_uses_bare_size_only(self, mock_get_resource):
        # When tree is truncated (large repo), fall back to bare size only
        mock_get_resource.side_effect = [
            {"size": 2500},
            {"truncated": True, "tree": []}  # truncated — can't sum blobs
        ]
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=2000
        )
        self.assertFalse(allowed)
        self.assertEqual(estimated_kb, 2500.0)

    @patch("httpx.get")
    def test_gitlab_repo_exceeds_limit(self, mock_httpx_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"statistics": {"repository_size": 5242880}}  # 5120 KB
        mock_httpx_get.return_value = mock_response

        allowed, estimated_kb = check_repo_size_limit(
            "https://gitlab.com/group/project", max_clone_size_kb=5000
        )
        self.assertFalse(allowed)
        self.assertAlmostEqual(estimated_kb, 5120.0, places=1)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_api_error_fallback(self, mock_get_resource):
        mock_get_resource.side_effect = Exception("API rate limit exceeded")
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=1000
        )
        self.assertTrue(allowed)
        self.assertIsNone(estimated_kb)


if __name__ == "__main__":
    unittest.main()
