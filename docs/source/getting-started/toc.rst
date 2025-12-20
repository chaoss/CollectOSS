===============
Getting Started
===============

This section of the documentation is a no work experience required walkthrough of the Augur project. By the end, you'll hopefully have a fully functioning local installation of Augur ready to collect data.

Choose Your Installation Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Augur offers two primary installation approaches:

**Docker (Recommended for Quickstart)**: The fastest way to get Augur up and running with minimal setup. Viable for installations of any size.

**Manual Installation**: For deployments requiring direct system access, development work, or specific customization needs. Both Docker and manual installation are suitable for long-term use—they represent different management styles. We officially support macOS, Ubuntu, and Fedora for manual installation.

.. note::

    On Windows, Docker installs run in a virtual machine behind the scenes because containers rely on features of the Linux kernel. Manual installation on Windows requires setting up a virtual machine with a supported operating system.

Select the installation method below to get started:

.. toctree::
   :maxdepth: 1

   using-docker
   installation
   database
   collecting-data
   frontend
   command-line-interface/toc
