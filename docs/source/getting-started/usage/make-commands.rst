~~~~~~~~~~~~~~~~~
Makefile Commands
~~~~~~~~~~~~~~~~~

These are the commands available in the ``Makefile`` in the root ``augur/`` directory.

============
Installation
============

``make install``
----------------
Run ``make install`` to install the project and set up the configuration file.

``make clean``
----------------
Run ``make clean`` to remove logs, caches, and other cruft that can get annoying.

``make rebuild``
----------------
``make rebuild`` is used to conjunction with ``make clean`` to remove all build/compiled files or binaries and reinstall the project. Useful for upgrading in place.

============
Development
============

``make dev``
-------------
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

``make frontend``
------------------
Run ``make frontend`` to start just the frontend server. To run just the backend server, see the ``augur`` commands `documentation`_.

.. _documentation: augur-commands.html#run

=======
Testing
=======

``make test``
-------------
Run ``make test`` to run all available unit tests for both the metric functions and their API endpoints.

Use the ``MODEL`` parameter to run tests for *one* specific model.

Example\:

.. code-block:: bash

  # this will run ALL tests for the issue model
  make test MODEL=issue

``make test-functions``
------------------------
Run ``make test-functions`` to run all available unit tests for the metric functions.

Use the ``MODEL`` parameter to run tests for *one* specific model.

Example\:

.. code-block:: bash

  # this will run only metric function tests for the issue model
  make test-functions MODEL=issue


``make test-routes``
------------------------
Run ``make test-routes`` to run all available unit tests for the metric API endpoints.

Use the ``MODEL`` parameter to run tests for *one* specific model.

Example\:

.. code-block:: bash

  # this will run only API endpoint tests for the issue model
  make test-routes MODEL=issue

==============
Documentation
==============

``make docs``
--------------
Run ``make docs`` to generate all documentation.

``make python-docs``
--------------------
Run ``make python-docs`` to generate the library documentation.

Run ``make python-docs`` to generate the library documentation, and then to automatically open a new browser tab to view it.

``make api-docs``
------------------
Run ``make api-docs`` to generate the API documentation.

Run ``make api-docs`` to generate the API documentation, and then to automatically open a new browser tab to view it.