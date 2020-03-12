Database Setup
===============

One of the reasons that Augur is so powerful is because of our `unified data model <../schema/data-model.html>`_.
In order to ensure this data model remains performant even with large amounts of data, we use PostgreSQL as
our database engine. 

.. note::

    If you've already configured an Augur database, you can continue to the `installation instructions <installation.html>`_.


PostgreSQL Installation
~~~~~~~~~~~~~~~~~~~~~~~~

Before you can install our schema, you will need to make sure you have write access to a PostgreSQL 10+ database.
During this installation process you will be asked to provide some credentials for the database, including:

- database name
- host
- user
- password
- port

Make sure to save these credentials in a safe location, as you'll need to access to them again when configuring
Augur. To set up PostgreSQL for your machine of choice, follow their excellent instructions `here <https://www.postgresql.org/docs/12/tutorial-install.html>`_.
If you're for the fastest possible way to get Augur started, you can use our `database container <../docker/docker.html>`_. 

.. warning::
    If you want to collect data long term, we strongly suggest `against using a Docker container for your database <https://vsupalov.com/database-in-docker/>`_. If you are setting up for development however, we recommend using the `testing Docker image to reproduce our test environment locally <../docker/docker.html>`_.

Creating a Database
~~~~~~~~~~~~~~~~~~~~~

You'll need to setup a fresh database to install the schema. You can do this with the following SQL command:

.. code:: 

    postgres=# CREATE DATABASE augur;

We recommend creating a user in your database just for Augur, like so:

.. code:: 

    postgres=# CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
    postgres=# GRANT ALL PRIVILEGES ON DATABASE augur TO augur;

At this point, Augur will take care of the rest of the setup for you. Now you're ready to `install Augur <installation.html>`_!
