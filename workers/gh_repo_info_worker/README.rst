GitHub Repo Info Worker
===================

.. image:: https://img.shields.io/pypi/v/augur_worker_github.svg
    :target: https://pypi.python.org/pypi/augur_worker_github
    :alt: Latest PyPI version

.. image:: False.png
   :target: False
   :alt: Latest Travis CI build status


Augur Worker that collects GitHub Repo Info data.

This worker is integrated into Augur's worker architecture and can receieve tasks through the broker.

Usage
-----

Installing the Worker
********

To install this worker execute the following command

.. code:: bash

    pip install -e .

Running this Worker
********

To run this worker execute the following command

.. code:: bash

    repo_info_worker


**Note:** Make sure the broker is running before running the worker

Sending Tasks
********

To send a task to this worker manually, send a POST request to the endpoint ``/task``
with the following json. Change ``git_url`` to the url of the GitHub repository you wish
to run the worker against.

.. code:: javascript

    {
        'job_type': 'UPDATE',
        'models': ['repo_info'],
        'given': {
            'git_url': 'https://github.com/openssl/openssl'
        }
    }

Scheduling Tasks
********
To make this worker run periodically add a Housekeeper job in ``augur.config.json``.
To do so, in your ``augur.config.json``, in the Housekeeper section add the following:

.. code:: javascript

    {
        "model": "repo_info",
        "delay": 60,
        "repo_group_id": 0
    }

Set ``delay`` to specify the interval (in seconds) the worker waits before running again.

Set ``repo_group_id`` to the repo_group_id of the Repo Group you wish to run this worker against.
If you wish to run the worker for all repositories specify ``repo_group_id`` to ``0``

Successful Log File
-----
Here is an example of ``worker.log``

.. code-block::

    INFO:root:Making database connections...
    INFO:root:Getting max repo_info_id...
    INFO:root:Starting Flask App with pid: 10950...
    INFO:werkzeug: * Running on http://localhost:51237/ (Press CTRL+C to quit)
    INFO:root:Sending to work on task: {'job_type': 'MAINTAIN', 'models': ['repo_info'], 'given': {'git_url': 'https://github.com/openssl/openssl'}, 'focused_task': 1}
    INFO:root:Running...
    INFO:werkzeug:127.0.0.1 - - [15/Jul/2019 15:09:05] "POST /AUGWOP/task HTTP/1.1" 200 -
    INFO:root:Popped off message: {'git_url': 'https://github.com/openssl/openssl', 'repo_id': 25151}
    INFO:root:Hitting endpoint https://api.github.com/graphql
    INFO:root:Recieved rate limit from headers

    INFO:root:Updated rate limit, you have: 4999 requests remaining.

    INFO:root:Inserting repo info for repo with id:25151, owner:openssl, name:openssl
    INFO:root:Primary Key inserted into repo_info table: [16]
    INFO:root:Inserted info for openssl/openssl
    INFO:root:Telling broker we completed task: {'worker_id': 'com.augurlabs.core.gh_repo_info_worker', 'job_type': 'MAINTAIN', 'repo_id': 25151, 'git_url': 'https://github.com/openssl/openssl'}
    This task inserted: 1 tuples.
