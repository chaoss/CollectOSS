"""
Test module for D0 Contributor Engagement Worker (GitLab)

This module contains unit tests for the GitLab D0 contributor engagement functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from augur.tasks.gitlab.d0_contributor_engagement.d0_worker import D0ContributorEngagementWorker
from augur.tasks.gitlab.d0_contributor_engagement.gitlab_api import GitLabAPI
from augur.tasks.gitlab.d0_contributor_engagement.utils import (
    format_social_links,
    parse_gitlab_url,
    extract_project_id_from_url,
    process_contributor_data
)


class TestGitLabAPI(unittest.TestCase):
    """Test cases for GitLabAPI class"""
    
    def setUp(self):
        self.api = GitLabAPI("test_token")
    
    @patch('requests.get')
    def test_get_user_profile(self, mock_get):
        """Test getting user profile"""
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 123, "username": "testuser", "name": "Test User"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock the second call for user details
        mock_response2 = Mock()
        mock_response2.json.return_value = {
            "id": 123,
            "username": "testuser", 
            "name": "Test User",
            "location": "Test City",
            "organization": "Test Org"
        }
        mock_response2.raise_for_status.return_value = None
        
        with patch.object(self.api, '_make_request') as mock_request:
            mock_request.side_effect = [
                [{"id": 123, "username": "testuser"}],
                {"id": 123, "username": "testuser", "name": "Test User"}
            ]
            
            result = self.api.get_user_profile("testuser")
            self.assertEqual(result["username"], "testuser")
    
    def test_has_starred_project(self):
        """Test checking if user starred a project"""
        with patch.object(self.api, '_make_request') as mock_request:
            mock_request.return_value = [
                {"username": "testuser", "name": "Test User"},
                {"username": "otheruser", "name": "Other User"}
            ]
            
            result = self.api.has_starred_project("testuser", 123)
            self.assertTrue(result)
            
            result = self.api.has_starred_project("nonexistent", 123)
            self.assertFalse(result)
    
    def test_has_forked_project(self):
        """Test checking if user forked a project"""
        with patch.object(self.api, '_make_request') as mock_request:
            mock_request.return_value = [
                {"owner": {"username": "testuser"}, "name": "forked-project"},
                {"owner": {"username": "otheruser"}, "name": "other-fork"}
            ]
            
            result = self.api.has_forked_project("testuser", 123)
            self.assertTrue(result)
            
            result = self.api.has_forked_project("nonexistent", 123)
            self.assertFalse(result)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_format_social_links(self):
        """Test formatting social links from profile data"""
        profile_data = {
            "website_url": "https://example.com",
            "linkedin": "https://linkedin.com/in/testuser",
            "twitter": "https://twitter.com/testuser",
            "skype": "testuser_skype"
        }
        
        result = format_social_links(profile_data)
        
        self.assertEqual(result["website"], "https://example.com")
        self.assertEqual(result["linkedin"], "https://linkedin.com/in/testuser")
        self.assertEqual(result["twitter"], "https://twitter.com/testuser")
        self.assertEqual(result["skype"], "testuser_skype")
    
    def test_parse_gitlab_url(self):
        """Test parsing GitLab URLs"""
        test_cases = [
            ("https://gitlab.com/namespace/project", ("namespace", "project")),
            ("https://gitlab.example.com/group/subgroup/project", ("subgroup", "project")),
            ("gitlab.com/user/repo", ("user", "repo"))
        ]
        
        for url, expected in test_cases:
            result = parse_gitlab_url(url)
            self.assertEqual(result, expected)
    
    def test_extract_project_id_from_url(self):
        """Test extracting project identifier from URL"""
        url = "https://gitlab.com/namespace/project"
        result = extract_project_id_from_url(url)
        self.assertEqual(result, "namespace/project")
    
    def test_process_contributor_data(self):
        """Test processing contributor data"""
        raw_data = {
            "username": "testuser",
            "name": "Test User",
            "organization": "Test Org",
            "location": "Test City",
            "website_url": "https://example.com",
            "has_starred": True,
            "has_forked": False,
            "contributions_last_year": 5
        }
        
        result = process_contributor_data(raw_data)
        
        self.assertEqual(result["username_gitlab"], "testuser")
        self.assertEqual(result["full_name"], "Test User")
        self.assertEqual(result["company"], "Test Org")
        self.assertEqual(result["country"], "Test City")
        self.assertEqual(result["platform"], "gitlab")
        self.assertTrue(result["has_starred"])
        self.assertFalse(result["has_forked"])


class TestD0ContributorEngagementWorker(unittest.TestCase):
    """Test cases for D0ContributorEngagementWorker class"""
    
    def setUp(self):
        self.mock_session = Mock()
        self.worker = D0ContributorEngagementWorker(
            session=self.mock_session,
            gitlab_token="test_token"
        )
    
    def test_init(self):
        """Test worker initialization"""
        self.assertIsNotNone(self.worker.gitlab_api)
        self.assertEqual(self.worker.session, self.mock_session)
    
    @patch('augur.tasks.gitlab.d0_contributor_engagement.d0_worker.Repo')
    def test_run_repo_not_found(self, mock_repo):
        """Test run method when repository is not found"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.worker.run(123)
        
        self.assertIn("Repository with ID 123 not found", str(context.exception))
    
    def test_get_engagement_metrics(self):
        """Test getting engagement metrics for a contributor"""
        with patch.object(self.worker.gitlab_api, 'get_user_details') as mock_user_details, \
             patch.object(self.worker.gitlab_api, 'has_starred_project') as mock_starred, \
             patch.object(self.worker.gitlab_api, 'has_forked_project') as mock_forked, \
             patch.object(self.worker.gitlab_api, 'get_contributions_last_year') as mock_contributions:
            
            mock_user_details.return_value = {"username": "testuser", "name": "Test User"}
            mock_starred.return_value = True
            mock_forked.return_value = False
            mock_contributions.return_value = 10
            
            result = self.worker._get_engagement_metrics(123, "testuser")
            
            self.assertTrue(result["has_starred"])
            self.assertFalse(result["has_forked"])
            self.assertEqual(result["contributions_last_year"], 10)
    
    def test_process_contributor(self):
        """Test processing a single contributor"""
        with patch.object(self.worker.gitlab_api, 'get_project_info') as mock_project_info, \
             patch.object(self.worker.gitlab_api, 'get_user_details') as mock_user_details, \
             patch.object(self.worker.gitlab_api, 'has_starred_project') as mock_starred, \
             patch.object(self.worker.gitlab_api, 'has_forked_project') as mock_forked, \
             patch.object(self.worker.gitlab_api, 'get_contributions_last_year') as mock_contributions:
            
            mock_project_info.return_value = {"id": 123, "name": "Test Project"}
            mock_user_details.return_value = {
                "username": "testuser",
                "name": "Test User",
                "location": "Test City",
                "organization": "Test Org"
            }
            mock_starred.return_value = True
            mock_forked.return_value = False
            mock_contributions.return_value = 5
            
            result = self.worker.process_contributor("testuser", "namespace/project", 456)
            
            self.assertIsNotNone(result)
            self.assertEqual(result["username_gitlab"], "testuser")
            self.assertEqual(result["full_name"], "Test User")
            self.assertEqual(result["repo_id"], 456)
            self.assertEqual(result["platform"], "gitlab")


if __name__ == '__main__':
    unittest.main() 