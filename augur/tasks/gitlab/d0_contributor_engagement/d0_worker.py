"""
D0 Contributor Engagement Worker (GitLab)

This module implements the worker for collecting and processing contributor engagement data
from GitLab projects. It tracks metrics such as stars, forks, and project membership for each
contributor in a project.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from augur.tasks.gitlab.d0_contributor_engagement.gitlab_api import GitLabAPI
from augur.tasks.gitlab.d0_contributor_engagement.utils import (
    format_social_links,
    process_contributor_data,
    update_contributor_data,
    extract_project_id_from_url,
)
from augur.application.db.models import D0ContributorEngagement, Repo

logger = logging.getLogger(__name__)

class D0ContributorEngagementWorker:
    """
    Worker class for collecting and processing contributor engagement data from GitLab.
    
    This worker fetches contributor data from GitLab, processes engagement metrics,
    and updates the database with the collected information.
    
    Attributes:
        gitlab_api (GitLabAPI): Instance of GitLabAPI for making API calls
        session (Session): SQLAlchemy database session
    """
    
    def __init__(self, session: Session, gitlab_token: str = None, gitlab_url: str = "https://gitlab.com/api/v4"):
        """
        Initialize the D0ContributorEngagementWorker.
        
        Args:
            session (Session): SQLAlchemy database session for database operations
            gitlab_token (str): GitLab API token for authentication
            gitlab_url (str): Base URL for GitLab API
        """
        self.gitlab_api = GitLabAPI(gitlab_token, gitlab_url) if gitlab_token else None
        self.session = session
    
    def run(self, repo_id: int) -> None:
        """
        Run the worker for a specific repository.
        
        This method orchestrates the entire process of collecting and processing
        contributor engagement data for a given GitLab project.
        
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
            
            # Extract project identifier from repo URL
            project_identifier = extract_project_id_from_url(repo.repo_git)
            if not project_identifier:
                raise ValueError(f"Could not extract project identifier from URL: {repo.repo_git}")
            
            # Get project ID from GitLab API
            project_info = self.gitlab_api.get_project_info(project_identifier)
            if not project_info:
                raise ValueError(f"Could not find project: {project_identifier}")
            
            project_id = project_info['id']
            
            # Get contributors for the project
            contributors = self.gitlab_api.get_project_contributors(project_id)
            
            # Process each contributor
            for contributor in contributors:
                self._process_contributor(repo_id, project_id, contributor)
            
            # Also process stargazers and forkers who might not be contributors
            self._process_stargazers(repo_id, project_id)
            self._process_forkers(repo_id, project_id)
            
            # Commit changes to database
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error in D0ContributorEngagementWorker.run: {str(e)}")
            raise
    
    def _process_contributor(self, repo_id: int, project_id: int, contributor: Dict) -> None:
        """
        Process a single contributor's data.
        
        This method fetches engagement metrics for a contributor and updates
        the database with the collected information.
        
        Args:
            repo_id (int): The ID of the repository
            project_id (int): The GitLab project ID
            contributor (Dict): Contributor information including username
            
        Raises:
            Exception: If there's an error processing the contributor's data
        """
        try:
            username = contributor.get('username')
            if not username:
                return
            
            # Get engagement metrics
            engagement_data = self._get_engagement_metrics(project_id, username)
            
            # Add contributor info to engagement data
            engagement_data.update({
                'username': username,
                'name': contributor.get('name'),
                'email': contributor.get('email'),
                'commits': contributor.get('commits', 0),
                'additions': contributor.get('additions', 0),
                'deletions': contributor.get('deletions', 0)
            })
            
            # Process and update data
            processed_data = process_contributor_data(engagement_data)
            update_contributor_data(self.session, repo_id, username, processed_data)
            
        except Exception as e:
            logger.error(f"Error processing contributor {username}: {str(e)}")
    
    def _process_stargazers(self, repo_id: int, project_id: int) -> None:
        """
        Process users who starred the project but might not be contributors.
        
        Args:
            repo_id (int): The ID of the repository
            project_id (int): The GitLab project ID
        """
        try:
            stargazers = self.gitlab_api.get_project_stargazers(project_id)
            
            for starrer in stargazers:
                username = starrer.get('username')
                if not username:
                    continue
                
                # Check if we already have this user in our database
                existing = self.session.query(D0ContributorEngagement).filter(
                    D0ContributorEngagement.username_gitlab == username,
                    D0ContributorEngagement.repo_id == repo_id
                ).first()
                
                if not existing:
                    # Get engagement metrics for this starrer
                    engagement_data = self._get_engagement_metrics(project_id, username)
                    engagement_data.update({
                        'username': username,
                        'name': starrer.get('name'),
                        'has_starred': True
                    })
                    
                    processed_data = process_contributor_data(engagement_data)
                    update_contributor_data(self.session, repo_id, username, processed_data)
                
        except Exception as e:
            logger.error(f"Error processing stargazers: {str(e)}")
    
    def _process_forkers(self, repo_id: int, project_id: int) -> None:
        """
        Process users who forked the project but might not be contributors.
        
        Args:
            repo_id (int): The ID of the repository
            project_id (int): The GitLab project ID
        """
        try:
            forks = self.gitlab_api.get_project_forks(project_id)
            
            for fork in forks:
                owner = fork.get('owner', {})
                username = owner.get('username')
                if not username:
                    continue
                
                # Check if we already have this user in our database
                existing = self.session.query(D0ContributorEngagement).filter(
                    D0ContributorEngagement.username_gitlab == username,
                    D0ContributorEngagement.repo_id == repo_id
                ).first()
                
                if not existing:
                    # Get engagement metrics for this forker
                    engagement_data = self._get_engagement_metrics(project_id, username)
                    engagement_data.update({
                        'username': username,
                        'name': owner.get('name'),
                        'has_forked': True
                    })
                    
                    processed_data = process_contributor_data(engagement_data)
                    update_contributor_data(self.session, repo_id, username, processed_data)
                
        except Exception as e:
            logger.error(f"Error processing forkers: {str(e)}")
    
    def _get_engagement_metrics(self, project_id: int, username: str) -> Dict:
        """
        Get engagement metrics for a contributor.
        
        This method fetches various engagement metrics from GitLab API,
        including stars, forks, and project membership.
        
        Args:
            project_id (int): The GitLab project ID
            username (str): The GitLab username of the contributor
            
        Returns:
            Dict: Dictionary containing engagement metrics
            
        Raises:
            Exception: If there's an error fetching the metrics
        """
        try:
            # Get user profile information
            user_profile = self.gitlab_api.get_user_details(username)
            
            return {
                'has_starred': self.gitlab_api.has_starred_project(username, project_id),
                'has_forked': self.gitlab_api.has_forked_project(username, project_id),
                'contributions_last_year': self.gitlab_api.get_contributions_last_year(username, project_id),
                'user_profile': user_profile
            }
        except Exception as e:
            logger.error(f"Error fetching engagement metrics for {username}: {str(e)}")
            return {}

    def get_project_contributors(self, project_identifier: str) -> List[Dict]:
        """
        Get all contributors for a project.
        
        Args:
            project_identifier: Project identifier (namespace/project or project ID)
            
        Returns:
            List of contributor dictionaries
        """
        try:
            # Get project info first to get the project ID
            project_info = self.gitlab_api.get_project_info(project_identifier)
            if not project_info:
                return []
            
            project_id = project_info['id']
            return self.gitlab_api.get_project_contributors(project_id)
            
        except Exception as e:
            logger.error(f"Error getting contributors for {project_identifier}: {str(e)}")
            return []

    def process_contributor(self, username: str, project_identifier: str, repo_id: int) -> Optional[Dict]:
        """
        Process a single contributor's data.
        
        Args:
            username: GitLab username
            project_identifier: Project identifier (namespace/project)
            repo_id: Repository ID in the database
            
        Returns:
            Dictionary containing processed contributor data
        """
        try:
            # Get project info first
            project_info = self.gitlab_api.get_project_info(project_identifier)
            if not project_info:
                return None
            
            project_id = project_info['id']
            
            # Get user details
            user_data = self.gitlab_api.get_user_details(username)
            if not user_data:
                return None

            # Get social links
            social_links = format_social_links(user_data)

            # Check engagement status
            has_starred = self.gitlab_api.has_starred_project(username, project_id)
            has_forked = self.gitlab_api.has_forked_project(username, project_id)
            contributions = self.gitlab_api.get_contributions_last_year(username, project_id)

            # Prepare data for storage
            contributor_data = {
                'repo_id': repo_id,
                'username_gitlab': username,
                'full_name': user_data.get('name'),
                'country': user_data.get('location'),
                'social_links': social_links,
                'company': user_data.get('organization'),
                'contributions_last_year': contributions,
                'has_starred': has_starred,
                'has_forked': has_forked,
                'is_watching': False,  # GitLab doesn't have a direct equivalent to GitHub's "watching"
                'collected_at': datetime.now(),
                'platform': 'gitlab'
            }

            return contributor_data

        except Exception as e:
            logger.error(f"Error processing contributor {username}: {str(e)}")
            return None

    def store_contributor_data(self, data: Dict) -> bool:
        """
        Store contributor data in the database.
        
        Args:
            data: Contributor data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if record already exists
            existing = self.session.query(D0ContributorEngagement).filter(
                D0ContributorEngagement.username_gitlab == data['username_gitlab'],
                D0ContributorEngagement.repo_id == data['repo_id']
            ).first()

            if existing:
                # Update existing record
                for key, value in data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
            else:
                # Create new record
                new_record = D0ContributorEngagement(**data)
                self.session.add(new_record)

            self.session.commit()
            return True

        except Exception as e:
            logger.error(f"Error storing contributor data: {str(e)}")
            self.session.rollback()
            return False

    def process_project(self, project_identifier: str, repo_id: int) -> None:
        """
        Process all contributors for a project.
        
        Args:
            project_identifier: Project identifier (namespace/project)
            repo_id: Repository ID in the database
        """
        try:
            # Get project info
            project_info = self.gitlab_api.get_project_info(project_identifier)
            if not project_info:
                logger.error(f"Could not find project: {project_identifier}")
                return
            
            project_id = project_info['id']
            logger.info(f"Processing project: {project_info['name']} (ID: {project_id})")

            # Process contributors
            contributors = self.gitlab_api.get_project_contributors(project_id)
            logger.info(f"Found {len(contributors)} contributors")

            for contributor in contributors:
                username = contributor.get('username')
                if username:
                    contributor_data = self.process_contributor(username, project_identifier, repo_id)
                    if contributor_data:
                        self.store_contributor_data(contributor_data)

            # Process stargazers
            stargazers = self.gitlab_api.get_project_stargazers(project_id)
            logger.info(f"Found {len(stargazers)} stargazers")

            for starrer in stargazers:
                username = starrer.get('username')
                if username:
                    # Check if already processed as contributor
                    existing = self.session.query(D0ContributorEngagement).filter(
                        D0ContributorEngagement.username_gitlab == username,
                        D0ContributorEngagement.repo_id == repo_id
                    ).first()
                    
                    if not existing:
                        contributor_data = self.process_contributor(username, project_identifier, repo_id)
                        if contributor_data:
                            self.store_contributor_data(contributor_data)

            # Process forkers
            forks = self.gitlab_api.get_project_forks(project_id)
            logger.info(f"Found {len(forks)} forks")

            for fork in forks:
                owner = fork.get('owner', {})
                username = owner.get('username')
                if username:
                    # Check if already processed
                    existing = self.session.query(D0ContributorEngagement).filter(
                        D0ContributorEngagement.username_gitlab == username,
                        D0ContributorEngagement.repo_id == repo_id
                    ).first()
                    
                    if not existing:
                        contributor_data = self.process_contributor(username, project_identifier, repo_id)
                        if contributor_data:
                            self.store_contributor_data(contributor_data)

            logger.info(f"Completed processing project: {project_identifier}")

        except Exception as e:
            logger.error(f"Error processing project {project_identifier}: {str(e)}")
            raise 