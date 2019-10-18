---------
Usage
---------

Getting Started
===============

To start the frontend and backend processes together, run ``make dev``.
The output should like something like this (note that your process IDs
and network will be different):

.. code:: bash

   sending SIGTERM to node (npm) at PID 9239; bash: line 0: kill: (9239) - No such process
   sending SIGTERM to python (Gunicorn) at PID 9224; bash: line 0: kill: (9224) - No such process

   Server     Description       Log                   Monitoring                   PID
   ------------------------------------------------------------------------------------------
   Frontend   npm               logs/frontend.log     make monitor-backend         9339
   Backend    Augur/Gunicorn    logs/backend.log      make monitor-frontend        9324

   Monitor both:  make monitor
   Restart and monitor: make dev
   Restart servers:  make dev-start
   Stop servers:  make dev-stop

   ==> logs/backend.log <==

     2019-09-04 12:39:28 parsec augur[19051] INFO Booting broker and its manager...
     2019-09-04 12:39:29 parsec augur[19051] INFO Booting housekeeper...
     2019-09-04 12:39:51 parsec root[19051] INFO Starting update processes...
     2019-09-04 12:39:52 parsec root[19083] INFO Housekeeper spawned issues model updater process for subsection 0 with PID 19083
     2019-09-04 12:39:52 parsec augur[19051] INFO Starting server...
     2019-09-04 12:39:52 parsec root[19084] INFO Housekeeper spawned pull_requests model updater process for subsection 0 with PID 19084
     [2019-09-04 12:39:52 -0500] [19051] [INFO] Starting gunicorn 19.9.0
     [2019-09-04 12:39:52 -0500] [19051] [INFO] Listening at: http://0.0.0.0:5000 (19051)
     [2019-09-04 12:39:52 -0500] [19051] [INFO] Using worker: sync
     [2019-09-04 12:39:52 -0500] [19085] [INFO] Booting worker with pid: 19085
     [2019-09-04 12:39:52 -0500] [19086] [INFO] Booting worker with pid: 19086
     [2019-09-04 12:39:52 -0500] [19087] [INFO] Booting worker with pid: 19087
     [2019-09-04 12:39:53 -0500] [19088] [INFO] Booting worker with pid: 19088
     [2019-09-04 12:39:53 -0500] [19089] [INFO] Booting worker with pid: 19089
     [2019-09-04 12:39:53 -0500] [19090] [INFO] Booting worker with pid: 19090
     [2019-09-04 12:39:53 -0500] [19091] [INFO] Booting worker with pid: 19091
     [2019-09-04 12:39:53 -0500] [19092] [INFO] Booting worker with pid: 19092
     127.0.0.1 - [04/Sep/2019:12:40:04 -0500] - GET /api/unstable HTTP/1.1

   ==> logs/frontend.log <==

       ...
       ...
       ...

     Version: typescript 3.5.3, tslint 5.18.0
     Time: 9311ms

     App running at:
     - Local:   http://localhost:8080/
     - Network: http://192.168.1.141:8080/


.. note:: 

  You'll likely see some linting warnings in the frontend section
  (indicated here by the …). Don’t worry about them: it’s the last 3 lines
  that indicate success.

Once you see this you’re good to go! Head to the local URL specified in
the frontend section (in this example it’s
``http://localhost:8080/``) to check it out!

.. note::

  Important note: if you chose to install and configure your own database 
  and also installed the frontend dependencies, please make sure you’ve added a few
  repositories to collect data for (instructions `here <#db>`_), as otherwise the frontend will not have any data to display!

Backend
========

Augur provides a few handy scripts and options for controlling the backend server. They're broken up into 3 main categories: ``run``, ``db``, and ``util``.

``run``
========
The collection of the ``run`` commands controls the actual starting and stopping of the server. For right now, only the default command ``augur run`` is implemented. This will initialize the backend server by itself and show the logs in the terminal. Press ``CTRL-C`` to kill it.

Example\:

.. code:: bash

  # to run just the backend server
  augur run


``db``
========
The collection of the ``db`` commands is for interacting with the database. For right now, only the command ``augur db add_repos /path/to/file.csv`` is implemented. When given a path to correctly formatted (see below) ``.csv`` file, it will insert each repo specified in the file into its corresponding repo group in the database specified in ``augur.config.json``.

Format:
The ``.csv`` file must have the following format:
``<repo_group_id>,<git_repo_url>`` where ``<repo_group_id>`` is a valid repository group ID, and ``<git_repo_url>`` is the url to the repository's Git repository, e.g. ``https://github.com/chaoss/augur.git``. Put each pairing of repo and ID on a separate line, and leave no spaces between lines. You don't need any columns headers either.

If you don't know a repo group ID, or don't care what group it's in, just use ``1``.

Example\:

.. code:: bash

  # to add repos to the database
  augur db add_repos repos.csv

  # contents of repos.csv
  1,https://github.com/chaoss/augur.git
  2,https://github.com/chaoss/wg-evolution.git
  2,https://github.com/chaoss/metrics.git

``util``
========
The collection of the ``util`` commands provides various miscelleanous functions that don't fit otherwise. For the sake of brevity for the time being, we'll only cover the most useful one (IMHO): ``augur util shell``. 

This command will drop you into an iPython shell with an instance of Augur's ``Application`` class already instantiated and ready for use. You can access this via the ``app`` variable once you're in the shell. See the `Python Library documentation <python.html>`_. for more info.

When you're finished in the iPython shell, press ``CTRL + D`` or type ``exit()`` in the interpreter and then press enter.

Example\:

.. code:: bash

  # drop into the shell
  augur util shell

  # inside the shell
  -- Augur Shell --
  augur [1]: print(app)
  <augur.application.Application object at 0x10966b860>

  augur [2]: print(app.metrics.issues_new(20, 21000))
     repo_name                      date  issues
  0        rails 2009-04-01 00:00:00+00:00       1
  1        rails 2009-04-17 00:00:00+00:00       1
  2        rails 2009-04-28 00:00:00+00:00       1
  3        rails 2011-04-28 00:00:00+00:00       7
  ...      ...                                 ...
  2092     rails 2019-09-22 00:00:00+00:00       1
  2093     rails 2019-09-23 00:00:00+00:00       4
  2094     rails 2019-09-24 00:00:00+00:00       4

  [2095 rows x 3 columns]

  augur [3]: exit()


Frontend
========

To start the frontend server, go into the ``frontend/`` directory and run ``npm run serve``. After the server spins up, you should see a line like this at the end\:

.. code:: bash

  App running at:
  - Local:   http://localhost:8080/
  - Network: http://192.168.1.141:8080/

Navigate to either link to see the frontend in action! Note that your ports could be different, and your network address won't be the same either.