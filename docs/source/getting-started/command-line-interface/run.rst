============
Run Command
============

``augur run``
=============

The ``augur run`` command is for starting Augur's backend server. Example usages are shown below the parameters.

--disable-housekeeper      Flag that turns off the housekeeper. Useful for testing the REST API or if you want to pause data collection without editing your config.

--skip-cleanup      Flag that disables the old process cleanup that runs before Augur starts. Useful for Python scripts where Augur needs to be run in the background: see the `test/api/runner.py` file for an example.

To start the backend as normal::

  $ augur run

  # successful output looks like:
  >[43389] augur [INFO] Augur application initialized
  >[43389] augur [INFO] Booting manager
  >[43389] augur [INFO] Booting broker
  >[43389] augur.housekeeper [INFO] Booting housekeeper
  >[43389] augur.housekeeper [INFO] Preparing housekeeper jobs
  >[43389] augur.housekeeper [INFO] Scheduling update processes
  >[43389] augur [INFO] Booting facade_worker #1
  >[43389] augur [INFO] Booting github_worker #1
  >[43389] augur [INFO] Booting linux_badge_worker #1
  >[43389] augur [INFO] Booting pull_request_worker #1
  >[43389] augur [INFO] Booting repo_info_worker #1
  >[43389] augur [INFO] Booting contributor_worker #1
  >[43389] augur [INFO] Booting gitlab_issues_worker #1
  >[43389] augur [INFO] Booting release_worker #1
  >[43389] augur [INFO] Starting Gunicorn server in the background...
  >[43389] augur [INFO] Housekeeper update process logs will now take over.
  >[43645] augur.jobs.insights [INFO] Housekeeper spawned insights model updater process for repo group id 0
  >[43639] augur.jobs.issues [INFO] Housekeeper spawned issues model updater process for repo group id 0
  >[43646] augur.jobs.badges [INFO] Housekeeper spawned badges model updater process for repo group id 0
  >[43640] augur.jobs.pull_request_commits [INFO] Housekeeper spawned pull_request_commits model updater process for repo group id 0
  >[43642] augur.jobs.commits [INFO] Housekeeper spawned commits model updater process for repo group id 0
  >[43647] augur.jobs.value [INFO] Housekeeper spawned value model updater process for repo group id 0
  >[43644] augur.jobs.contributors [INFO] Housekeeper spawned contributors model updater process for repo group id 0
  >[43641] augur.jobs.repo_info [INFO] Housekeeper spawned repo_info model updater process for repo group id 0
  >[43643] augur.jobs.pull_requests [INFO] Housekeeper spawned pull_requests model updater process for repo group id 0
  >[43648] augur.jobs.pull_request_files [INFO] Housekeeper spawned pull_request_files model updater process for repo group id 0
  > ...
  > From this point on, the housekeeper and broker logs detailing the worker's progress will take over


To start the backend server without the housekeeper::

  $ augur run --disable-housekeeper

  # successful output looks like:
    > [53524] augur [INFO] Augur application initialized
    > [53524] augur [INFO] Starting Gunicorn server in the background...
    > [53524] augur [INFO] Gunicorn server logs will be written to gunicorn.log
    > [53524] augur [INFO] Augur is still running...don't close this process!
  > ...

To start the backend server and skip the process cleanup::

  $ augur run --skip-cleanup

  # successful output looks the same as without the flag

