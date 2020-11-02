==================
Getting Started
==================

This section of the documentation is an entry-level walkthrough of the Augur project. By the end, you'll hopefully have a fully functioning local installation of Augur ready to collect data.

If you want to get started as fast as possible, we have `Docker images <../docker/toc.html>`_; however, if you're looking to use Augur for long-term data collection or if you want to install for development, you'll need to follow this walkthrough.

.. note::

    We currently officially support local installation of Augur from source on macOS, Ubuntu, and Fedora (but most UNIX-like systems will probably work with a few tweaks). If you are using Windows, we recommend either using the Docker images or setting up a virtual machine with a supported operating system installed.

To install from source, we'll need to do a few things:

0. Setup a PostgreSQL instance to store the data collected by Augur
1. Install and configure Augur's application server
2. Install and configure Augur's data collection workers

The next section will start with getting a database setup, and then go from there.
You can also find the table of contents for the whole walkthrough below.
Happy hacking!

.. toctree::
   :maxdepth: 1

   database
   installation
   collecting-data
   frontend
   command-line-interface/toc