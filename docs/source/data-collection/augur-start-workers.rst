---------------------------
Auto starting Augur Workers
---------------------------

To configure Augur's data collection workers to run continuously on startup, you set the workers parameter `switch` to `1`, instead of the default of `0`. The following workers support auto starting. We are still working the kinks out of autostart on some platforms, so please share your logs and any issues you encounter by opening up a GitHub issue. 

Sometimes autostarting is not a good idea, and you want to be able to start workers up when you are ready. We have a command for starting the workers: 

To start Augur and the Workers: ``> make run``

To start Augur alone: ``> make augur``

To start the Workers after starting Augur: ``> make collect``

Enabling and Disabling Parts of Data Collection
-------------------------------------------------

There are two parts of the augur.config.json file that control what data is collected. In general, using the default file built on installation will be effective. When collecting larger sets of data, you may want to sequence data collection by running these workers before initiating the remainder : 

1. Facade worker (``facade_worker``)
2. GitHub worker (``github_worker ``)
3. Pull Request worker (``pull_request_worker``)
4. Repo Info worker (``repo_info_worker``)
5. Linux Badge Worker (``linux_badge_worker``)

.. note::

    The Github Worker has two data collection models. One is for issues, and the other is for contributors. If you are doing a large data collection we advise you to delete the contributors model until all data is collected, and then restart Augur with the contributors model enabled. This will create a more consistent and uniform collection of "canonical users". The Contributors Model resolves multiple email addresses used by a single contributor through the GitHub API and other platform APIs. If it is run after initial collection of the Pull Request, Issues, and facade-commits models, the canonical email selected is more likely to be the users preferred and thus more easily identifiable email. 


Workers Block of ``augur.config.json``
---------------------------------------

.. code-block:: json

    {
        "facade_worker": {
            "port": 56111,
            "repo_directory": "/home/sean/github/augur-test/repos/",
            "switch": 0,
            "workers": 1
        },
        "github_worker": {
            "port": 56211,
            "switch": 0,
            "workers": 2
        },
        "insight_worker": {
            "port": 56311,
            "switch": 0,
            "workers": 1
        },
        "pull_request_worker": {
            "port": 56411,
            "switch": 0,
            "workers": 1
        },
        "repo_info_worker": {
            "port": 56511,
            "switch": 0,
            "workers": 1
        },
        "value_worker": {
            "port": 56611,
            "scc_bin": "/home/sean/go/bin/scc",
            "switch": 0,
            "workers": 1
        },
        "metric_status_worker": {
            "port": 56711,
            "switch": 0,
            "workers": 1
        },
        "linux_badge_worker": {
            "port": 56811,
            "switch": 0,
            "workers": 1
        },
        "license_worker": {
            "port": 51242,
            "switch": 0,
            "workers": 1,
            "tagfile": "3.0.tag"
        }
    }

Models Block of ``augur.config.json``
--------------------------------------

You can disable the contributors block by adding three underscores and the word disabled to the end of the model name, as illustrated below in the contributors model: ``"model": "contributors___disabled"``.

.. code-block:: json

    {
        "Housekeeper": {
            "jobs": [
                {
                    "focused_task": 1,
                    "delay": 150000,
                    "given": [
                        "github_url"
                    ],
                    "model": "issues",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "github_url"
                    ],
                    "model": "contributors___disabled",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": [
                        "github_url"
                    ],
                    "model": "repo_info",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": [
                        "repo_group"
                    ],
                    "model": "commits",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "github_url"
                    ],
                    "model": "pull_requests",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "insights",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "badges",
                    "repo_group_id": 0
                },
                {
                    "model": "value",
                    "delay": 100000,
                    "given": [
                        "git_url"
                    ],
                    "repo_group_id": 0
                }
            ]
        }
    }


