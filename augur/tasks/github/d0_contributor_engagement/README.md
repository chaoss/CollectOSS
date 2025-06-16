# D0 Contributor Engagement

## Overview
The D0 Contributor Engagement metric tracks and analyzes how contributors interact with repositories on GitHub. This implementation collects data about contributors' engagement activities such as starring, forking, and watching repositories, along with their contribution history.

## Features
- Tracks contributor engagement metrics:
  - Stars (has_starred)
  - Forks (has_forked)
  - Watchers (is_watching)
  - Contributions in the last year
  - Contributor profile information (name, country, company, social links)
- Supports both GitHub and GitLab platforms
- Automatic data collection and updates
- Unique tracking per repository and contributor

## Database Schema
The `d0_contributor_engagement` table stores the following information:

| Column | Type | Description |
|--------|------|-------------|
| id | BigInteger | Primary key |
| updated_at | TIMESTAMP | Last update timestamp |
| username_github | String | GitHub username |
| username_gitlab | String | GitLab username |
| full_name | String | Contributor's full name |
| country | String | Contributor's country |
| social_links | JSONB | Social media links |
| company | String | Contributor's company |
| contributions_last_year | Integer | Number of contributions in last year |
| has_starred | Boolean | Whether contributor has starred the repo |
| has_forked | Boolean | Whether contributor has forked the repo |
| is_watching | Boolean | Whether contributor is watching the repo |
| collected_at | TIMESTAMP | When the data was collected |
| platform | String | Platform (GitHub/GitLab) |
| repo_id | BigInteger | Foreign key to repo table |

## Components

### 1. Worker (`d0_worker.py`)
The main worker that orchestrates the data collection process:
- Fetches contributor data from GitHub/GitLab
- Processes engagement metrics
- Updates the database

### 2. GitHub API Integration (`github_api.py`)
Handles interactions with the GitHub API:
- Retrieves starred repositories
- Checks for forks
- Gets watcher information
- Fetches contributor profiles

### 3. Utilities (`utils.py`)
Helper functions for:
- Data processing
- API rate limiting
- Error handling
- Data validation

### 4. Tests (`test_d0.py`)
Test suite for:
- Worker functionality
- API interactions
- Database operations
- Edge cases

## Setup and Installation

1. **Database Setup**
   ```sql
   -- Run the schema.sql file to create the necessary table
   psql -d your_database -f schema.sql
   ```

2. **Environment Variables**
   ```bash
   GITHUB_API_KEY=your_github_token
   GITHUB_API_USER=your_github_username
   ```

3. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Worker
```python
from augur.tasks.github.d0_contributor_engagement.d0_worker import D0ContributorEngagementWorker

worker = D0ContributorEngagementWorker()
worker.run()
```

### Running Tests
```bash
pytest augur/tasks/github/d0_contributor_engagement/test_d0.py
```

## API Functions

### 1. Get Contributor Engagement
```python
def get_contributor_engagement(repo_id: int, username: str) -> dict:
    """
    Get engagement metrics for a specific contributor in a repository.
    
    Args:
        repo_id (int): Repository ID
        username (str): GitHub username
        
    Returns:
        dict: Contributor engagement data
    """
```

### 2. Update Contributor Data
```python
def update_contributor_data(repo_id: int, username: str, data: dict) -> None:
    """
    Update contributor engagement data in the database.
    
    Args:
        repo_id (int): Repository ID
        username (str): GitHub username
        data (dict): Updated engagement data
    """
```

## Error Handling
The implementation includes robust error handling for:
- API rate limits
- Network failures
- Invalid data
- Database connection issues

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details. 