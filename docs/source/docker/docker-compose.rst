Docker Compose Deployment
=========================

This section assumes you have read and configured your Docker installation as detailed `here <toc.html#getting-started>`_.

The default ports for each service are\:

- ``backend``: ``5000:50100-50800``
- ``frontend``: ``8080``
- ``database``: ``5434``

.. note::

    Make sure your database is configured to listen to all addresses to work with the containers. The most common error an improperly configured database throws are
    ::

        psql: could not connect to server: Connection refused
        Is the server running on host 10.254.254.254 and accepting
        TCP/IP connections on port 5432?
  

Docker Compose with the script (recommended)
============================================
This section details how to use Augur's docker-setup script to get a docker-compose deployment up and running as fast as possible.

Running the containers
-----------------------

.. warning::

    Don't forget to provide your external database credentials in the ``docker_env.txt`` file or generate it within the script. `More about the configuration file here <getting-started.html>`_

To run Augur

.. code-block:: bash

    sudo ./docker-setup.sh

Answer the prompts depending on your needs. If you are using a local database it is important to use 10.254.254.254 as a hostname or localhost if prompted. If you are using the container database or the test database press 2 or 3 for the prompt answer.

The script should automatically generate the environment variables for the docker containers and compose files. Additionally, it will set up a network alias so that the containers can communicate with localhost. Finally, it also takes care of whether or not to generate the schema to protect the integrity of any databases in use.


.. warning::

    It is also important to only generate the schema if you need to otherwise your database could become unusable later on.

Stopping the containers
-------------------------

To stop the containers, do a keyboard interrupt while the script is running ``Ctrl+C``. The script will then ask if you want to generate log files to look at later.

If not using the script, the standard method of stopping the containers that you started should work such as ``docker stop`` or ``docker-compose down``

Once you've got your container up and running, checkout out `how to use them <usage.html>`_ 


Docker Compose without a script
===============================

This section of the documentation details how to use Augur's Docker Compose configuration to get the full stack up and running as fast as possible without the recommended helper script. 

.. warning::

    Don't forget to provide your external database credentials in the ``docker_env.txt`` file. Additionally an ``.env`` file is needed for the ``*.yml`` files' environment variables. Don't forget to set the variables specified in these files namely ``AUGUR_DB_TYPE`` and ``AUGUR_DB_HOST``.

    Example docker_env.txt:
    .. code:: 

        AUGUR_GITHUB_API_KEY=your_key_here
        AUGUR_DB_SCHEMA_BUILD=0
        AUGUR_DB_HOST=xx.xxx.xxx.xxx
        AUGUR_DB_NAME=augur
        AUGUR_DB_PORT=5432
        AUGUR_DB_USER=augur
        AUGUR_DB_PASSWORD=somePassword


To run Augur **without** the database container:

.. code-block:: bash

    docker-compose -f docker-compose.yml up

To run Augur **with** the database container:

.. code-block:: bash

    docker-compose -f docker-compose.yml -f database-compose.yml up

If you want to use the ``test_data`` image with the data preloaded, change the ``image`` line of ``database-compose.yml`` to:

.. code::

    image: augurlabs/augur:test_data

Or you can set it dynamically in the .env file.

Stopping the containers
-------------------------

To stop the containers, run ``docker-compose down --remove-orphans``. The flag is necessary to stop the database container if you used one; run the command again to delete them. 

Once you've got your container up and running, checkout out `how to use them <usage.html>`_ 
