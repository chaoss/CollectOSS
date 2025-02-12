Database setup
===============

One of the reasons that Augur is so powerful is because of its `unified data model <../schema/overview.html>`_.
To ensure this data model remains performant with large amounts of data, we use PostgreSQL as our database engine. 
We'll need to set up a PostgreSQL instance and create a database, after which Augur can take care of the rest.
Make sure to save off the credentials you use when creating the database; you'll need them again to configure Augur.

PostgreSQL Installation
~~~~~~~~~~~~~~~~~~~~~~~~

Before you can install our schema, you will need to make sure you have **write access** to a PostgreSQL 10 or later database. If you're looking for the fastest possible way to get Augur started, we recommend use our `database container <../docker/docker.html>`_. If you're looking to collect data long-term, we recommend following the rest of this tutorial and setting up a persistent PostgreSQL installation.

.. warning::

    If you want to collect data over the long term, we strongly advise against `using a Docker container for your database <https://vsupalov.com/database-in-docker/>`_.

If you're a newcomer to PostgreSQL, you can follow their excellent instructions `here <https://www.postgresql.org/docs/12/tutorial-install.html>`_ to set it up for your machine of choice. We recommend using ``Postgres.app`` if you're on macOS, but if you're running UNIX or are looking for an alternative to ``Postgres.app`` then pgAdmin is a great open-source alternative.

Creating a Database
~~~~~~~~~~~~~~~~~~~~~

After you set up your PostgreSQL instance, you'll need to create a database and user with the correct permissions. You can do this with the SQL commands below, but be sure to change the password!

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


Once you've got the database setup, Augur will install the schema for you. You're now ready to `install Augur <installation.html>`_!
