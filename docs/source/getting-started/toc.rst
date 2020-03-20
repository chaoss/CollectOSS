==================
Getting Started
==================

This section of the documentation is an entry-level walkthrough of the Augur project, complete with installation, usage, and configuration guides. To set up Augur, we'll need to do a few things:

- Setup a PostgreSQL 10 database instance to store the data collected by Augur
- Install Augur's data collection workers and metrics API
- Configure Augur to collect data
- Start Augur using the built-in command line interface

If you want to get Augur up and running locally just to test it out, we have `Docker images available <../docker/toc.html>`_. If you're looking to install Augur for long-term data collection or for development, follow the instructions below.

.. toctree::
   :maxdepth: 1

   database
   installation
   collecting-data
   configuration-file-reference
   command-line-interface/toc