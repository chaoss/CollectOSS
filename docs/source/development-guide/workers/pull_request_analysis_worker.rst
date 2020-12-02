============================
Pull Request Analysis Worker
============================

This worker analyzes the open pull requests of every repository and predicts the probability of it getting accepted and merged. Pull requests having a low probability of getting merged, are indicative of being outlier/anomalous ones.

Worker Configuration
---------------------

To kickstart the worker, it needs to receive a task from the Housekeeper, similar to other workers, and have a corresponding worker specific configuration.

The standard options are:

- ``switch`` - a boolean flag indicating if the worker should automatically be started with Augur. Defaults to ``0`` (false).
- ``workers`` - the number of instances of this worker that Augur should spawn if ``switch`` is set to ``1``. Defaults to ``1``.
- ``port`` - the TCP port the worker will use to communicate with Augur’s broker, the default being ``51400``.
- ``insight_days`` - open PRs created in the duration of the past ``x`` days are analyzed.

.. note::

    - ``insight_days`` can be adjusted to analyze very recently opened PRs as well. Run the data collection workers to have enough data to analyze!
    - This worker uses some methods of the *Message Insights Worker*

Worker Pipeline
---------------

When a repo is analyzed, the trained ML models are used to predict the probability of acceptance.
The major factors influencing this are:

1. **Pull request characteristics**: No. of commits, sentiment of PR title
2. **Contributor characteristics**: Acceptance rate of PRs created, no. of projects contributed to in the past
3. **Repo characteristics**: No. of open issues, no. of watchers, past acceptance rate of PRs
4. **Discussion characteristics**: No. of comments, no. of participants, average sentiment of all comments

After feature engineering, the following features were considered:

- No. of commits
- No. of comments
- Length of PR in days
- Relationship between PR creator and repo (member, collaborator, etc)
- Average sentiment score of comments
- Watch count of repo
- Past acceptance ratio of a PR in the repo

.. code-block:: bash

    pull_request_analysis_worker/
    ├── __init__.py
    ├── pull_request_analysis_worker.py
    ├── runtime.py
    ├── setup.py
    └── trained_pr_model.pkl

The ``trained_pr_model.pkl`` is the saved pre-trained model, used for the analysis. 

After prediction, the ``pull_request_analysis`` table is populated with the predicted probabilities for every open PR.