Docker Installation
=====================

Getting Started
---------------

Before we begin, make sure you have everything you need installed:

-  A `PostgreSQL 10 or higher <https://www.postgresql.org/download/>`__ installation

.. code:: bash

  sudo apt-get install postgresql

- `Git <https://git-scm.com/downloads>`__
- `Docker <https://www.docker.com/community-edition>`__
- `Docker Compose <https://docs.docker.com/compose/install/>`__

We provide a database container alongside the data collection/API container and the frontend container, but we also support using an external database. To configure one, follow the instructions in the `data collection <getting-started/installation.html#data-collection>`__ of the installation, and once you're done, return to this guide to install the schemas and get the container running. Make sure to save the credentials for the database; you'll need them again. If you're not sure which to use, we recommend using the database container for ease of setup.

Configuring the containers
--------------------------

Next, we'll need to provide some configuration values so the data collection workers will function correctly. Fill out your values for the following variables in a file called ``env.txt`` in the root ``augur/`` directory. Note that if you're using the database container, you only need the first lines.

.. code:: bash

    AUGUR_GITHUB_API_KEY=<your credentials here>

    //only necessary if connecting to an external database
    AUGUR_DB_USER=<your credentials here>
    AUGUR_DB_PASSWORD=<your credentials here>
    AUGUR_DB_HOST=<your credentials here>
    AUGUR_DB_PORT=<your credentials here>
    AUGUR_DB_NAME=<your credentials here>
    AUGUR_FACADE_REPO_DIRECTORY=<your credentials here>

.. note::

    ``AUGUR_GITHUB_API_KEY`` is needed for the GitHub worker to collect data from the GitHub API. ``AUGUR_FACADE_REPO_DIRECTORY`` is where the Facade worker will store the repos it clones for analysis.

Running the containers
----------------------

To run Augur with the database container:

.. code:: bash

    docker-compose -f docker-compose.yml -f database-compose.yaml up --build

To run Augur without the database container (don't forget to provide your credentials in the ``env.txt`` file, as mentioned above):

.. code:: bash

    docker-compose -f docker-compose.yml up --build

.. note::

    To start the containers in the background, append (``-d``) to the end. You can then use ``docker attatch <container SHA>`` to view the logs of a running container.

To stop the container, run ``docker-compose down --remove-orphans``. The flag is necessary to kill the database container.


Interacting with the Augur
---------------------------

Once you see the following lines, the backend is up and available at ``http://localhost:5000/api/unstable``.

.. code-block:: 

    2020-01-20 20:28:15 954a5f1a3281 augur[13] INFO Starting server...
    [2020-01-20 20:28:15 +0000] [13] [INFO] Starting gunicorn 19.9.0
    [2020-01-20 20:28:15 +0000] [13] [INFO] Listening at: http://0.0.0.0:5000 (13)
    [2020-01-20 20:28:15 +0000] [13] [INFO] Using worker: sync
    [2020-01-20 20:28:15 +0000] [49] [INFO] Booting worker with pid: 49
    [2020-01-20 20:28:15 +0000] [50] [INFO] Booting worker with pid: 50
    [2020-01-20 20:28:15 +0000] [51] [INFO] Booting worker with pid: 51
    [2020-01-20 20:28:15 +0000] [52] [INFO] Booting worker with pid: 52

However, they'll likely fly right past you on your terminal, but once you start seeing messages from the housekeeper and broker, the server should be up. Keep pinging every few moments - we'll have a better fix for this soon.

The frontend will automatically be available on port ``8080``, as the files are hosted statically.

Now you're good to go! Augur will automatically start collecting data in the background and populating the database, and you're free to start exploring the frontend and gathering data.