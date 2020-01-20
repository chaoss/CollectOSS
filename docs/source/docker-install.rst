Docker Installation
=====================

Before we begin, make sure you have everything you need installed:

-  A `PostgreSQL 10 or higher <https://www.postgresql.org/download/>`__ installation

.. code:: bash

  sudo apt-get install postgresql

- `Git <https://git-scm.com/downloads>`__
- `Docker <https://www.docker.com/community-edition>`__

Before starting up the container, you'll need to setup a database. Follow the instructions in the 
`data collection <getting-started/installation.html#data-collection>`__ of the installation, and once you're done, return to this guide to install the schemas and get the container running. Make sure to save the credentials for the database; you'll need them again.


Installing the DB schema
-------------------------

To install the necessary schemas and load a sample dataset, you'll need to clone augur to get access to the ``.sql`` files.

After you run ``git clone https://github.com/chaoss/augur.git``, to install the schema:

.. code:: bash

    psql -h localhost -d augur -U augur -p 5432 -a -w -f persistence_schema/1-schema.sql
    psql -h localhost -d augur -U augur -p 5432 -a -w -f persistence_schema/2-augur_data.sql
    psql -h localhost -d augur -U augur -p 5432 -a -w -f persistence_schema/3-augur_operations.sql
    psql -h localhost -d augur -U augur -p 5432 -a -w -f persistence_schema/4-spdx.sql
    psql -h localhost -d augur -U augur -p 5432 -a -w -f persistence_schema/5-seed-data.sql
    psql -h localhost -d augur -U augur -p 5432 -a -w -f persistence_schema/6-schema_update_8.sql
    psql -h localhost -d augur -U augur -p 5432 -a -w -f persistence_schema/7-schema_update_9.sql

    psql -h localhost -d augur -U augur -p augur -a -w -c "UPDATE augur_data.settings SET VALUE = 'repos/' WHERE setting='repo_directory';"

And load a small sample dataset:

.. code:: 

    persistence_schema/db_load.sh localhost augur augur 5432

Running the container
----------------------

Once you've set the database up, fill out your values for the following variables in a file called ``env.txt`` in the root ``augur/`` directory:

.. code:: bash

    AUGUR_DB_USER=<your credentials here>
    AUGUR_DB_PASSWORD=<your credentials here>
    AUGUR_DB_HOST=<your credentials here>
    AUGUR_DB_PORT=<your credentials here>
    AUGUR_DB_NAME=<your credentials here>
    AUGUR_GITHUB_API_KEY=<your credentials here>
    AUGUR_FACADE_REPO_DIRECTORY=<your credentials here>
    AUGUR_PORT=5000

.. note::

    ``AUGUR_GITHUB_API_KEY`` is needed for the GitHub worker to collect data from the GitHub API. ``AUGUR_FACADE_REPO_DIRECTORY`` is where the Facade worker will store the repos it clones for analysis. Change ``AUGUR_PORT`` only if port 5000 is already taken on your machine.

To start the container:

.. code:: bash

    docker run -p $AUGUR_PORT:$AUGUR_PORT --name augur --env-file env.txt augurlabs/augur:latest

Wait until you see the following lines:

.. code-block:: 

    2020-01-20 20:28:15 954a5f1a3281 augur[13] INFO Starting server...
    [2020-01-20 20:28:15 +0000] [13] [INFO] Starting gunicorn 19.9.0
    [2020-01-20 20:28:15 +0000] [13] [INFO] Listening at: http://0.0.0.0:5000 (13)
    [2020-01-20 20:28:15 +0000] [13] [INFO] Using worker: sync
    [2020-01-20 20:28:15 +0000] [49] [INFO] Booting worker with pid: 49
    [2020-01-20 20:28:15 +0000] [50] [INFO] Booting worker with pid: 50
    [2020-01-20 20:28:15 +0000] [51] [INFO] Booting worker with pid: 51
    [2020-01-20 20:28:15 +0000] [52] [INFO] Booting worker with pid: 52

Now you're good to go! Augur will automatically start collecting data in the background and populating the database.