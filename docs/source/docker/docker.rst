Docker
=================

Augur provides a separate Docker image for each layer of our application (database, backend, and frontend). This section details how to build and run these images locally for testing, and also describes how to set up our test environment using Docker.

.. note::

    This page is primarily targeted at developers. 

Building the images
--------------------

All ``Dockerfiles`` and other Docker-related files are located in ``docker/<service_name>``, where ``<service_name>`` is either ``backend``, ``frontend``, or ``database``. To build these images locally, use the following command, being sure to replace ``<tag_name>`` and ``<service_name>`` as appropriate.

.. code-block:: bash

    # in the root augur/ directory
    $ docker build -t <tag_name> -f util/docker/<service name>/Dockerfile .

.. note::

    You can set ``<tag_name>`` to whatever you like, we recommend something like ``local_augur_backend`` so you don't get it confused with the official images.

Running containers
-------------------

To start a container, use the command below. ``<container_name>`` can be whatever you like, but ``<tag_name>`` should be the same as in the previous step or the tag of one of the official images.

.. code-block:: bash

    $ docker run -p <host_port>:<docker_port> --name <container_name> --env-file <file_with_enviroment_variables> --add-host host.docker.internal:host-gateway -t <tag_name>

.. note::

    If you are running the ``backend`` service, then ``<docker_port>`` needs to be ``5000``; for ``frontend`` and ``database`` the ports are ``8080`` and ``5434``. You can set the ``<host_port>`` to any **available** port on your machine for any of the services.

.. note::
    If you are running the backend service, you'll also need to add ``--env-file docker_env.txt`` to your command to make the container aware of your configuration file. You'll also need to add ``--add-host host.docker.internal:host-gateway`` to your command to make the container able to connect to services running on localhost. Make sure your database is configured to accept the container's connections by making sure that ``listen_addresses = '*'`` wherever the postgresql.conf is located on your machine and change the pg_hba.conf to accept hosts with a line similar to ``host	all  		all 		0.0.0.0/0 		md5``.


.. code-block::bash

    # in the root augur/ directory
    $ docker run -p <host_port>:<docker_port> --name <container_name> <tag_name>

