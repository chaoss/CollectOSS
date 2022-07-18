==================
Getting Started
==================

This section of the documentation is a no work experience required walkthrough of the Augur project. By the end, you’ll hopefully have a fully functioning local installation of Augur ready to collect data.

If you want to get started as fast as possible, we have `Docker images <../docker/toc.html>`_; however, if you’re looking to use Augur for long-term data collection or if you want to install it for development, you’ll need to follow this walkthrough.


.. note::

    We currently officially support the local installation of Augur from source on macOS, Ubuntu, and Fedora (but most UNIX-like systems will probably work with a few tweaks). We recommend either using the Docker images or setting up a virtual machine with a supported operating system installed if you are using Windows.

To install from source, we'll need to do a few things:

1. Setup a PostgreSQL instance to store the data collected by Augur
2. Install and configure Augur's application server
3. Install and configure Augur's data collection workers

The next section will start with a database setup, and then you can continue with the following steps given below.

Happy hacking!

.. toctree::
   :maxdepth: 1

   database
   installation
   collecting-data
   frontend
   command-line-interface/toc
