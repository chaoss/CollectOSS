Docker
=====================

.. note::

  **Quick Start**: 

  If you want to start running docker against an external database right away: 

  1. Follow the instructions to create a database, and database user: 

  .. code-block:: postgresql 
    
    CREATE DATABASE augur;
    CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE augur TO augur;

  2. Install Docker. If you're not familiar with Docker, their `starting guide <https://www.docker.com/resources/what-container>`_ is a great resource.
  3. Execute the following script from the base directory of the Augur repository: `sudo ./docker-setup.sh`

Augur provides several Docker images designed to get you started with our software as quickly as possible. They are:

- ``augurlabs/augur:backend``, our backend data collection and metrics API
- ``augurlabs/augur:frontend``, our metrics visualization frontend

.. warning::
   The frontend is very out of date and will likely not work with the backend very well. It is still available however.

- ``augurlabs/augur:database``, an empty PostgreSQL database with the Augur schema installed
- ``augurlabs/augur:test_data``, a PostgreSQL database loaded with the data used in our testing environment

If you're not familiar with Docker, their `starting guide <https://www.docker.com/resources/what-container>`_ is a great resource.

The rest of this section of the documentation assumes you have a working installation of Docker as well as some familiarity with basic Docker concepts and a few basic Docker and Docker Compose commands.

If this is your first time using Docker with Augur, please follow the instructions in "Getting Started" to set up your environment.

.. toctree::
   :maxdepth: 1

   getting-started
   docker
   docker-compose
   usage


