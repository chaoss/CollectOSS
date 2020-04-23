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
  > 2020-04-08 13:03:56 laputa augur[31088] INFO Cleaning up old Augur processes. Just a moment please...
  > 2020-04-08 13:03:59 laputa augur[31088] INFO Booting broker and its manager...
  > 2020-04-08 13:03:59 laputa augur[31088] INFO Booting housekeeper...
  > 2020-04-08 13:04:00 laputa root[31088] INFO Starting update processes...
  > 2020-04-08 13:04:00 laputa augur[31088] INFO Housekeeper has finished booting.
  > 2020-04-08 13:04:00 laputa augur[31088] INFO Starting server...
  > [2020-04-08 13:04:00 -0500] [31088] [INFO] Starting gunicorn 19.9.0
  > [2020-04-08 13:04:00 -0500] [31088] [INFO] Listening at: http://0.0.0.0:5000 (31088)
  > [2020-04-08 13:04:00 -0500] [31088] [INFO] Using worker: sync
  > [2020-04-08 13:04:00 -0500] [31403] [INFO] Booting worker with pid: 31403
  > [2020-04-08 13:04:00 -0500] [31404] [INFO] Booting worker with pid: 31404
  > [2020-04-08 13:04:00 -0500] [31405] [INFO] Booting worker with pid: 31405
  > [2020-04-08 13:04:00 -0500] [31406] [INFO] Booting worker with pid: 31406
  > 2020-04-08 13:04:02 laputa root[31395] INFO Housekeeper spawned commits model updater process for repo group id 0 with PID 31395
  > 2020-04-08 13:04:02 laputa root[31397] INFO Housekeeper spawned contributors model updater process for repo group id 0 with PID 31397
  > 2020-04-08 13:04:02 laputa root[31396] INFO Housekeeper spawned pull_requests model updater process for repo group id 0 with PID 31396
  > 2020-04-08 13:04:02 laputa root[31398] INFO Housekeeper spawned insights model updater process for repo group id 0 with PID 31398
  > 2020-04-08 13:04:02 laputa root[31394] INFO Housekeeper spawned repo_info model updater process for repo group id 0 with PID 31394
  > 2020-04-08 13:04:02 laputa root[31400] INFO Housekeeper spawned value model updater process for repo group id 0 with PID 31400
  > 2020-04-08 13:04:02 laputa root[31393] INFO Housekeeper spawned issues model updater process for repo group id 0 with PID 31393
  > 2020-04-08 13:04:02 laputa root[31399] INFO Housekeeper spawned badges model updater process for repo group id 0 with PID 31399
  > ...


To start the backend server without the housekeeper::

  $ augur run --disable-housekeeper

  # successful output looks like:
  > 2020-04-08 13:03:56 laputa augur[31088] INFO Cleaning up old Augur processes. Just a moment please...
  > 2020-04-08 13:03:59 laputa augur[31088] INFO Booting broker and its manager...
  > 2020-04-08 13:04:00 laputa augur[31088] INFO Starting server...
  > [2020-04-08 13:04:00 -0500] [31088] [INFO] Starting gunicorn 19.9.0
  > [2020-04-08 13:04:00 -0500] [31088] [INFO] Listening at: http://0.0.0.0:5000 (31088)
  > [2020-04-08 13:04:00 -0500] [31088] [INFO] Using worker: sync
  > [2020-04-08 13:04:00 -0500] [31403] [INFO] Booting worker with pid: 31403
  > [2020-04-08 13:04:00 -0500] [31404] [INFO] Booting worker with pid: 31404
  > [2020-04-08 13:04:00 -0500] [31405] [INFO] Booting worker with pid: 31405
  > [2020-04-08 13:04:00 -0500] [31406] [INFO] Booting worker with pid: 31406
  > ...

To start the backend server and skip the process cleanup::

  $ augur run --skip-cleanup

  # successful output looks like:
  > 2020-04-08 13:03:59 laputa augur[31088] INFO Booting broker and its manager...
  > 2020-04-08 13:03:59 laputa augur[31088] INFO Booting housekeeper...
  > 2020-04-08 13:04:00 laputa root[31088] INFO Starting update processes...
  > 2020-04-08 13:04:00 laputa augur[31088] INFO Housekeeper has finished booting.
  > 2020-04-08 13:04:00 laputa augur[31088] INFO Starting server...
  > [2020-04-08 13:04:00 -0500] [31088] [INFO] Starting gunicorn 19.9.0
  > [2020-04-08 13:04:00 -0500] [31088] [INFO] Listening at: http://0.0.0.0:5000 (31088)
  > [2020-04-08 13:04:00 -0500] [31088] [INFO] Using worker: sync
  > [2020-04-08 13:04:00 -0500] [31403] [INFO] Booting worker with pid: 31403
  > [2020-04-08 13:04:00 -0500] [31404] [INFO] Booting worker with pid: 31404
  > [2020-04-08 13:04:00 -0500] [31405] [INFO] Booting worker with pid: 31405
  > [2020-04-08 13:04:00 -0500] [31406] [INFO] Booting worker with pid: 31406
  > 2020-04-08 13:04:02 laputa root[31395] INFO Housekeeper spawned commits model updater process for repo group id 0 with PID 31395
  > 2020-04-08 13:04:02 laputa root[31397] INFO Housekeeper spawned contributors model updater process for repo group id 0 with PID 31397
  > 2020-04-08 13:04:02 laputa root[31396] INFO Housekeeper spawned pull_requests model updater process for repo group id 0 with PID 31396
  > 2020-04-08 13:04:02 laputa root[31398] INFO Housekeeper spawned insights model updater process for repo group id 0 with PID 31398
  > 2020-04-08 13:04:02 laputa root[31394] INFO Housekeeper spawned repo_info model updater process for repo group id 0 with PID 31394
  > 2020-04-08 13:04:02 laputa root[31400] INFO Housekeeper spawned value model updater process for repo group id 0 with PID 31400
  > 2020-04-08 13:04:02 laputa root[31393] INFO Housekeeper spawned issues model updater process for repo group id 0 with PID 31393
  > 2020-04-08 13:04:02 laputa root[31399] INFO Housekeeper spawned badges model updater process for repo group id 0 with PID 31399
  > ...

.. note::

    Of course, your computer name (mine is ``laputa``) and process IDs (shown in brackets after ``root`` and anytime you see the word ``PID``) will be different.
