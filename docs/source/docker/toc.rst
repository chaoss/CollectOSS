Docker
=====================

Augur provides several Docker images designed to you started with our software as quickly as possible. They are:

- ``augurlabs/augur:backend``, our backend data collection and metrics API
- ``augurlabs/augur:frontend``, our metrics visualization frontend
- ``augurlabs/augur:database``, an empty PostgreSQL database with the Augur schema installed
- ``augurlabs/augur:test_data``, a PostgreSQL database loaded with the data used in our testing environment

If you're not familiar with Docker, their `starting guide <https://www.docker.com/resources/what-container>`_ is a great resource.

The rest of this section of the documentation assumes you have a working installation of Docker as well as some familiarity with basic Docker concepts and a few basic Docker and Docker Compose commands.

If this is your first time using Docker with Augur, you'll need to read the section below to set up your environment. If you just came for the commands and usage guidelines, you can skip to the Table of Contents.

.. toctree::
   :maxdepth: 1

   docker
   docker-compose
   usage

Introduction
________________

Credentials
------------
Before you get started with Docker, you'll need to set up a PostgreSQL instance with the Augur schema installed. 

If you're interested solely in data collection and do not care if your data is not persisted, we recommend using Docker Compose. This will start up the backend and frontend containers simultaneously, well as an optional database container; however, if you are looking to collect data long term, we **strongly suggest setting up a persistent database instance**; you can find instructions for doing so `here <../getting-started/database.html>`_. Remember to save off the credentials for your newly minted database; you'll need them shortly. 

If you don't care if your data doesn't get persisted or are doing local development, you can use the database containers we provide. 

.. warning::

    Using a Docker container as a production database is `not recommended <https://vsupalov.com/database-in-docker/>`_. You have been warned!

If you're more interested in doing local development, we recommend using our Docker testing environment image - more on that later.

Configuration
--------------

Besides a database instance, you will also need a `GitHub Access Token <https://github.com/settings/tokens>`__ (``repo`` and all ``read`` scopes except ``enterprise``). **This is required for all Docker users**.

Now that you've got your external database credentials (if you are using one) and your access token, we'll need to set up the configuration file.

First, you'll need to clone the repository. In your terminal, run:

  .. code:: 

    $ git clone https://github.com/chaoss/augur.git
    $ cd augur/

Now, create a file in this directory called ``augur_env.txt``. If you are using Docker Compose, you will only need to enter your access token (as shown on the first line below).

You can copy and paste the below example, but don't forget to change the values to match your database credentials!

  .. code:: 

    AUGUR_GITHUB_API_KEY=your_key_here

    AUGUR_DB_HOST=example.com
    AUGUR_DB_NAME=augur
    AUGUR_DB_PORT=5432
    AUGUR_DB_USER=augur
    AUGUR_DB_PASSWORD=augur

.. note::

    macOS users only: if you are trying to run Augur in a Docker container and are pointing it to a local database instance using either another Docker container or a local database, you'll need to set ``AUGUR_DB_HOST`` to ``host.docker.internal``. This is a limitation of networking Docker Desktop for Mac; see the Docker `docs <https://docs.docker.com/docker-for-mac/networking/#i-want-to-connect-from-a-container-to-a-service-on-the-host>`_ for more info.

.. note::

  If you're using the ``test_data`` image instead of your database image, you'll need to add ``AUGUR_DB_NAME=test_data`` to your ``augur_env.txt`` to override the default database image name.

Now that you've created your config file, you're ready to get going.
If you're doing data collection or just want to try out Augur, you'll want to use Docker Compose. If you're installing Augur for local development, we recommend using the more fine-grained `Docker <docker.html>`_ commands to build and run the containers individually. 

.. note::

    Using Docker Compose is still a good way to try out the system as a whole before you start developing, and it doesn't hurt to know either!
