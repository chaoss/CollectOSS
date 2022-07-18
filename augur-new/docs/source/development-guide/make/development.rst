Development
============

**THIS SECTION IS UNDER CONSTRUCTION.**

If you have questions or would like to help please open an issue on GitHub_.

.. _GitHub: https://github.com/chaoss/augur/issues

These commands are used to control Augur's backend and frontend servers simultaneously.

--------------

``make dev``
-------------
**If the above command doesn't work, try running ``make dev-start`` instead**.

This command starts the frontend and backend servers together in the background. The output of the backend are in ``logs/augur.log``, and the logs for the frontend are in ``logs/frontend.log``.
The backend output should like something like this (note that your process IDs and hostname will be different)::

     2020-03-22 12:39:28 kaiyote augur[19051] INFO Booting broker and its manager...
     2020-03-22 12:39:29 kaiyote augur[19051] INFO Booting housekeeper...
     2020-03-22 12:39:51 kaiyote root[19051] INFO Starting update processes...
     2020-03-22 12:39:52 kaiyote root[19083] INFO Housekeeper spawned issues model updater process for subsection 0 with PID 19083
     2020-03-22 12:39:52 kaiyote augur[19051] INFO Starting server...
     2020-03-22 12:39:52 kaiyote root[19084] INFO Housekeeper spawned pull_requests model updater process for subsection 0 with PID 19084
     [2020-03-22 12:39:52 -0500] [19051] [INFO] Starting gunicorn 19.9.0
     [2020-03-22 12:39:52 -0500] [19051] [INFO] Listening at: http://0.0.0.0:5000 (19051)
     [2020-03-22 12:39:52 -0500] [19051] [INFO] Using worker: sync
     [2020-03-22 12:39:52 -0500] [19085] [INFO] Booting worker with pid: 19085
     [2020-03-22 12:39:52 -0500] [19086] [INFO] Booting worker with pid: 19086
     [2020-03-22 12:39:52 -0500] [19087] [INFO] Booting worker with pid: 19087
     [2020-03-22 12:39:53 -0500] [19088] [INFO] Booting worker with pid: 19088
     [2020-03-22 12:39:53 -0500] [19089] [INFO] Booting worker with pid: 19089
     [2020-03-22 12:39:53 -0500] [19090] [INFO] Booting worker with pid: 19090
     [2020-03-22 12:39:53 -0500] [19091] [INFO] Booting worker with pid: 19091
     [2020-03-22 12:39:53 -0500] [19092] [INFO] Booting worker with pid: 19092

The frontend output should like something like this::
    
       # a whole bunch of stuff about compiling
       ...
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
  that indicate success. Once you see this you’re good to go! Head to the specified URL 
  (in this example it’s ``http://localhost:8080/``) to check it out!

--------------

``make dev-stop``
------------------
Stops both the frontend and the backend server.

Example\:

.. code-block:: bash

    $ make dev-stop
