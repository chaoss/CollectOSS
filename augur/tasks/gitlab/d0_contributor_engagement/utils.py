"""
Utility functions for D0 Contributor Engagement (GitLab)

This module provides helper functions for processing contributor engagement data,
handling API rate limits, and managing database operations for GitLab repositories.
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
    """Extract social media links from GitLab profile"""
    social_links = {}
    
    if 'website_url' in profile and profile['website_url']:
        social_links['website'] = profile['website_url']
    
    if 'linkedin' in profile and profile['linkedin']:
        social_links['linkedin'] = profile['linkedin']
    
    if 'twitter' in profile and profile['twitter']:
        social_links['twitter'] = profile['twitter']
    
    if 'skype' in profile and profile['skype']:
        social_links['skype'] = profile['skype']
    
    return social_links

def count_contributions_last_year(events: List[Dict[str, Any]]) -> int:
    """Count contributions in the last year from events"""
    one_year_ago = datetime.now() - timedelta(days=365)
    return sum(1 for event in events if datetime.fromisoformat(event['created_at'].replace('Z', '+00:00')) >= one_year_ago)

def parse_gitlab_url(url: str) -> tuple:
    """Parse GitLab URL to get namespace and project name"""
    parts = url.strip('/').split('/')
    if len(parts) < 2:
        raise ValueError("Invalid GitLab URL")
    # For GitLab URLs like https://gitlab.com/namespace/project
    # or https://gitlab.example.com/namespace/project
    if 'gitlab' in url:
        # Find the index where the actual namespace/project starts
        try:
            gitlab_index = next(i for i, part in enumerate(parts) if 'gitlab' in part)
            return parts[gitlab_index + 1], parts[gitlab_index + 2]
        except (IndexError, StopIteration):
            return parts[-2], parts[-1]
    return parts[-2], parts[-1]

def paginate_gitlab(url: str, headers: Dict[str, str], params: Optional[Dict] = None) -> Generator[Dict, None, None]:
    """
    Generator function to handle paginated GitLab API responses.
    
    Args:
        url: The API endpoint URL
        headers: Request headers including authentication
        params: Optional query parameters
        
    Yields:
        Dictionary containing the response data for each page
    """
    if params is None:
        params = {}
    
    params['per_page'] = 100  # Maximum items per page for GitLab
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
    Format social media links from GitLab profile data.
    
    Args:
        profile_data (Dict): GitLab profile data
        
    Returns:
        Dict: Formatted social media links
    """
    social_links = {}
    
    # Extract website URL if it exists
    if 'website_url' in profile_data and profile_data['website_url']:
        social_links['website'] = profile_data['website_url']
    
    # Extract LinkedIn URL if it exists
    if 'linkedin' in profile_data and profile_data['linkedin']:
        social_links['linkedin'] = profile_data['linkedin']
    
    # Extract Twitter URL if it exists
    if 'twitter' in profile_data and profile_data['twitter']:
        social_links['twitter'] = profile_data['twitter']
    
    # Extract Skype if it exists
    if 'skype' in profile_data and profile_data['skype']:
        social_links['skype'] = profile_data['skype']
    
    return social_links

def parse_gitlab_username(url: str) -> Optional[str]:
    """
    Extract GitLab username from various URL formats.
    
    Args:
        url: URL string that might contain a GitLab username
        
    Returns:
        GitLab username or None if not found
    """
    if not url:
        return None
        
    # Remove common URL prefixes
    url = url.lower().replace('https://', '').replace('http://', '')
    
    # Handle different URL formats
    if 'gitlab.com/' in url:
        try:
            return url.split('gitlab.com/')[1].split('/')[0]
        except IndexError:
            return None
    elif '@' in url:
        return url.split('@')[1].split()[0]
    
    return None

def get_contributors(project_url: str) -> List[Dict]:
    """
    Get list of contributors for a GitLab project.
    
    Args:
        project_url (str): Project URL
        
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
        raise Exception(f"Error fetching contributors: {str(e)}")

def process_contributor_data(data: Dict) -> Dict:
    """
    Process raw contributor data into a standardized format.
    
    Args:
        data (Dict): Raw contributor data from GitLab API
        
    Returns:
        Dict: Processed contributor data
    """
    processed = {
        'username_gitlab': safe_get(data, 'username'),
        'full_name': safe_get(data, 'name'),
        'company': safe_get(data, 'organization'),
        'country': safe_get(data, 'location'),
        'social_links': format_social_links(data),
        'has_starred': safe_get(data, 'has_starred', False),
        'has_forked': safe_get(data, 'has_forked', False),
        'is_watching': safe_get(data, 'is_member', False),  # GitLab equivalent of "watching" (project membership)
        'contributions_last_year': safe_get(data, 'contributions_last_year', 0),
        'collected_at': datetime.now(),
        'platform': 'gitlab'
    }
    
    return processed

def update_contributor_data(session: Session, repo_id: int, username: str, data: Dict) -> bool:
    """
    Update or insert contributor data in the database.
    
    Args:
        session (Session): SQLAlchemy database session
        repo_id (int): Repository ID
        username (str): GitLab username
        data (Dict): Processed contributor data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if record already exists
        existing = session.query(D0ContributorEngagement).filter(
            D0ContributorEngagement.username_gitlab == username,
            D0ContributorEngagement.repo_id == repo_id
        ).first()
        
        if existing:
            # Update existing record
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.now()
        else:
            # Create new record
            new_record = D0ContributorEngagement(
                repo_id=repo_id,
                **data
            )
            session.add(new_record)
        
        session.commit()
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error updating contributor data: {str(e)}")
        session.rollback()
        return False
    except Exception as e:
        logger.error(f"Error updating contributor data: {str(e)}")
        session.rollback()
        return False

def extract_project_id_from_url(url: str) -> Optional[str]:
    """
    Extract project ID or namespace/project from GitLab URL.
    
    Args:
        url: GitLab project URL
        
    Returns:
        Project identifier (namespace/project format)
    """
    try:
        namespace, project = parse_gitlab_url(url)
        return f"{namespace}/{project}"
    except Exception:
        return None

    """
    Calculate an engagement score based on various metrics.
    
    Args:
        data: Contributor engagement data
        
    Returns:
        Engagement score (0.0 to 1.0)
    """
    score = 0.0
    
    # Star gives 0.2 points
    if data.get('has_starred'):
        score += 0.2
    
    # Fork gives 0.3 points
    if data.get('has_forked'):
        score += 0.3
    
    # Being a member gives 0.3 points
    if data.get('is_member'):
        score += 0.3
    
    # Contributions give up to 0.2 points (scaled)
    contributions = data.get('contributions_last_year', 0)
    if contributions > 0:
        # Scale contributions to 0.2 max (10+ contributions = max score)
        score += min(0.2, contributions / 50)
    
    return min(1.0, score)  # Cap at 1.0 