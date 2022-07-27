
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


## How Metrics Actually Work?

### How Metrics are Added to Flask App

1. First Gunicorn creates the Flask app when it asks for the app from `server.py`
2. This casues the left most indented code in server.py to execute which calls create_app (code shown below) 
```python
server = Server()
server.create_app()
app = server.get_app()
```
3. Then `create_app()` calls the function `create_metrics()`
4. Then `create_metrics()`
    1. Gets a list of metric files from the `augur/api/metrics` directory
    2. Loops through the list of metric files and imports them all
    3. As each file is getting imported all functions with the decorator `@register_metric()` are getting called and the decorator function in `augur/api/util.py` is called
    4. The `@register_metric()` decorator adds the attribute `is_metric` to the function so we can determine that it is a metric later 
    5. Loops through the list of metric files and calls `add_metrics(file)` method and passes the metrics file
5. The `add_metrics(file)` method then loops through the file modules and finds the functions that are metrics using the `is_metric` attribute
6. It then takes the metric functions and calls `add_standard_metric(function, endpoint_name)` if the metric is standard, or `add_toss_metric(function, endpoint_name)` if it is a toss metric
    - Note: The `@register_metric()` decorator also defines whether the metric is a standard or toss metric by setting the `function.metadata` dict with a key value par of `{"type": "standard"}` or `{"type": "toss"}`
7. The `add_standard_metric(function, endpoint_name)` and `add_toss_metric(function, endpoint_name)` do the similar things so I will only explain `add_standard_metric(function, endpoint_name)`
8. The `add_standard_metric(function, endpoint_name)` first defines three endpoint string, `repo`, `repo group`, and a `deperacated version of repo`.
9. Then it calls the `@app.route()` decorator directly for each of the three endpoint strings and passes it a function to call when the route is pinged 
10. The function that it passes is called `endpoint_function(*args, **kwargs)` and is returned by the method `routify(function, endpoint_string)`

After step 10 is completed the metric endpoints have been created and added to the Flask app. They simply all refer to the `endpoint_function`

### What Happens when Metric Endpoints are Pinged

1. The Guncicorn server routes the request to the function that was passed to `@app.route()`. In this case the function passed was a `endpoint_function`
2. Then `endpoint_function(*args, **kwargs)` gets the args defined on the request, and calls `transform(function, args, kwargs)`
3. Then `transform(function, args, kwargs)` calls the metric function and 





