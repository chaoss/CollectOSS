How to Install CollectOSS for Development
=========================================

Building CollectOSS for local development (i.e. from source) uses the same process as the normal installation fom docker.
If you are completely new to CollectOSS, we recommend following the `Getting Started <../getting-started/toc.html>`_ section first; once you feel more comfortable with CollectOSS and how to use it, come back to this document.

Setting up the Database
------------------------

If they so desire, developers can set up a persistent instance of PostgreSQL on either the local machine or a remote server. The instructions for doing so can be found in the `database <../getting-started/database.html>`_ portion of the Getting Started section


However, during development, you might find that you need to reset your database often, especially if you are working on the data collection components of collectoss. To this end, we recommend developers make use of our `Docker images <../docker/docker.html>`_ to quickly provision and terminate database instances in a lightweight and reproducible manner.


More information about CollectOSS's Docker images can be found `here <../docker/docker.html>`_. If you're new to our Docker process, we recommend following the `introduction section <../docker/toc.html>`_ first.


Building CollectOSS from Source
-------------------------------

To build CollectOSS from source, you can use the following command:

.. code-block:: bash

   $ docker compose build

This will build the CollectOSS image based on the current state of your local repository.

You can then use the same `docker compose up` command to run the CollectOSS container stack to test your changes.