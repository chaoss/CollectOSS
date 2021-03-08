=================
Backend Commands
=================

``augur backend``
====================
The ``augur backend`` CLI group is for controlling Augur's API server & data collection workers. All commands are invoked like::

  $ augur backend <command name>

``start``
============
This command is for starting Augur's API server & (optionally) data collection workers. Example usages are shown below the parameters. After starting up, it will run indefinitely (but might not show any output, unless it's being queried or the housekeeper is working).

--disable-housekeeper      Flag that turns off the housekeeper. Useful for testing the REST API or if you want to pause data collection without editing your config.

--skip-cleanup      Flag that disables the old process cleanup that runs before Augur starts. Useful for Python scripts where Augur needs to be run in the background: see the `test/api/runner.py` file for an example.

To start the backend as normal::

  $ augur backend start

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

To start the backend as a background process: 

  $ nohup augur backend start >logs/base.log 2>logs/base.err &
  # successful output looks like the generation of standard Augur logfiles in the logs/ directory

To start the backend server without the housekeeper::

  $ augur backend start --disable-housekeeper

  # successful output looks like:
  > [14467] augur [INFO] Augur application initialized
  > [14467] augur [INFO] Using config file: /Users/carter/workspace/chaoss/augur/augur.config.json
  > [14467] augur [INFO] Starting Gunicorn webserver...
  > [14467] augur [INFO] Augur is running at: http://0.0.0.0:5000
  > [14467] augur [INFO] Gunicorn server logs & errors will be written to logs/gunicorn.log


``stop``
---------
**Gracefully** attempts to stop all currently running backend Augur processes, including any workers. Will only work in a virtual environment.

Example usage::

  # to stop the server and workers
  $ augur backend stop

  # successful output looks like:
  > CLI: [backend.stop] [INFO] Stopping process 33607
  > CLI: [backend.stop] [INFO] Stopping process 33775
  > CLI: [backend.stop] [INFO] Stopping process 33776
  > CLI: [backend.stop] [INFO] Stopping process 33777

``kill``
---------
**Forcefully** terminates (using ``SIGKILL``) all currently running backend Augur processes, including any workers. Will only work in a virtual environment.
Should only be used when ``augur backend stop`` is not working.

Example usage::

  # to stop the server and workers
  $ augur backend kill

  # successful output looks like:
  > CLI: [backend.kill] [INFO] Killing process 87340
  > CLI: [backend.kill] [INFO] Killing process 87573
  > CLI: [backend.kill] [INFO] Killing process 87574
  > CLI: [backend.kill] [INFO] Killing process 87575
  > CLI: [backend.kill] [INFO] Killing process 87576


``processes``
--------------
Outputs the process ID (PID) of all currently running backend Augur processes, including any workers. Will only work in a virtual environment.

Example usage::

  # to stop the server and workers
  $ augur backend processes

  # successful output looks like:
  > CLI: [backend.processes] [INFO] Found process 14467
  > CLI: [backend.processes] [INFO] Found process 14725


