# D0 Contributor Engagement Worker (GitLab)

This module implements the D0 contributor engagement metric collection for GitLab projects. It tracks various engagement metrics to understand how users interact with GitLab repositories.

## Overview

The D0 metric aims to capture the breadth of contributor engagement with a project. For GitLab, this includes:

- **Stars**: Users who have starred the project
- **Forks**: Users who have forked the project  
- **Project Members**: Users who are members of the project (GitLab equivalent of "watchers")
- **Contributors**: Users who have made commits, created issues, or submitted merge requests
- **Issue Creation**: Users who have created issues
- **Comments**: Users who have commented on issues, merge requests, or discussions

## Features

### Supported Metrics

1. **Stars** - Users who starred the project
2. **Forks** - Users who forked the project
3. **Project Membership** - Users who are project members (similar to GitHub watchers)
4. **Contributions** - Commits, issues, and merge requests in the last year
5. **User Profile Data** - Name, location, company, social links

### GitLab vs GitHub Differences

| Feature | GitHub | GitLab | Notes |
|---------|--------|--------|-------|
| Stars | ✅ | ✅ | Direct equivalent |
| Forks | ✅ | ✅ | Direct equivalent |
| Watchers | ✅ | ❌ | GitLab doesn't have watchers |
| Project Members | ❌ | ✅ | GitLab-specific feature |
| Issues | ✅ | ✅ | Direct equivalent |
| Pull/Merge Requests | ✅ | ✅ | GitLab uses "Merge Requests" |
| Discussions | ❌ | ✅ | GitLab-specific feature |

## Architecture

```
augur/tasks/gitlab/d0_contributor_engagement/
├── __init__.py          # Module initialization
├── d0_worker.py         # Main worker logic
├── gitlab_api.py        # GitLab API wrapper
├── utils.py             # Utility functions
├── schema.sql           # Database schema
└── README.md           # This file
```

## Usage

### Basic Usage

```python
from augur.tasks.gitlab.d0_contributor_engagement import D0ContributorEngagementWorker
from sqlalchemy.orm import Session

# Initialize worker
worker = D0ContributorEngagementWorker(
    session=session,
    gitlab_token="your_gitlab_token",
    gitlab_url="https://gitlab.com/api/v4"  # Optional, defaults to GitLab.com
)

# Process a repository
worker.run(repo_id=123)
```

### Processing Specific Projects

```python
# Process a specific project by identifier
worker.process_project("namespace/project-name", repo_id=123)

# Process a single contributor
contributor_data = worker.process_contributor(
    username="username",
    project_identifier="namespace/project",
    repo_id=123
)
```

## Configuration

### Environment Variables

- `GITLAB_API_TOKEN`: GitLab API token for authentication
- `GITLAB_API_URL`: Base URL for GitLab API (optional, defaults to https://gitlab.com/api/v4)

### GitLab API Token

You need a GitLab API token with the following scopes:
- `read_api`: To read project and user information
- `read_repository`: To access repository data

Create a token at: https://gitlab.com/-/profile/personal_access_tokens

## Database Schema

The worker uses the same `d0_contributor_engagement` table as the GitHub implementation, with the `platform` field set to 'gitlab' to differentiate the data.

Key fields for GitLab:
- `username_gitlab`: GitLab username
- `platform`: Set to 'gitlab'
- `is_watching`: Represents project membership (GitLab equivalent)
- `social_links`: JSON object with website, LinkedIn, Twitter, Skype links

## API Rate Limits

GitLab.com has the following rate limits:
- **Authenticated requests**: 2,000 requests per minute
- **Unauthenticated requests**: 10 requests per minute

The worker includes basic rate limit handling and will retry failed requests.

## Limitations

1. **Stargazer Check**: GitLab doesn't provide a direct API to check if a specific user starred a project. The worker fetches all stargazers and searches through them, which can be inefficient for popular projects.

2. **No Watchers**: GitLab doesn't have a "watchers" concept like GitHub. We use project membership as the closest equivalent.

3. **Private Projects**: Some data may not be available for private projects depending on your access level.

4. **Self-hosted GitLab**: For self-hosted GitLab instances, you'll need to provide the appropriate `gitlab_url` parameter.

## Error Handling

The worker includes comprehensive error handling:
- API request failures are logged and retried
- Database errors trigger rollbacks
- Individual contributor processing errors don't stop the entire job
- Rate limit handling with exponential backoff

## Logging

The worker uses Python's logging module. Configure logging in your application:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('augur.tasks.gitlab.d0_contributor_engagement')
```

## Testing

```python
# Test with a small public project
worker.process_project("gitlab-org/gitlab-foss", repo_id=123)
```

## Performance Considerations

1. **Large Projects**: For projects with many stars/forks, consider processing in batches
2. **API Calls**: Each contributor requires multiple API calls, so processing can be slow for large projects
3. **Database**: Ensure proper indexing on `username_gitlab` and `repo_id` fields

## Contributing

When contributing to this module:
1. Follow the existing code style and patterns
2. Add appropriate error handling and logging
3. Update tests for any new functionality
4. Consider GitLab API limitations and differences from GitHub

## Related Files

- `augur/tasks/github/d0_contributor_engagement/`: GitHub equivalent
- `augur/application/db/models.py`: Database models
- `augur/tasks/gitlab/gitlab_api_handler.py`: General GitLab API utilities 