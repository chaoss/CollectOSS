Docker Quick Start
==================================
Before you get off to such a quick start, go ahead and 
  1. Create a fork from augur starting at https://github.com/chaoss/augur
  2. Clone that fork locally
  3. Checkout the appropriate branch to work on (see notes below):
  
  .. code-block:: python
  
     git checkout dev 
  
  4. Usually, we'll have you checkout the `dev` branch.
  5. Make sure to install all the pre-requisites here: https://oss-augur.readthedocs.io/en/main/getting-started/installation.html#dependencies


.. note::

  **Quick Start**: 

  If you want to start running docker against an external database right away: 

  1. Follow the instructions to create a database, and database user (if you have just installed Postgresql locally, you may need to follow instructions to allow access to Postgresql from Docker on the next page. tl;dr, there are edits to the Postgresql `pg_hba.conf` and `postgresql.conf` files): 

  .. code-block:: postgresql 
    
    CREATE DATABASE augur;
    CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE augur TO augur;
  
  2. Make sure you have an instance of redis running somewhere an external machine can access. On linux you can do this manually like this:

  .. code-block:: bash

    redis-server --protected-mode no

  3. Install Docker. If you're not familiar with Docker, their `starting guide <https://www.docker.com/resources/what-container>`_ is a great resource.

  4. Create a file to store all relevant enviroment variables for running docker. Below is an example file.

  .. code-block:: 

    AUGUR_GITHUB_API_KEY=xxxxxxxxxxxxxxxxxxx
    AUGUR_GITHUB_USERNAME=ExampleUser
    AUGUR_GITLAB_API_KEY=xxxxxxxxxxxxxxxxxxx
    AUGUR_GITLAB_USERNAME=ExampleUser
    AUGUR_DB=postgresql://xxxx:xxxxxxxx@yourhost:5432/yourdb
    REDIS_CONN_STRING=redis://yourhost:6379

  4. Execute the code from the base directory of the Augur repository:

  .. code-block:: bash

    sudo docker build -t augur-docker -f docker/backend/Dockerfile .
    sudo docker run --name augur --env-file <location where you saved your enviroment variables> --add-host host.docker.internal:host-gateway -t augur-docker

