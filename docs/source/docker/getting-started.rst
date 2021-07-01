Getting Started
================

Credentials
------------
Before you get started with Docker, you'll need to set up a PostgreSQL instance either locally or using a remote host. Alternatively, you can also set up the databse within a docker container either manually or through the script but this is not recommended.

.. note::

  Make sure your database is configured to listen on all addresses in order to work with the containers. These settings can be edited in your ``postgresql.conf``. Additionally edit the bottom section of your ``pg_hba.conf`` file with:
.. code-block:: 

      # TYPE  DATABASE        USER            ADDRESS                 METHOD
      host	all  		all 		0.0.0.0/0 		md5

If you're interested solely in data collection and do not care if your data is not persisted, we recommend using our Docker Compose script. This will start up the backend and frontend containers simultaneously, well as an optional database container; however, if you are looking to collect data long term, we **strongly suggest setting up a persistent database instance**; you can find instructions for doing so `here <../getting-started/database.html>`_. Remember to save off the credentials for your newly minted database; you'll need them shortly. 

If you don't care if your data doesn't get persisted or are doing local development, you can use the database containers we provide. 

.. warning::

    Using a Docker container as a production database is `not recommended <https://vsupalov.com/database-in-docker/>`_. You have been warned!

If you're more interested in doing local development, we recommend using our Docker testing environment image - more on that later.

Configuration File
-------------------

Besides a database instance, you will also need a `GitHub Access Token <https://github.com/settings/tokens>`__ (``repo`` and all ``read`` scopes except ``enterprise``). **This is required for all Docker users**.

First, you'll need to clone the repository. In your terminal, run:

.. code-block:: bash

    $ git clone https://github.com/chaoss/augur.git
    $ cd augur/


Now that you've got your external database credentials (if you are using one) and your access token, we'll need to use to docker setup script or set environment variables manually.

Your database credentials and other environment variables used at runtime are stored in a file called docker_env.txt. This file determines the database credentials, the github API key, and whether or not to build the database schema.

If you do not want to use the script (not recommended) you can provide your own docker_env.txt to pull from. The file should have the below format and set all the variables to some value.

  .. code:: 

    AUGUR_GITHUB_API_KEY=your_key_here
    AUGUR_DB_SCHEMA_BUILD=0
    AUGUR_DB_HOST=xx.xxx.xxx.xxx
    AUGUR_DB_NAME=augur
    AUGUR_DB_PORT=5432
    AUGUR_DB_USER=augur
    AUGUR_DB_PASSWORD=somePassword

.. note::

  If you're using the ``test_data`` image instead of your database image, you'll need to add ``AUGUR_DB_NAME=test_data`` to your ``docker_env.txt`` to override the default database image name. This is taken care of for you if you use the script.


Now that you've created your config file or are ready to generate it yourself, you're ready to get going.
If you're doing data collection or just want to try out Augur, you'll want to use the docker-setup.sh script. If you're installing Augur for local development, we recommend using the more fine-grained `Docker <docker.html>`_ commands to build and run the containers individually. Using Docker Compose or the script is still a good way to try out the system as a whole before you start developing, and it doesn't hurt to know either!

.. note::

  Linux is currently the only supported platform for the script. Docker is slightly differant on macOS. Additionally, the script uses a network alias for local connections which is done differantly for macOS. The script will setup the alias for macOS correctly but it is untested for macOS and can be unpredictable.

Docker Setup Script
-------------------

.. note::

  It may take a while to download/build the docker containers depending on your internet/computer.


First, start the script in the augur directory using ``sudo ./docker-setup.sh``

Answer the prompt to select the type of deployment to use:

1. Deploy the backend using docker connected to a non-docker database.
    This option lets you deploy the backend using your own database whether local or remote.
2. Deploy the backend and database together in docker containers.
    This option lets you deploy the backend and database together as a pure docker deployment starting from an empty database.
3. Deploy the backend, and database together in docker containers using premade test data
    This option lets you deploy the backend and database together as a pure docker environment with pregenerated testing data to use. This option is great for trying out augur.


Deploying the backend using docker connected to a non-docker database
----------------------------------------------------------------------------------

Answer yes when the script prompts you for your database credentials if you did not manually generate the docker_env.txt. They will be saved locally and will persist if left unchanged.

.. warning::

  Make sure to specify localhost or 10.254.254.254 if the database is set up locally.

The script will then prompt you to ask whether or not to build a schema on the database. The default option is "no," only select yes if the database is without an existing schema.

If the containers deploy, the console output will switch to a monitor of state of the twin containers, with a monitor of both of their console output below.

A keyboard inturrupt will stop the containers and the script gives you the option of saving the console output to a log file.

Deploy the backend and database together in docker containers. With and without test data
----------------------------------------------------------------------------------------------------

If you have run the containers before and have already generated your environment variables the script should remember your github api key. Only change it if it is not the intended api key to use.

The containers should then deploy, switching to a console feed along with the process state of each docker container.
