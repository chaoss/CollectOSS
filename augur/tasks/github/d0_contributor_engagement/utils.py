"""
Utility functions for D0 Contributor Engagement

This module provides helper functions for processing contributor engagement data,
handling API rate limits, and managing database operations.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Generator
import json
import requests
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from augur.application.db.models import D0ContributorEngagement

logger = logging.getLogger(__name__)

def is_within_last_year(date: datetime) -> bool:
    """Check if a date is within the last year"""
    one_year_ago = datetime.now() - timedelta(days=365)
    return date >= one_year_ago

def flatten_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten nested JSON structure"""
    flattened = {}
    
    def _flatten(d: Dict[str, Any], prefix: str = ''):
        for key, value in d.items():
            new_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                _flatten(value, new_key)
            elif isinstance(value, list):
                flattened[new_key] = json.dumps(value)
            else:
                flattened[new_key] = value
    
    _flatten(data)
    return flattened

def extract_social_links(profile: Dict[str, Any]) -> Dict[str, str]:
    """Extract social media links from GitHub profile"""
    social_links = {}
    
    if 'blog' in profile and profile['blog']:
        social_links['blog'] = profile['blog']
    
    if 'twitter_username' in profile and profile['twitter_username']:
        social_links['twitter'] = f"https://twitter.com/{profile['twitter_username']}"
    
    return social_links

def count_contributions_last_year(events: List[Dict[str, Any]]) -> int:
    """Count contributions in the last year from events"""
    one_year_ago = datetime.now() - timedelta(days=365)
    return sum(1 for event in events if datetime.fromisoformat(event['created_at'].replace('Z', '+00:00')) >= one_year_ago)

def parse_github_url(url: str) -> tuple:
    """Parse GitHub URL to get owner and repo name"""
    parts = url.strip('/').split('/')
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")
    return parts[-2], parts[-1]

def paginate(url: str, headers: Dict[str, str], params: Optional[Dict] = None) -> Generator[Dict, None, None]:
    """
    Generator function to handle paginated API responses.
    
    Args:
        url: The API endpoint URL
        headers: Request headers including authentication
        params: Optional query parameters
        
    Yields:
        Dictionary containing the response data for each page
    """
    if params is None:
        params = {}
    
    params['per_page'] = 100  # Maximum items per page
    page = 1
    
    while True:
        params['page'] = page
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:  # Empty page
                break
                
            yield data
            
            # Check if we've reached the last page
            if len(data) < params['per_page']:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during pagination for {url}: {str(e)}")
            break

def convert_to_datetime(date_str: str) -> Optional[datetime]:
    """
    Convert a date string to a datetime object.
    
    Args:
        date_str (str): Date string in ISO format
        
    Returns:
        Optional[datetime]: Datetime object or None if conversion fails
    """
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None

def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary.
    
    Args:
        data (Dict): Dictionary to get value from
        key (str): Key to look up
        default (Any, optional): Default value if key not found. Defaults to None.
        
    Returns:
        Any: Value from dictionary or default if not found
    """
    return data.get(key, default)

def format_social_links(profile_data: Dict) -> Dict:
    """
    Format social media links from GitHub profile data.
    
    Args:
        profile_data (Dict): GitHub profile data
        
    Returns:
        Dict: Formatted social media links
    """
    social_links = {}
    
    # Extract blog URL if it exists
    if 'blog' in profile_data and profile_data['blog']:
        social_links['blog'] = profile_data['blog']
    
    # Extract Twitter URL if it exists
    if 'twitter_username' in profile_data and profile_data['twitter_username']:
        social_links['twitter'] = f"https://twitter.com/{profile_data['twitter_username']}"
    
    return social_links

def parse_github_username(url: str) -> Optional[str]:
    """
    Extract GitHub username from various URL formats.
    
    Args:
        url: URL string that might contain a GitHub username
        
    Returns:
        GitHub username or None if not found
    """
    if not url:
        return None
        
    # Remove common URL prefixes
    url = url.lower().replace('https://', '').replace('http://', '')
    
    # Handle different URL formats
    if 'github.com/' in url:
        try:
            return url.split('github.com/')[1].split('/')[0]
        except IndexError:
            return None
    elif '@' in url:
        return url.split('@')[1].split()[0]
    
    return None

def get_contributors(repo_url: str) -> List[Dict]:
    """
    Get list of contributors for a repository.
    
    Args:
        repo_url (str): Repository URL
        
    Returns:
        List[Dict]: List of contributor information
        
    Raises:
        Exception: If there's an error fetching contributors
    """
    try:
        # Implementation depends on your specific needs
        # This is a placeholder for the actual implementation
        return []
    except Exception as e:
        raise Exception(f"Error getting contributors: {str(e)}")

def process_contributor_data(data: Dict) -> Dict:
    """
    Process raw contributor data into a format suitable for database storage.
    
    Args:
        data (Dict): Raw contributor data
        
    Returns:
        Dict: Processed contributor data
    """
    return {
        'username_github': data.get('username'),
        'full_name': data.get('name'),
        'country': data.get('location'),
        'company': data.get('company'),
        'social_links': format_social_links(data),
        'contributions_last_year': data.get('contributions_last_year', 0),
        'has_starred': data.get('has_starred', False),
        'has_forked': data.get('has_forked', False),
        'is_watching': data.get('is_watching', False),
        'collected_at': datetime.now(),
        'platform': 'github'
    }

def update_contributor_data(session: Session, repo_id: int, username: str, data: Dict) -> bool:
    """
    Update contributor data in the database.
    
    Args:
        session (Session): SQLAlchemy database session
        repo_id (int): Repository ID
        username (str): GitHub username
        data (Dict): Contributor data to update
        
    Returns:
        bool: True if update was successful, False otherwise
        
    Raises:
        SQLAlchemyError: If there's a database error
    """
    try:
        # Add repo_id to data
        data['repo_id'] = repo_id
        
        # Check if record exists
        existing = session.query(D0ContributorEngagement).filter_by(
            username_github=username,
            repo_id=repo_id
        ).first()
        
        if existing:
            # Update existing record
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            # Create new record
            new_record = D0ContributorEngagement(**data)
            session.add(new_record)
        
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error storing contributor data: {str(e)}")
        return False 