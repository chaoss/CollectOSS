Docker Compose
=========================

This section of the documentation details how to use Augur's Docker Compose configuration to get the full stack up and running as fast as possible. This section assumes you have read and configured your Docker installation as detailed `here <toc.html#getting-started>`_.

The default ports for each service are\:

- ``backend``: ``5000:50100-50800``
- ``frontend``: ``8080``
- ``database``: ``5434``

Running the containers
-----------------------

To run Augur **without** the database container:

.. code-block:: bash

    docker-compose -f docker-compose.yml up

.. warning::

    Don't forget to provide your external database credentials in the ``env.txt`` file.

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