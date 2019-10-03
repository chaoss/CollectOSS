============================
Installation
============================

0. Clone the repository and switch to the ``osd-2019`` branch.

.. code:: bash

   git clone https://github.com/chaoss/augur.git
   cd augur/
   git checkout osd-2019

1. Create a virtual environment in your home environment. Be sure to use
   the correct ``python`` command for your installation of Python 3.6+

.. code:: bash

   python -m venv $HOME/.virtualenvs/augur_env

2. Bring the installation process.

.. code:: bash

   make install

This procces will: - install augur’s backend and its dependencies -
install data collection workers and their dependencies (you will be able
to select which workers you would like: we recommend all of them) -
optionally install augur’s frontend and its dependencies - generate
documentation - prompt the user for **connection credentials for a
Postgres 11 installation**

After Augur is installed, given that you provided a correct set of
credentials you should have a functioning version of Augur.

---------
Usage
---------

To start the frontend and backend processes together, run ``make dev``.
The output should like something like this (note that your process IDs
and network will be different):

::

   sending SIGTERM to node (Brunch) at PID 9239; bash: line 0: kill: (9239) - No such process
   sending SIGTERM to python (Gunicorn) at PID 9224; bash: line 0: kill: (9224) - No such process

   Server     Description       Log                   Monitoring                   PID
   ------------------------------------------------------------------------------------------
   Frontend   Brunch            logs/frontend.log     make monitor-backend         9339
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

*Note: there will be a lot of linting warnings in the frontend section
(indicated here by the …). Don’t worry about them: it’s the last 3 lines
that indicate success.*

Once you see this you’re good to go! Head to the local URL specified in
the frontend logs section (in this example it’s
``http://localhost:8080/``) to check it out!

**Important note: if you chose to set up your own database & installed
the frontend dependencies, please make sure you’ve added a few
repositories to collect data for (instructions for which are directly
below), as otherwise the frontend will not have any data to display!**
