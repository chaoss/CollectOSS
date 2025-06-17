"""
GitLab API Integration

This module provides a wrapper around the GitLab API for fetching contributor engagement data.
It handles authentication, rate limiting, and data retrieval for various engagement metrics.
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GitLabAPI:
    """
    Wrapper class for GitLab API interactions.
    
    This class provides methods to interact with the GitLab API to fetch
    contributor engagement data such as stars, forks, and project members.
    
    Attributes:
        base_url (str): Base URL for GitLab API
        headers (Dict): HTTP headers for API requests
    """
    
    def __init__(self, token: str, base_url: str = "https://gitlab.com/api/v4"):
        """
        Initialize the GitLab API wrapper.
        
        Args:
            token (str): GitLab API token for authentication
            base_url (str): Base URL for GitLab API (default: https://gitlab.com/api/v4)
        """
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to GitLab API with rate limit handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            return {}

    def get_user_profile(self, username: str) -> Dict:
        """
        Get a user's GitLab profile information.
        
        Args:
            username (str): GitLab username
            
        Returns:
            Dict: User profile data including name, company, location, etc.
            
        Raises:
            Exception: If there's an error fetching the profile
        """
        try:
            # First try to get user by username
            users = self._make_request("/users", {"username": username})
            if users and len(users) > 0:
                user_id = users[0]['id']
                return self._make_request(f"/users/{user_id}")
            return {}
        except Exception as e:
            raise Exception(f"Error fetching user profile: {str(e)}")

    def get_user_events(self, username: str, since: Optional[datetime] = None) -> List[Dict]:
        """Get user's public events"""
        try:
            users = self._make_request("/users", {"username": username})
            if users and len(users) > 0:
                user_id = users[0]['id']
                params = {}
                if since:
                    params['after'] = since.isoformat()
                return self._make_request(f"/users/{user_id}/events", params)
            return []
        except Exception as e:
            logger.error(f"Error fetching user events: {str(e)}")
            return []

    def has_starred_project(self, username: str, project_id: int) -> bool:
        """
        Check if a user has starred a project.
        
        Note: GitLab doesn't have a direct API to check if a specific user starred a project.
        This would require getting all stargazers and checking if the user is in the list.
        For large projects, this might be inefficient.
        
        Args:
            username (str): GitLab username
            project_id (int): Project ID
            
        Returns:
            bool: True if the user has starred the project, False otherwise
        """
        try:
            # TODO: Pagination required for large projects
            stargazers = self._make_request(f"/projects/{project_id}/starrers")
            if stargazers:
                for starrer in stargazers:
                    if starrer.get('username') == username:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking star status: {str(e)}")
            return False

    def has_forked_project(self, username: str, project_id: int) -> bool:
        """
        Check if a user has forked a project.
        
        Args:
            username (str): GitLab username
            project_id (int): Project ID
            
        Returns:
            bool: True if the user has forked the project, False otherwise
        """
        try:
            forks = self._make_request(f"/projects/{project_id}/forks")
            if forks:
                for fork in forks:
                    if fork.get('owner', {}).get('username') == username:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking fork status: {str(e)}")
            return False

    def get_project_contributors(self, project_id: int) -> List[Dict]:
        """Get list of contributors for a project"""
        try:
            return self._make_request(f"/projects/{project_id}/repository/contributors")
        except Exception as e:
            logger.error(f"Error fetching contributors: {str(e)}")
            return []

    def get_project_issues(self, project_id: int, state: str = 'all') -> List[Dict]:
        """Get project issues"""
        try:
            params = {'state': state, 'per_page': 100}
            return self._make_request(f"/projects/{project_id}/issues", params)
        except Exception as e:
            logger.error(f"Error fetching issues: {str(e)}")
            return []

    def get_project_merge_requests(self, project_id: int, state: str = 'all') -> List[Dict]:
        """Get project merge requests"""
        try:
            params = {'state': state, 'per_page': 100}
            return self._make_request(f"/projects/{project_id}/merge_requests", params)
        except Exception as e:
            logger.error(f"Error fetching merge requests: {str(e)}")
            return []

    def get_user_details(self, username: str) -> Dict:
        """Get user details including full name, location, company, etc."""
        return self.get_user_profile(username)

    def get_user_social_links(self, username: str) -> Dict:
        """Get user's social links from their profile"""
        try:
            profile = self.get_user_profile(username)
            social_links = {}
            
            if profile.get('website_url'):
                social_links['website'] = profile['website_url']
            
            if profile.get('linkedin'):
                social_links['linkedin'] = profile['linkedin']
            
            if profile.get('twitter'):
                social_links['twitter'] = profile['twitter']
                
            return social_links
        except Exception as e:
            logger.error(f"Error fetching social links: {str(e)}")
            return {}

    def get_project_stargazers(self, project_id: int) -> List[Dict]:
        """Get all users who starred the project"""
        try:
            stargazers = []
            page = 1
            per_page = 100
            
            while True:
                params = {'page': page, 'per_page': per_page}
                page_stargazers = self._make_request(f"/projects/{project_id}/starrers", params)
                
                if not page_stargazers:
                    break
                    
                stargazers.extend(page_stargazers)
                
                if len(page_stargazers) < per_page:
                    break
                    
                page += 1
                
            return stargazers
        except Exception as e:
            logger.error(f"Error fetching stargazers: {str(e)}")
            return []

    def get_project_forks(self, project_id: int) -> List[Dict]:
        """Get all forks of the project"""
        try:
            forks = []
            page = 1
            per_page = 100
            
            while True:
                params = {'page': page, 'per_page': per_page}
                page_forks = self._make_request(f"/projects/{project_id}/forks", params)
                
                if not page_forks:
                    break
                    
                forks.extend(page_forks)
                
                if len(page_forks) < per_page:
                    break
                    
                page += 1
                
            return forks
        except Exception as e:
            logger.error(f"Error fetching forks: {str(e)}")
            return []

    def get_contributions_last_year(self, username: str, project_id: int) -> int:
        """
        Get the number of contributions a user made to a project in the last year.
        
        This is an approximation based on commits, issues, and merge requests.
        
        Args:
            username (str): GitLab username
            project_id (int): Project ID
            
        Returns:
            int: Number of contributions in the last year
        """
        try:
            one_year_ago = datetime.now() - timedelta(days=365)
            contributions = 0
            
            # Get commits by the user
            commits = self._make_request(f"/projects/{project_id}/repository/commits", {
                'author': username,
                'since': one_year_ago.isoformat(),
                'per_page': 100
            })
            contributions += len(commits) if commits else 0
            
            # Get issues created by the user
            issues = self._make_request(f"/projects/{project_id}/issues", {
                'author_username': username,
                'created_after': one_year_ago.isoformat(),
                'per_page': 100
            })
            contributions += len(issues) if issues else 0
            
            # Get merge requests created by the user
            mrs = self._make_request(f"/projects/{project_id}/merge_requests", {
                'author_username': username,
                'created_after': one_year_ago.isoformat(),
                'per_page': 100
            })
            contributions += len(mrs) if mrs else 0
            
            return contributions
            
        except Exception as e:
            logger.error(f"Error calculating contributions: {str(e)}")
            return 0

    def get_project_info(self, project_id: int) -> Dict:
        """Get basic project information"""
        try:
            return self._make_request(f"/projects/{project_id}")
        except Exception as e:
            logger.error(f"Error fetching project info: {str(e)}")
            return {} 