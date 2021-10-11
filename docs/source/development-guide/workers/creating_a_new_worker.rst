============================
Creating a New Worker
============================

Worker Setup
---------------------

1. If you are hitting an API on a platform like GitHub, or GitLab, follow the pattern in those workers. 
2. If you are analyzing Augur data, the `value_worker` provides a good example. 

What are the key sections? 
-----------------------------------

The key sections you can copy from any worker are illustrated in this example from the Pull Request Worker:  

.. code-block:: python


    #SPDX-License-Identifier: MIT
    import ast
    import json
    import logging
    import os
    import sys
    import time
    import traceback
    import requests
    import copy
    from datetime import datetime
    from multiprocessing import Process, Queue
    import pandas as pd
    import sqlalchemy as s
    from sqlalchemy.sql.expression import bindparam
    from workers.worker_base import Worker

    class GitHubPullRequestWorker(Worker):
        """
        Worker that collects Pull Request related data from the
        Github API and stores it in our database.

        :param task: most recent task the broker added to the worker's queue
        :param config: holds info like api keys, descriptions, and database connection strings
        """
        def __init__(self, config={}):

            worker_type = "pull_request_worker"

            # Define what this worker can be given and know how to interpret
            given = [['github_url']]
            models = ['pull_requests', 'pull_request_commits', 'pull_request_files']

            # Define the tables needed to insert, update, or delete on
            data_tables = ['contributors', 'pull_requests',
                'pull_request_assignees', 'pull_request_events', 'pull_request_labels',
                'pull_request_message_ref', 'pull_request_meta', 'pull_request_repo',
                'pull_request_reviewers', 'pull_request_teams', 'message', 'pull_request_commits',
                'pull_request_files', 'pull_request_reviews', 'pull_request_review_message_ref']
            operations_tables = ['worker_history', 'worker_job']

            self.deep_collection = True
            self.platform_id = 25150 # GitHub

            # Run the general worker initialization
            super().__init__(worker_type, config, given, models, data_tables, operations_tables)

            # Define data collection info
            self.tool_source = 'GitHub Pull Request Worker'
            self.tool_version = '1.0.0'
            self.data_source = 'GitHub API'

Getting Your Worker to Talk to Augur
----------------------------------------

In the house keeper block, you need to add something following this pattern, inside the "jobs" section: 

.. code-block:: python  

    "Housekeeper": {
        "update_redirects": {
            "switch": 0,
            "repo_group_id": 0
        },
        "jobs": [
            {
                "delay": 150000,
                "given": [
                    "github_url"
                ],
                "model": "contributor_breadth",
                "repo_group_id": 0
            },
            {
                "all_focused": 1,
                "delay": 150000,
                "given": [
                    "github_url"
                ],
                "model": "issues",
                "repo_group_id": 0
            },
            {
                "delay": 150000,
                "given": [
                    "<given specified in your worker>"
                ],
                "model": "<model specified in your worker>",
                "repo_group_id": 0
            },

In the Worker block you need to add something like this: 

.. code-block:: python 

    "Workers": {
        "contributor_breadth_worker": {
            "port": 48234,
            "switch": 0,
            "workers": 1
        },
        "facade_worker": {
            "port": 48868,
            "repo_directory": "/Volumes/repo_two/repos/augur-prwrt/",
            "switch": 1,
            "workers": 1
        },
        "your_worker": {
            "port": <some port not otherwise in use>,
            "switch": 1,
            "workers": 1
        },


There should NOT be a comma after the final entry in each block. 

ALSO, if you wanted to have those blocks installed with auger itself when you do the PR, you need to add them to the `$AUGUR_ROOT/augur/config.py` file. The recommended way is to set a port range not already in use and assign a random variable range with the others, like this `your_new_worker_p = randint(56500, 56999)` ... its totally ok to compress a couple other port ranges for this process.

You can copy the housekeeper block verbatim from what you added to your own `augur.config.json`. For the worker block, in the `config.py` it would look like this: 

.. code-block:: python 

    "your_worker": {
        "port": your_worker_p ,
        "switch": 1,
        "workers": 1
    },



The `switch` variable tells Augur to run your worker. The `worker` variable tells Augur how many to run. We recommend you begin with the number `1`.

Let us know if that works.  I will add this to the documentation. 