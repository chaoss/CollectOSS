Docker Compose
===========
For quickest start up, set up Docker or Podman desktop with a machine with roughly
the following resources (or more).

- 8 CPUs 
- 100 GB disk
- 10 GB RAM

1. Clone the Augur repository https://github.com/chaoss/augur


2. Create a .env file in the top level directory with the following fields: 

.. code:: python

    AUGUR_DB=augur
    AUGUR_DB_USER=augur
    AUGUR_DB_PASSWORD=password_here

    AUGUR_GITHUB_API_KEY=ghp_value_here
    AUGUR_GITHUB_USERNAME=gh_username
    AUGUR_GITLAB_API_KEY=placeholder
    AUGUR_GITLAB_USERNAME=placeholder

3. Build the container using one of the following commands:

.. code:: shell 

    docker compose up --build 

or

.. code:: shell 

    podman compose up --build 

And augur should be up and running! 