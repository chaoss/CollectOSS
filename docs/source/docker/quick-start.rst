Docker Quick Start
==================================
Before you get off to such a quick start, go ahead and 
  1. create a fork from augur starting at https://github.com/chaoss/augur
  2. clone that fork locally
  3. Checkout the appropriate branch to work on (see notes below). For right now, to checkout the ``test`` branch.:
  
  .. code-block:: python
  
     git checkout test 
  
  4. Usually, we'll have you checkout the `dev` branch, but through August 9, 2021, that branch is undergoing refactoring, to be be maintable, and is not reliable for new development 
  5. Make sure to install all the pre-requisites here: https://oss-augur.readthedocs.io/en/master/getting-started/installation.html#dependencies


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


