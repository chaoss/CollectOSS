Database Setup
===============

One of the reasons that Augur is so powerful is because of our `unified data model <../schema/data-model.html>`_.
In order to ensure this data model remains performant even with large amounts of data, we use PostgreSQL as
our database engine. 

.. note::

    If you've already configured an Augur database, you can continue to the `installation instructions <installation.html>`_.


PostgreSQL Installation
~~~~~~~~~~~~~~~~~~~~~~~~

Before you can install our schema, you will need to make sure you have write access to a PostgreSQL 10 or later database. If you're looking for the fastest possible way to get Augur started or you're setting up for local development, you can use our `database container <../docker/docker.html>`_. If you're looking to collect data long term, we suggest following the rest of this tutorial and setting up a persistent PostgreSQL installation.

.. warning::

    If you want to collect data over the long term, we strongly advise against `using a Docker container for your database <https://vsupalov.com/database-in-docker/>`_.


If you're a newcomer to to PostgreSQL, follow their excellent instructions `here <https://www.postgresql.org/docs/12/tutorial-install.html>`_ to set it up for your machine of choice. We recommend using ``Postgres.app`` if you're on macOS, but if you're running a Linux distribution or are looking for an alternative to ``Postgres.app`` then pgAdmin is a great open source tool, albeit one with a somewhat cumbersome UI.

Creating a Database
~~~~~~~~~~~~~~~~~~~~~

After you've created your PostgreSQL instance, you'll need to setup a database in which to install the schema, as well as set up a dedicated augur user. You can do this with the SQL commands below (be sure to change the password!).

.. code-block:: postgresql 
    
    CREATE DATABASE augur;
    CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE augur TO augur;

For example, if you were using ``psql`` to connect to an instance on your machine ``localhost`` under the default user ``postgres`` on the default PostgreSQL port ``5432``, you might run something like this to connect to the server:

.. code-block:: bash

    $ psql -h localhost -U postgres -p 5432

Then, once you've connected to your PostgreSQL instance\:

.. code-block:: postgresql

    postgres=# CREATE DATABASE augur;
    postgres=# CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
    postgres=# GRANT ALL PRIVILEGES ON DATABASE augur TO augur;


Once you've got the database setup, Augur will take care of installing the schema for you. You're now ready to `install Augur <installation.html>`_!
