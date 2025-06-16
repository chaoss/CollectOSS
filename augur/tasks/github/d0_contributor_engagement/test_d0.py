"""
Test suite for D0 Contributor Engagement worker
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from augur.tasks.github.d0_contributor_engagement.d0_worker import D0ContributorEngagementWorker
from augur.application.db.models import D0ContributorEngagement, Repo

@pytest.fixture
def mock_session():
    """Create a mock database session"""
    return Mock()

@pytest.fixture
def mock_github_api():
    """Create a mock GitHub API"""
    with patch('augur.tasks.github.d0_contributor_engagement.d0_worker.GitHubAPI') as mock:
        yield mock

@pytest.fixture
def worker(mock_session, mock_github_api):
    """Create a worker instance with mocked dependencies"""
    return D0ContributorEngagementWorker(mock_session)

def test_process_contributor(worker, mock_session):
    """Test processing a single contributor"""
    # Mock data
    repo_id = 1
    contributor = {
        'username': 'testuser',
        'name': 'Test User',
        'location': 'Test Country',
        'company': 'Test Company'
    }
    
    # Mock GitHub API responses
    worker.github_api.has_starred.return_value = True
    worker.github_api.has_forked.return_value = False
    worker.github_api.is_watching.return_value = True
    worker.github_api.get_contributions_last_year.return_value = 10
    
    # Process contributor
    worker._process_contributor(repo_id, contributor)
    
    # Verify database operations
    mock_session.query.assert_called()
    mock_session.commit.assert_called()

def test_get_engagement_metrics(worker):
    """Test getting engagement metrics"""
    repo_id = 1
    username = 'testuser'
    
    # Mock GitHub API responses
    worker.github_api.has_starred.return_value = True
    worker.github_api.has_forked.return_value = False
    worker.github_api.is_watching.return_value = True
    worker.github_api.get_contributions_last_year.return_value = 10
    
    # Get metrics
    metrics = worker._get_engagement_metrics(repo_id, username)
    
    # Verify metrics
    assert metrics['has_starred'] is True
    assert metrics['has_forked'] is False
    assert metrics['is_watching'] is True
    assert metrics['contributions_last_year'] == 10

def test_run_worker(worker, mock_session):
    """Test running the worker for a repository"""
    repo_id = 1
    
    # Mock repository
    mock_repo = Mock(spec=Repo)
    mock_repo.repo_id = repo_id
    mock_repo.repo_git = 'https://github.com/test/repo.git'
    mock_session.query.return_value.filter.return_value.first.return_value = mock_repo
    
    # Mock contributors
    with patch('augur.tasks.github.d0_contributor_engagement.d0_worker.get_contributors') as mock_get_contributors:
        mock_get_contributors.return_value = [
            {'username': 'testuser1'},
            {'username': 'testuser2'}
        ]
        
        # Run worker
        worker.run(repo_id)
        
        # Verify operations
        mock_session.query.assert_called()
        mock_session.commit.assert_called()
        assert mock_get_contributors.call_count == 1

def test_error_handling(worker, mock_session):
    """Test error handling in worker"""
    repo_id = 1
    
    # Mock repository not found
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    # Test running worker with non-existent repository
    with pytest.raises(ValueError):
        worker.run(repo_id)
    
    # Verify rollback was called
    mock_session.rollback.assert_called() 