"""
GitHub API Integration

This module provides a wrapper around the GitHub API for fetching contributor engagement data.
It handles authentication, rate limiting, and data retrieval for various engagement metrics.
"""

import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GitHubAPI:
    """
    Wrapper class for GitHub API interactions.
    
    This class provides methods to interact with the GitHub API to fetch
    contributor engagement data such as stars, forks, and watchers.
    
    Attributes:
        base_url (str): Base URL for GitHub API
        headers (Dict): HTTP headers for API requests
    """
    
    def __init__(self, token: str):
        """
        Initialize the GitHub API wrapper.
        
        Args:
            token (str): GitHub API token for authentication
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to GitHub API with rate limit handling"""
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
        Get a user's GitHub profile information.
        
        Args:
            username (str): GitHub username
            
        Returns:
            Dict: User profile data including name, company, location, etc.
            
        Raises:
            Exception: If there's an error fetching the profile
        """
        try:
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, headers=self.headers)
            return response.json()
        except Exception as e:
            raise Exception(f"Error fetching user profile: {str(e)}")

    def get_user_events(self, username: str, since: Optional[datetime] = None) -> List[Dict]:
        """Get user's public events"""
        params = {}
        if since:
            params['since'] = since.isoformat()
        return self._make_request(f"/users/{username}/events/public", params)

    def has_starred(self, username: str, repo_id: int) -> bool:
        """
        Check if a user has starred a repository.
        
        Args:
            username (str): GitHub username
            repo_id (int): Repository ID
            
        Returns:
            bool: True if the user has starred the repository, False otherwise
            
        Raises:
            Exception: If there's an error checking the star status
        """
        try:
            url = f"{self.base_url}/user/starred/{username}/{repo_id}"
            response = requests.get(url, headers=self.headers)
            return response.status_code == 204
        except Exception as e:
            raise Exception(f"Error checking star status: {str(e)}")

    def has_forked(self, username: str, repo_id: int) -> bool:
        """
        Check if a user has forked a repository.
        
        Args:
            username (str): GitHub username
            repo_id (int): Repository ID
            
        Returns:
            bool: True if the user has forked the repository, False otherwise
            
        Raises:
            Exception: If there's an error checking the fork status
        """
        try:
            url = f"{self.base_url}/repos/{username}/{repo_id}/forks"
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200 and len(response.json()) > 0
        except Exception as e:
            raise Exception(f"Error checking fork status: {str(e)}")

    def is_watching(self, username: str, repo_id: int) -> bool:
        """
        Check if a user is watching a repository.
        
        Args:
            username (str): GitHub username
            repo_id (int): Repository ID
            
        Returns:
            bool: True if the user is watching the repository, False otherwise
            
        Raises:
            Exception: If there's an error checking the watch status
        """
        try:
            url = f"{self.base_url}/user/subscriptions/{username}/{repo_id}"
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            raise Exception(f"Error checking watch status: {str(e)}")

    def get_repo_contributors(self, owner: str, repo: str) -> List[Dict]:
        """Get list of contributors for a repository"""
        return self._make_request(f"/repos/{owner}/{repo}/contributors")

    def get_repo_issues(self, owner: str, repo: str, state: str = 'all') -> List[Dict]:
        """Get repository issues"""
        return self._make_request(f"/repos/{owner}/{repo}/issues", {'state': state})

    def get_repo_pulls(self, owner: str, repo: str, state: str = 'all') -> List[Dict]:
        """Get repository pull requests"""
        return self._make_request(f"/repos/{owner}/{repo}/pulls", {'state': state})

    def get_user_details(self, username: str) -> Dict:
        """Get user details including full name, location, company, etc."""
        endpoint = f"/users/{username}"
        return self._make_request(endpoint)

    def get_user_social_links(self, username: str) -> Dict:
        """Get user's social links (currently returns empty dict as this requires scraping)"""
        # This would require scraping the user's profile page
        # For now, return empty dict as placeholder
        return {}

    def has_starred_repo(self, username: str, owner: str, repo: str) -> bool:
        """Check if user has starred the repository."""
        endpoint = f"/user/{username}/starred/{owner}/{repo}"
        try:
            response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
            return response.status_code == 204  # 204 means starred
        except requests.exceptions.RequestException:
            return False

    def has_forked_repo(self, username: str, owner: str, repo: str) -> bool:
        """Check if user has forked the repository."""
        endpoint = f"/repos/{owner}/{repo}/forks"
        params = {'per_page': 100}
        page = 1
        while True:
            params['page'] = page
            forks = self._make_request(endpoint, params)
            if not forks:
                break
            for fork in forks:
                if fork['owner']['login'] == username:
                    return True
            page += 1
        return False

    def is_watching_repo(self, username: str, owner: str, repo: str) -> bool:
        """Check if user is watching the repository."""
        endpoint = f"/user/{username}/subscriptions"
        params = {'per_page': 100}
        page = 1
        while True:
            params['page'] = page
            subscriptions = self._make_request(endpoint, params)
            if not subscriptions:
                break
            for sub in subscriptions:
                if sub['owner']['login'] == owner and sub['name'] == repo:
                    return True
            page += 1
        return False

    def get_contributions_last_year(self, username: str, repo_id: int) -> int:
        """
        Get the number of contributions a user has made to a repository in the last year.
        
        Args:
            username (str): GitHub username
            repo_id (int): Repository ID
            
        Returns:
            int: Number of contributions in the last year
            
        Raises:
            Exception: If there's an error fetching contribution data
        """
        try:
            # Calculate date one year ago
            one_year_ago = datetime.now() - timedelta(days=365)
            date_str = one_year_ago.strftime("%Y-%m-%d")
            
            url = f"{self.base_url}/repos/{username}/{repo_id}/commits"
            params = {
                "author": username,
                "since": date_str
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            return len(response.json())
        except Exception as e:
            raise Exception(f"Error fetching contributions: {str(e)}") 