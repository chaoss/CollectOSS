
# Metrics

## What are Metrics?

Metrics are standardized endpoints that take a repo_id or a repo_group_id, as path paramaters. They also frequently accept begin_date, end_date, and period as query paramaters, although these are not required to be defined as a metric. 

## How to Define a New Metric?

1. Add a file to the metrics directory, or use an existing file if your metric fits into one of the existing file
2. Import these required libraries and objects
```py
import datetime
import sqlalchemy as s
import pandas as pd
from augur.api.util import register_metric
from augur.application.db.engine import engine
```
3. Defining the function
    1. Add the decorator @register_metric to the function
    2. Name the function using snake case
    3. Keep in mind that the endpoint that is created from this function will be the same name as the function but with the underscores replaced with hyphens
    4. Define a positonal paramater of repo_group_id first, then a keyword paramater of repo_id second
    5. Define any additional keyword paramater the function may need
        - Note: When querying the endpoint these will be passed as query paramaters
4. Define any queries with the structure show below
```py
repo_sql = s.sql.text(""" SELECT repo.repo_name FROM repo WHERE repo.repo_id = :repo_id """)
results = pd.read_sql(repo_sql, engine, params={'repo_id': repo_id})
```
5. Return either a pandas dataframe, dict, or json.
    - Note: If you return a pandas dataframe or dict it will be automatically converted into json

## How to Query Your New Metric?

1. First lets go over how to query by repo and repo_group
    - A metric is queried by repo using the following url strucutre: `https://<host>:<port>/api/unstable/repos/<repo_id>/`
    - A metric is queried by repo group using the follwing url structure: `https://<host>:<port>/api/unstable/repo-groups/<repo_group_id>/`
2. Now that we have the base url defined lets add the metric we want to query. This is done by adding the name of the metric we want but with the underscores replaced with hyphens
    - For example if we wanted to query a metric called open_issue_count by repo. Then we would use the url: `https://<host>:<port>/api/unstable/repos/<repo_id>/open-issue-count`
3. Finally if there are any other keyword arguments specified on the metric, then we can specify the values of those using query paramaters.
    - For example if we wanted to query the open_issue_count metric by repo, but only wanted the count of issues after 01-01-2020 and before 01-01-2021. Then we could use this url: `https://<host>:<port>/api/unstable/repos/<repo_id>/open-issue-count?begin_data=01-01-2020&end_date=01-01-2021`


## How Metrics Actuall Work?





