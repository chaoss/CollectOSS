Docker Installation
=====================

Before we begin, make sure you have everything you need installed:

-  A `PostgreSQL 10 or higher <https://www.postgresql.org/download/>`__ installation

.. code:: bash

  sudo apt-get install postgresql

- `Git <https://git-scm.com/downloads>`__
- `Docker <https://www.docker.com/community-edition>`__
- `Docker Compose <https://docs.docker.com/compose/install/>`__

We provide a database container alongside the data collection/API container and the frontend container, but we also support using an external database. To configure one, follow the instructions in the `data collection <getting-started/installation.html#data-collection>`__ of the installation, and once you're done, return to this guide to install the schemas and get the container running. Make sure to save the credentials for the database; you'll need them again.


Installing the DB schema
-------------------------

To install the necessary schemas and load a sample dataset, you'll need to clone augur to get access to the ``.sql`` files. While still connected to your database server, run the following commands to clone the repo and install the schemas. ``db_name`` is the name of the database you configured in the previous section, ``$db_user`` is the name of the role you created, and ``$db_port`` is the port on which Postgres is accepting connections (usually, this is the default port ``5432``).

.. code:: bash

    git clone https://github.com/chaoss/augur.git
    cd augur/
    psql -h localhost -d $db_name -U $db_user -p $db_port -a -w -f persistence_schema/generate/1-schema.sql
    psql -h localhost -d $db_name -U $db_user -p $db_port -a -w -f persistence_schema/generate/2-augur_data.sql
    psql -h localhost -d $db_name -U $db_user -p $db_port -a -w -f persistence_schema/generate/3-augur_operations.sql
    psql -h localhost -d $db_name -U $db_user -p $db_port -a -w -f persistence_schema/generate/4-spdx.sql
    psql -h localhost -d $db_name -U $db_user -p $db_port -a -w -f persistence_schema/generate/5-seed-data.sql
    psql -h localhost -d $db_name -U $db_user -p $db_port -a -w -f persistence_schema/enerate/6-schema_update_8.sql
    psql -h localhost -d $db_name -U $db_user -p $db_port -a -w -f persistence_schema/generate/7-schema_update_9.sql

    psql -h localhost -d augur -U augur -p 5432 augur -a -w -c "UPDATE augur_data.settings SET VALUE = 'repos/' WHERE setting='repo_directory';"

And load a small sample dataset:

.. code:: bash

    persistence_schema/db_load.sh localhost augur augur 5432

Configuring the containers
--------------------------

Next, fill out your values for the following variables in a file called ``env.txt`` in the root ``augur/`` directory. Note that if you're using the database container, you only need the first two lines.

.. code:: bash

    AUGUR_GITHUB_API_KEY=<your credentials here>
    AUGUR_PORT=5000

    //only necessary if connecting to an external database
    AUGUR_DB_USER=<your credentials here>
    AUGUR_DB_PASSWORD=<your credentials here>
    AUGUR_DB_HOST=<your credentials here>
    AUGUR_DB_PORT=<your credentials here>
    AUGUR_DB_NAME=<your credentials here>
    AUGUR_FACADE_REPO_DIRECTORY=<your credentials here>

.. note::

    ``AUGUR_GITHUB_API_KEY`` is needed for the GitHub worker to collect data from the GitHub API. ``AUGUR_FACADE_REPO_DIRECTORY`` is where the Facade worker will store the repos it clones for analysis. Change ``AUGUR_PORT`` only if port 5000 is already taken on your machine.

Running the containers
----------------------

Running with the database container
=======================================

To start the container:

.. code:: bash

    docker-compose -f docker-compose.yml -f database-compose.yaml up --build

.. note::

    To start it in the background, append (``-d``) to the end.

After killing the container, to remove everything run ``docker-compose down --remove-orphans``.


Running without the database container
=======================================

To start the container:

.. code:: bash

    docker-compose -f docker-compose.yml up --build

.. note::

    To start it in the background, append (``-d``) to the end.

After killing the container, to remove everything run ``docker-compose down``.


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

Similarly, once you see the following lines, the frontend is up and available at ``http://localhost:8080``.

.. code-block:: 

    frontend_1  |  DONE  Compiled successfully in 43415ms11:40:57 PM
    frontend_1  |
    frontend_1  | No type errors found
    frontend_1  | No lint errors found
    frontend_1  | Version: typescript 3.5.3, tslint 5.18.0
    frontend_1  | Time: 20475ms
    frontend_1  |
    frontend_1  |   App running at:
    frontend_1  |   - Local:   http://localhost:8080/

Now you're good to go! Augur will automatically start collecting data in the background and populating the database, and you're free to start exploring the frontend and gathering data.