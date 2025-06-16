"""
D0 Contributor Engagement Worker

This module implements the worker for collecting and processing contributor engagement data
from GitHub repositories. It tracks metrics such as stars, forks, and watchers for each
contributor in a repository.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from augur.tasks.github.d0_contributor_engagement.github_api import GitHubAPI
from augur.tasks.github.d0_contributor_engagement.utils import (
    safe_get,
    format_social_links,
    convert_to_datetime,
    get_contributors,
    process_contributor_data,
    update_contributor_data
)
from augur.application.db.models import D0ContributorEngagement, Repo

logger = logging.getLogger(__name__)

class D0ContributorEngagementWorker:
    """
    Worker class for collecting and processing contributor engagement data.
    
    This worker fetches contributor data from GitHub, processes engagement metrics,
    and updates the database with the collected information.
    
    Attributes:
        github_api (GitHubAPI): Instance of GitHubAPI for making API calls
        session (Session): SQLAlchemy database session
    """
    
    def __init__(self, session: Session):
        """
        Initialize the D0ContributorEngagementWorker.
        
        Args:
            session (Session): SQLAlchemy database session for database operations
        """
        self.github_api = GitHubAPI()
        self.session = session
    
    def run(self, repo_id: int) -> None:
        """
        Run the worker for a specific repository.
        
        This method orchestrates the entire process of collecting and processing
        contributor engagement data for a given repository.
        
        Args:
            repo_id (int): The ID of the repository to process
            
        Raises:
            Exception: If there's an error during data collection or processing
        """
        try:
            # Get repository information
            repo = self.session.query(Repo).filter(Repo.repo_id == repo_id).first()
            if not repo:
                raise ValueError(f"Repository with ID {repo_id} not found")
            
            # Get contributors for the repository
            contributors = get_contributors(repo.repo_git)
            
            # Process each contributor
            for contributor in contributors:
                self._process_contributor(repo_id, contributor)
            
            # Commit changes to database
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            raise
    
    def _process_contributor(self, repo_id: int, contributor: Dict) -> None:
        """
        Process a single contributor's data.
        
        This method fetches engagement metrics for a contributor and updates
        the database with the collected information.
        
        Args:
            repo_id (int): The ID of the repository
            contributor (Dict): Contributor information including username
            
        Raises:
            Exception: If there's an error processing the contributor's data
        """
        try:
            username = contributor.get('username')
            if not username:
                return
            
            # Get engagement metrics
            engagement_data = self._get_engagement_metrics(repo_id, username)
            
            # Process and update data
            processed_data = process_contributor_data(engagement_data)
            update_contributor_data(self.session, repo_id, username, processed_data)
            
        except Exception as e:
            raise Exception(f"Error processing contributor {username}: {str(e)}")
    
    def _get_engagement_metrics(self, repo_id: int, username: str) -> Dict:
        """
        Get engagement metrics for a contributor.
        
        This method fetches various engagement metrics from GitHub API,
        including stars, forks, and watchers.
        
        Args:
            repo_id (int): The ID of the repository
            username (str): The GitHub username of the contributor
            
        Returns:
            Dict: Dictionary containing engagement metrics
            
        Raises:
            Exception: If there's an error fetching the metrics
        """
        try:
            return {
                'has_starred': self.github_api.has_starred(username, repo_id),
                'has_forked': self.github_api.has_forked(username, repo_id),
                'is_watching': self.github_api.is_watching(username, repo_id),
                'contributions_last_year': self.github_api.get_contributions_last_year(username, repo_id)
            }
        except Exception as e:
            raise Exception(f"Error fetching engagement metrics for {username}: {str(e)}")

    def get_repo_contributors(self, owner: str, repo: str) -> List[Dict]:
        """
        Get all contributors for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of contributor dictionaries
        """
        try:
            contributors = []
            endpoint = f"/repos/{owner}/{repo}/contributors"
            params = {'per_page': 100}
            page = 1
            
            while True:
                params['page'] = page
                response = self.github_api._make_request(endpoint, params)
                
                if not response:
                    break
                    
                contributors.extend(response)
                
                if len(response) < params['per_page']:
                    break
                    
                page += 1
                
            return contributors
        except Exception as e:
            logger.error(f"Error getting contributors for {owner}/{repo}: {str(e)}")
            return []

    def process_contributor(self, username: str, owner: str, repo: str, repo_id: int) -> Optional[Dict]:
        """
        Process a single contributor's data.
        
        Args:
            username: GitHub username
            owner: Repository owner
            repo: Repository name
            repo_id: Repository ID in the database
            
        Returns:
            Dictionary containing processed contributor data
        """
        try:
            # Get user details
            user_data = self.github_api.get_user_details(username)
            if not user_data:
                return None

            # Get social links
            social_links = format_social_links(user_data)

            # Check engagement status
            has_starred = self.github_api.has_starred_repo(username, owner, repo)
            has_forked = self.github_api.has_forked_repo(username, owner, repo)
            is_watching = self.github_api.is_watching_repo(username, owner, repo)

            # Get contributions
            contributions = self.github_api.get_contributions_last_year(username, f"{owner}/{repo}")

            # Build the data record
            return {
                'username_github': username,
                'username_gitlab': None,  # Not implemented yet
                'full_name': safe_get(user_data, 'name'),
                'country': safe_get(user_data, 'location'),
                'social_links': social_links,
                'company': safe_get(user_data, 'company'),
                'contributions_last_year': contributions,
                'has_starred': has_starred,
                'has_forked': has_forked,
                'is_watching': is_watching,
                'collected_at': datetime.utcnow(),
                'platform': 'github',
                'repo_id': repo_id
            }
        except Exception as e:
            logger.error(f"Error processing contributor {username}: {str(e)}")
            return None

    def store_contributor_data(self, data: Dict) -> bool:
        """
        Store contributor data in the database.
        
        Args:
            data: Dictionary containing contributor data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if record exists
            existing = self.session.query(D0ContributorEngagement).filter_by(
                username_github=data['username_github'],
                repo_id=data['repo_id']
            ).first()

            if existing:
                # Update existing record
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                # Create new record
                new_record = D0ContributorEngagement(**data)
                self.session.add(new_record)

            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error storing contributor data: {str(e)}")
            return False

    def process_repo(self, owner: str, repo: str, repo_id: int) -> None:
        """
        Process all contributors for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            repo_id: Repository ID in the database
        """
        logger.info(f"Processing repository {owner}/{repo}")
        
        # Get all contributors
        contributors = self.get_repo_contributors(owner, repo)
        
        for contributor in contributors:
            username = safe_get(contributor, 'login')
            if not username:
                continue
                
            # Process contributor data
            data = self.process_contributor(username, owner, repo, repo_id)
            if data:
                # Store in database
                if self.store_contributor_data(data):
                    logger.info(f"Successfully processed contributor {username}")
                else:
                    logger.error(f"Failed to store data for contributor {username}")
