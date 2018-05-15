# Augur Tutorial: a metric from start to finish

This tutorial shows the entire process of adding a metric to Augur. You will complete the following steps:

  1. [Selecting a metric](#selecting-a-metric) from the [CHAOSS Metrics Committee wiki](https://github.com/chaoss/metrics/)
  2. [Prototyping a metric](#prototyping-a-metric) with a [Jupyter Notebook](/notebooks/example-metrics.ipynb)
  3. [Adding a metric to a class](#adding-a-metric-to-a-class)
  4. [Creating an endpoint](#creating-an-endpoint) for a metric on the REST API
  5. [Referencing an endpoint on the frontend](#referencing-an-endpoint-on-the-frontend)
  6. [Adding a visualization](#adding-a-visualization) for the metric to the appropiate tab.

Before we begin, make sure you have completed the [developer installation](./dev-install.md) and verified that `make dev` runs Augur successfully.

## Selecting a metric

In order to know which metrics still need to be developed, run `make metrics-status` in the base directory of the repository. All of the red metrics are not yet implemented. For the purpose of this tutorial, suppose that under 'Growth, Maturity, and Decline', a 'lines-deleted' metric had not yet been implemented. This metric would show how many lines were deleted from a project each week.

## Prototyping a metric

Now that we've chosen the 'lines-deleted' metric, we next need to write function that implements it. While this could be done directly in the class files, we will use a Jupyter notebook while developing the implementation. This allows us to take advantage of Jupyter's advanced logging capabilities.

First, we need to figure out how we are going to get the data we need. Since there are already connectors to [GHTorrent](http://ghtorrent.org/relational.html) and the [GitHub API](https://developer.github.com/v3/) we will look at their documentation first. While searching GitHub's documentation, we can see that they provide [an endpoint](https://developer.github.com/v3/repos/statistics/#get-the-number-of-additions-and-deletions-per-week) to "get the number of additions and deletions per week". Perfect!

Start the Jupyter Notebook by running `make jupyter` in the base directory. If you want to skip ahead, you can see two example metrics (including this one) implemented in the [example-metrics.ipynb](../notebooks/example-metrics.ipynb) file. Otherwise, read on...

Since we know that we are going to be writing a metric for the GitHub API datasource, we should import all the packages depended on by the GitHub API class:

```python
import augur

# import everything that githubapi.py imports so we can just copy and paste our function later
import json
import re
from dateutil.parser import parse
import pandas as pd
import github
import numpy as np
import datetime
import requests
```

Next, we should create an Augur application so that we can use our existing configuration file:

```python
augurApp = augur.Application('../augur.cfg')
# we only need an instance of the GitHubAPI class
github = augurApp.github()
```

Now we are ready to implement the metric:

```python
# We are writing this function to be run as part of the GitHub class, so 
# the "self" in this function will be an instance of an augur.GitHubAPI
def lines_deleted(self, owner, repo=None): 
    """
    Additions and deletions each week

    :param owner: The name of the project owner
    :param repo: The name of the repo
    :return: DataFrame with each row being am issue
    """
    # get the data we need from the GitHub API
    # see <project_root>/augur/githubapi.py for examples using the GraphQL API
    url = "https://api.github.com/repos/{}/{}/stats/code_frequency".format(owner, repo)
    json = requests.get(url, auth=('user', self.GITHUB_API_KEY)).json()
    # get our data into a dataframe
    df = pd.DataFrame(json, columns=['date', 'additions', 'deletions'])
    # all timeseries metrics need a 'date' column
    df['date'] = pd.to_datetime(df['date'], unit='s', infer_datetime_format=True)
    # normalize our data
    df['deletions'] = df['deletions'] * -1
    # return the dataframe
    return df
```

The above function demonstrates a few important rules to keep in mind while writing your own metrics:
  1. All functions that provide metric data must accept an 'owner' and 'repo' parameter
  2. All functions that provide metric data must return a Pandas DataFrame
  3. All function that implement timeseries metrics must return a 'date' column

Now, we need to test this metric, so let's hack it on to the GitHubAPI class and run it in the context of our initialized GitHubAPI instance:

```python
# add our new function to the class
augur.GitHubAPI.lines_deleted = lines_deleted

# test our function on the initialized instance
ld = github.lines_deleted('osshealth', 'augur')
ld['deletions'].plot()
```

What do you see? This a good time to dive into your data and make sure it looks the way you expect it to. If it does, you are ready to move on and add it to a class.

## Adding a metric to a class

Since we were working in the context of the GitHubAPI class as we developed the metric, adding the `lines_deleted` function to the class is as simple as copying and pasting it into [githubapi.py](../augur/githubapi.py):

```python
class GitHubAPI(object):
  # ...
  # existing stuff in the class
  # ...
  def lines_deleted(self, owner, repo=None): 
      """
      Additions and deletions each week

      :param owner: The name of the project owner
      :param repo: The name of the repo
      :return: DataFrame with each row being am issue
      """
      # get the data we need from the GitHub API
      # see <project_root>/augur/githubapi.py for examples using the GraphQL API
      url = "https://api.github.com/repos/{}/{}/stats/code_frequency".format(owner, repo)
      json = requests.get(url, auth=('user', self.GITHUB_API_KEY)).json()
      # get our data into a dataframe
      df = pd.DataFrame(json, columns=['date', 'additions', 'deletions'])
      # all timeseries metrics need a 'date' column
      df['date'] = pd.to_datetime(df['date'], unit='s', infer_datetime_format=True)
      # normalize our data
      df['deletions'] = df['deletions'] * -1
      # return the dataframe
      return df
```

Once that is done, we need to write tests for the function in that data source's test file, in our case [/test/test_github.py](../test/test_github.py):

```python
def test_lines_deleted(github):
    assert github.lines_deleted("OSSHealth", "augur").isin(["2741"]).any
``` 

That test verifies that a value that we know should be there *is there*.

Now that our metric has been added to a class, we can expose it as an endpoint.

## Creating an endpoint

All of the endpoints are defined in [server.py](../augur/server.py)

Since we created a timeseries metric, we are going to use the `addTimeseries` function to expose this function as an endpoint. We also need to write the API documentation for the function.

In [`<project root>/augur/server.py`](../augur/server.py):
```python
"""
@api {get} /:owner/:repo/timeseries/lines_deleted Lines deleted by week
@apiDescription <a href="https://github.com/OSSHealth/metrics/blob/master/activity-metrics/lines-deleted.md">CHAOSS Metric Definition</a>
@apiName LinesDeleted
@apiGroup Growth-Maturity-Decline

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            'date': '2015-11-01T00:00:00Z', 
                            'lines_deleted': 3961
                        },
                        {
                            'date': '2015-11-08T00:00:00Z', 
                            'lines_deleted': 3896
                        },
                    ]
"""
addTimeseries(app, github.lines_deleted, 'lines_deleted')
```

You can test this endpoint by running `make dev` and visiting [http://localhost:3333/api/unstable/osshealth/augur/timeseries/lines_deleted](http://localhost:3333/api/unstable/osshealth/augur/timeseries/lines_deleted)

Now is a good time to create a commit, because you are done with backend changes. That way your backend changes can be accepted into the project seperately from your frontend changes.

## Referencing an endpoint on the frontend

Now, we should make sure our front-end API library, [AugurAPI.js](../frontend/app/AugurAPI.js), knows how to access our new endpoint.

In [`<project root>/frontend/app/AugurAPI.js`](../frontend/app/AugurAPI.js):
```javascript
Timeseries(repo, 'linesDeleted', 'lines_deleted')
```

This will allow charts that accept timeseries able to reference your endpoint. Now we will visualize your data!

## Adding a visualization

Since lines-deleted is a timeseries metric, we can use the existing `<LineChart>` component to visualize it. Since it was a 'Growth, Maturity, and Decline' metric, we want to add it to the [GrowthMaturityDeclineCard](../frontend/app/components/GrowthMaturityDeclineCard.vue).

In [`<project root>/frontend/app/components/GrowthMaturityDeclineCard.vue`](../frontend/app/components/GrowthMaturityDeclineCard.vue):

```html
<div class="col col-6">
  <line-chart source="linesDeleted" 
              title="Lines Deleted / Week" 
              cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/lines-deleted.md"
              cite-text="Lines Deleted"> 
  </line-chart>
</div>
```

Now if you run `make dev` in the project root and visit [http://localhost:3333/?repo=rails+rails](http://localhost:3333/?repo=rails+rails) you should see our new visualization.

You've now added a metric to Augur from start to finish!
