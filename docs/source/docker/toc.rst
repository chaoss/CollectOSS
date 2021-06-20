Docker
=====================

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


