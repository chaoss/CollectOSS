Auto starting Augur Workers
----------------

To configure Augur's data collection workers to run continuously on startup, you set the workers parameter `switch` to `1`, instead of the default of `0`. The following workers support auto starting. We are still working the kinks out of autostart on some platforms, so please share your logs and any issues you encounter by opening up a GitHub issue. 

.. code-block:: json


            "pull_request_worker": {
                    "port": 51552,
                    "switch": 1,
                    "workers": 1
            },  
            "github_worker": {
                    "port": 51553,
                    "switch": 1,
                    "workers": 1
            },
            "insight_worker": {
                    "port": 51554,
                    "switch": 1,
                    "workers": 1
            },
            "repo_info_worker": {
                    "port": 51555,
                    "switch": 1,
                    "workers": 1
            },
            "value_worker": {
                    "port": 51556,
                    "switch": 1,
                    "workers": 1,
                    "scc_bin": '/home/<user>/go/bin/scc'
            }