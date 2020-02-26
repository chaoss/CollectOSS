~~~~~~~~~~~~~~~~~
``make`` Commands
~~~~~~~~~~~~~~~~~

These are the commands available in the ``Makefile`` in the root ``augur/`` directory.
If ``make`` is run by itself (literally just the command ``make``) in the root ``augur/`` directory 
a condensed version of each description will be displayed for quick reference.

============
Installation
============

``make install``
----------------
Installs the project dependencies, sets up default configuration file, and gathers database credentials.

.. code-block:: bash

  # example usage

  > make install

``make clean``
----------------
Removes logs, caches, and some other cruft that can get annoying. Use when things aren't building properly or you think an old version of augur is getting in the way.

.. code-block:: bash

  # example usage

  > make clean

``make rebuild``
----------------
Used in conjunction with ``make clean`` to remove all build/compiled files and binaries and reinstall the project. Useful for upgrading in place.

.. code-block:: bash

  # example usage

  > make rebuild

============
Development
============

``make dev``
-------------
Starts the frontend and backend servers together.
The output should like something like this (note that your process IDs
and network will be different):

.. code-block:: bash

  # example usage

  > make dev
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
Start just the frontend server. To run just the backend server, see the ``augur`` commands `documentation`_.

.. _documentation: augur-commands.html#run

``make augur``
---------------
Start augur in the background.

``make collect``
-----------------
Start all the installed data collection workers in the background. Use ``make status`` to quickly 
check the logs after you've started them.

``make run``
-------------
Start both augur AND all the installed data collection workers in the background. Use ``make status`` to quickly 
check the logs after you've started them.

``make status``
----------------
Display the last 10 lines of all augur and worker log/error files.


=======
Testing
=======
These commands are used to run specific subsets of unit tests. We use ``tox`` to manage the test environments, and ``pytest`` as the test runner. Each of these commands except for ``make test-pythons-versions`` will use your default Python version, while ``make test-python-versions`` will test all supported Python versions. 

``make test``
-------------
Runs available  tests for both the metric functions and their API endpoints.

.. code-block:: bash

  # example usage

  # this will run ALL tests for JUST the issue model
  > make test

``make test-metrics``
------------------------
Runs unit tests for the metric functions.

.. code-block:: bash

  # example usage

  # this will run ALL metric function unit tests
  > make test-metrics

``make test-metrics-api``
--------------------------
Runs tests for the metrics API.

.. code-block:: bash

  # example usage

  # this will run ALL metric API tests
  > make test-metrics-api

``make test-python-versions``
-----------------------------
Runs all tests under all currently supported versions of Python (3.6 and above).

.. code-block:: bash

  # example usage

  # this will run ALL metric API tests
  > make test-python-versions

==============
Documentation
==============

Before making any documentation changes, please read the `documentation guide <../../documentation.html>`_.

``make docs``
--------------
Generate both library and API documentation.

.. code-block:: bash

  # example usage

  > make docs

``make library-docs``
----------------------
Generate the library documentation (this documentation).

.. code-block:: bash

  # example usage

  > make library-docs


``make library-docs-view``
--------------------------
Generate the library documentation, and automatically open a new browser tab to view it.

.. code-block:: bash

  # example usage

  > make library-docs-view

``make api-docs``
------------------
Generate the API documentation.

.. code-block:: bash

  # example usage

  > make api-ddocs

``make api-docs-view``
-----------------------
Generate the API documentation, and automatically open a new browser tab to view it.

.. code-block:: bash

  # example usage

  > make api-docs-view
