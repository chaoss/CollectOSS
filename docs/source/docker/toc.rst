Docker
=====================

.. note::

  **Quick Start**: 

  If you want to start running docker against an external database right away: 

  1. Follow the instructions to create a database, and database user (if you have just installed Postgresql locally, you may need to follow instructions for allow access to Postgresql from Docker in the next page. tl;dr, there are edits to the Postgresql `pg_hba.conf` and `postgresql.conf` files): 

  .. code-block:: postgresql 
    
    CREATE DATABASE augur;
    CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE augur TO augur;

  2. Install Docker. If you're not familiar with Docker, their `starting guide <https://www.docker.com/resources/what-container>`_ is a great resource.
  3. Execute the following script from the base directory of the Augur repository:

  .. code-block:: bash

    sudo ./docker-setup.sh

**Detailed Instructions that explain each step, and alternative, are available on the next page**

.. toctree::
   :maxdepth: 1

   getting-started
   docker
   docker-compose
   usage


