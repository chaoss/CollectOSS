Docker Compose Deployment
=========================

This section assumes you have read and configured your Docker installation as detailed `here <toc.html#getting-started>`_.

The default ports for each service are\:

- ``backend``: ``5000:50100-50800``
- ``frontend``: ``8080``
- ``database``: ``5434``

Docker Compose with the script (recommended)
============================================
This section details how to use Augur's docker-setup script in order to get a docker-compose deployment up and running as fast as possible.

Running the containers
-----------------------

.. warning::

    Don't forget to provide your external database credentials in the ``docker_env.txt`` file or generate it within the script. `More about the configuration file here <getting-started.html>`_

.. note::

    Running the database in a container is currently not supported by the script.
  
To run Augur

.. code-block:: bash

    sudo ./docker-setup.sh

Answer the prompts depending on your needs. If you are using a local database it is important to use 10.254.254.254 as a hostname or localhost if prompted.

.. warning::

    It is also important to only generate the schema if you need to otherwise your database could become unusable later on.

The default timeout interval of five seconds should work for most uses but if you have a slower machine increasing the value may help with deployment.

Stopping the containers
-------------------------

To stop the containers, do a keyboard inturrupt while the script is running ``Ctrl+C``. The script will then ask if you want to generate log files to look at later.

Once you've got your container up and running, checkout out `how to use them <usage.html>`_ 


Docker Compose without a script
===============================

This section of the documentation details how to use Augur's Docker Compose configuration to get the full stack up and running as fast as possible without the recommended helper script. 


To run Augur **without** the database container:

.. code-block:: bash

    docker-compose -f docker-compose.yml up

.. warning::

    Don't forget to provide your external database credentials in the ``docker_env.txt`` file.

To run Augur **with** the database container:

.. code-block:: bash

    docker-compose -f docker-compose.yml -f database-compose.yml up

If you want to use the ``test_data`` image with the data preloaded, change the ``image`` line of ``database-compose.yml`` to\:

.. code::

    image: augurlabs/augur:test_data

Stopping the containers
-------------------------

To stop the containers, run ``docker-compose down --remove-orphans``. The flag is necessary to stop the database container if you used one; run the command again to delete them. 

Once you've got your container up and running, checkout out `how to use them <usage.html>`_ 
