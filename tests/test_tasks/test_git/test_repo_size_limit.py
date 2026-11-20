import unittest
from unittest.mock import MagicMock, patch
import collectoss.tasks.github.util.github_data_access
from collectoss.tasks.git.util.facade_worker.facade_worker.repofetch import (
    check_repo_size_limit, _get_github_repo_size_kb, _get_gitlab_repo_size_kb
)


class TestRepoSizeLimit(unittest.TestCase):

    def setUp(self):
        self.github_access_patcher = patch(
            "collectoss.tasks.github.util.github_data_access.GithubDataAccess.__init__",
            return_value=None
        )
        self.mock_github_init = self.github_access_patcher.start()

    def tearDown(self):
        self.github_access_patcher.stop()

    # ------------------------------------------------------------------
    # check_repo_size_limit — limit disabled
    # ------------------------------------------------------------------

    def test_size_limit_disabled(self):
        """When limit is 0 (disabled), always allow regardless of repo size."""
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", 0
        )
        self.assertTrue(allowed)
        self.assertIsNone(estimated_kb)

    # ------------------------------------------------------------------
    # check_repo_size_limit — GitHub, normal (non-truncated) tree
    # ------------------------------------------------------------------

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_github_repo_under_limit(self, mock_get_resource):
        """Repo comfortably below limit — clone is allowed."""
        # bare: 1000 KB, blobs: 500,000 bytes = ~488 KB → ~1488 KB total
        mock_get_resource.side_effect = [
            {"size": 1000},
            {"truncated": False, "tree": [
                {"type": "blob", "size": 300000},
                {"type": "blob", "size": 200000},
                {"type": "tree", "size": None},   # directories have no size
            ]}
        ]
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=2000
        )
        self.assertTrue(allowed)
        self.assertAlmostEqual(estimated_kb, 1000 + (500000 / 1024), places=1)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_github_repo_exceeds_limit(self, mock_get_resource):
        """Repo above limit — clone is blocked."""
        # bare: 1000 KB, blobs: 1,500,000 bytes = ~1465 KB → ~2465 KB total > 2000 KB
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
    def test_github_repo_exactly_at_limit(self, mock_get_resource):
        """Repo exactly at the limit — clone is allowed (limit is exclusive upper bound)."""
        mock_get_resource.side_effect = [
            {"size": 2000},
            {"truncated": False, "tree": []}
        ]
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=2000
        )
        self.assertTrue(allowed)
        self.assertEqual(estimated_kb, 2000.0)

    # ------------------------------------------------------------------
    # check_repo_size_limit — GitHub, truncated tree
    # ------------------------------------------------------------------

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_github_truncated_tree_uses_partial_blob_data(self, mock_get_resource):
        """When the tree is truncated, partial blob data is still counted.

        GitHub's recursive tree endpoint returns up to 100,000 entries. When
        truncated=True, full coverage requires traversing sub-trees individually
        (not implemented here). Instead, the partial blob sizes in the response
        are used as a lower-bound estimate. If the lower bound already exceeds
        the limit, the clone is blocked.
        """
        # bare: 1000 KB, partial blobs (truncated): 800,000 bytes = ~781 KB
        # total: ~1781 KB > 1500 KB limit → blocked
        mock_get_resource.side_effect = [
            {"size": 1000},
            {"truncated": True, "tree": [
                {"type": "blob", "size": 800000},
            ]}
        ]
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=1500
        )
        self.assertFalse(allowed)
        self.assertAlmostEqual(estimated_kb, 1000 + (800000 / 1024), places=1)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_github_truncated_tree_under_limit_still_allowed(self, mock_get_resource):
        """Truncated tree whose partial sum falls under the limit — clone is allowed.

        The partial blob sum is a lower bound on the true working-tree size. When
        that lower bound is still below the limit, we allow the clone. Operators
        who want a tighter safety margin for repos near the limit should configure
        a smaller max_clone_size_kb.
        """
        # bare: 500 KB, partial blobs: 100,000 bytes = ~98 KB → ~598 KB < 2000 KB
        mock_get_resource.side_effect = [
            {"size": 500},
            {"truncated": True, "tree": [
                {"type": "blob", "size": 100000},
            ]}
        ]
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=2000
        )
        self.assertTrue(allowed)
        self.assertAlmostEqual(estimated_kb, 500 + (100000 / 1024), places=1)

    # ------------------------------------------------------------------
    # check_repo_size_limit — error handling (fail closed)
    # ------------------------------------------------------------------

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_api_error_blocks_clone(self, mock_get_resource):
        """When the API call fails, cloning is BLOCKED (fail closed).

        A configured limit must not be silently bypassed because of a
        network failure or API error.
        """
        mock_get_resource.side_effect = Exception("API rate limit exceeded")
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=1000
        )
        self.assertFalse(allowed)
        self.assertIsNone(estimated_kb)

    @patch("collectoss.tasks.github.util.github_data_access.GithubDataAccess.get_resource")
    def test_malformed_api_response_blocks_clone(self, mock_get_resource):
        """When the API returns a non-dict, _get_github_repo_size_kb raises, blocking the clone."""
        mock_get_resource.return_value = "not a dict"
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=1000
        )
        self.assertFalse(allowed)
        self.assertIsNone(estimated_kb)

    def test_unsupported_forge_blocks_clone(self):
        """For unsupported forges, cloning is blocked when a limit is configured."""
        allowed, estimated_kb = check_repo_size_limit(
            "https://bitbucket.org/some/repo", max_clone_size_kb=1000
        )
        self.assertFalse(allowed)
        self.assertIsNone(estimated_kb)

    def test_unsupported_forge_no_limit_allows_clone(self):
        """For unsupported forges with no limit configured, cloning is allowed."""
        allowed, estimated_kb = check_repo_size_limit(
            "https://bitbucket.org/some/repo", max_clone_size_kb=0
        )
        self.assertTrue(allowed)
        self.assertIsNone(estimated_kb)

    # ------------------------------------------------------------------
    # check_repo_size_limit — GitLab
    # ------------------------------------------------------------------

    @patch("httpx.get")
    def test_gitlab_repo_exceeds_limit(self, mock_httpx_get):
        """GitLab repo above limit — clone is blocked."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "statistics": {"repository_size": 5242880}  # 5120 KB
        }
        mock_httpx_get.return_value = mock_response

        allowed, estimated_kb = check_repo_size_limit(
            "https://gitlab.com/group/project", max_clone_size_kb=5000
        )
        self.assertFalse(allowed)
        self.assertAlmostEqual(estimated_kb, 5120.0, places=1)

    @patch("httpx.get")
    def test_gitlab_api_error_blocks_clone(self, mock_httpx_get):
        """When GitLab API fails, cloning is blocked (fail closed)."""
        mock_httpx_get.side_effect = Exception("Connection refused")

        allowed, estimated_kb = check_repo_size_limit(
            "https://gitlab.com/group/project", max_clone_size_kb=5000
        )
        self.assertFalse(allowed)
        self.assertIsNone(estimated_kb)

    @patch("httpx.get")
    def test_gitlab_repo_under_limit(self, mock_httpx_get):
        """GitLab repo below limit — clone is allowed."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "statistics": {"repository_size": 1024000}  # 1000 KB
        }
        mock_httpx_get.return_value = mock_response

        allowed, estimated_kb = check_repo_size_limit(
            "https://gitlab.com/group/project", max_clone_size_kb=5000
        )
        self.assertTrue(allowed)
        self.assertAlmostEqual(estimated_kb, 1000.0, places=1)

    def test_negative_limit_treated_as_disabled(self):
        """A negative limit value is treated as disabled — clone is always allowed."""
        allowed, estimated_kb = check_repo_size_limit(
            "https://github.com/chaoss/CollectOSS", max_clone_size_kb=-1
        )
        self.assertTrue(allowed)
        self.assertIsNone(estimated_kb)


if __name__ == "__main__":
    unittest.main()
