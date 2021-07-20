Docker
=================

Augur provides a separate Docker image for each layer of our application (database, backend, and frontend). This section details how to build and run these images locally for testing, and also describes how to set up our test environment using Docker.

.. note::

    This page is primarily targeted at developers. If you're solely interested in collecting data, we recommend using our `Docker Setup Script <docker-compose.html>`_.

Building the images
--------------------

All ``Dockerfiles`` and other Docker-related files are located in ``util/docker/<service_name>``, where ``<service_name>`` is either ``backend``, ``frontend``, or ``database``. To build these images locally, use the following command, being sure to replace ``<tag_name>`` and ``<service_name>`` as appropriate.

.. code-block:: bash

    # in the root augur/ directory
    $ docker build -t <tag_name> -f util/docker/<service name>/Dockerfile .

.. note::

    You can set ``<tag_name>`` to whatever you like, we recommend something like ``local_augur_backend`` so you don't get it confused with the official images.

Running containers
-------------------

To start a container, use the command below. ``<container_name>`` can be whatever you like, but ``<tag_name>`` should be the same as in the previous step, or the tag of one of the official images.

.. code-block:: bash

    $ docker run -p <host_port>:5432 --name <container_name> -t <tag_name>

.. note::

    If you are running the ``backend`` service, then ``<docker_port>`` needs to be ``5000``; for ``frontend`` and ``database`` the ports are ``8080`` and ``5434``. You can set the ``<host_port>`` to any **available** port on your machine for any of the services.

.. note::
    If you are running the backend service, you'll also need to add ``--env-file docker_env.txt`` to your command in order to make the container aware of your configuration file. You'll also need to add ``--add-host=database:<ip_of_database>`` to your command in order to make the container connect to your database. Make sure your database is configured to accept the container's connections by making sure that ``listen_addresses = '*'`` wherever the postgresql.conf is located on your machine and change the pg_hba.conf to accept hosts with a line similar to ``host	all  		all 		0.0.0.0/0 		md5``.

.. warning::
    If you are using a local database, you need to set up an alias for your localhost. In a terminal, type ``sudo ifconfig lo:0 10.254.254.254`` if you are using linux or ``sudo ifconfig lo0 alias 10.254.254.254`` if you are using macOS. You will use this alias, ``10.254.254.254`` to connect to the local database. Make sure your database is properly configured by using this command ``psql -d "postgresql://augur:<your_password>@10.254.254.254/augur" -c "select now()"``. This command should have the same output if you replace the ip with ``localhost``.


.. code-block::bash

    # in the root augur/ directory
    $ docker run -p <host_port>:<docker_port> --name <container_name> <tag_name>

Running the test database
~~~~~~~~~~~~~~~~~~~~~~~~~~~

One of the containers we provide is ``augurlabs/augur:test_data``, a container preloaded with the Augur schema and our testing environment. This is primarly for developers to easily reproduce the tests locally, but could also be used by those who just want to browse some sample data.
We recommend using the following command to start it up:

.. code-block:: bash

    $ docker run -p <host_port>:5432 --name augur_test augurlabs/augur:test_data
