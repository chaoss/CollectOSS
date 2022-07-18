Installing for Development
=============================

Installing Augur for local development is pretty similar to the normal installation process. This guide will primarily detail the differences between the two instead of regurgitating all the information in the `Getting Started <../getting-started/toc.html>`_ section. If you are completely new to Augur, we recommend following the aforementioned `Getting Started <../getting-started/toc.html>`_ section first; once you feel more comfortable with Augur and how to use it, come back to this document.

Setting up the Database
------------------------

If they so desire, developers can set up a persistent instance of PostgreSQL on either the local machine or a remote server. The instructions for doing so can be found in the `database <../getting-started/database.html>`_ portion of the Getting Started section


However, during development, you might find that you need to reset your database often, especially if you are working on the data collection components of Augur. To this end, we recommend developers make use of our `Docker images <../docker/docker.html>`_ to quickly provision and terminate database instances in a lightweight and reproducible manner.


More information about Augur's Docker images can be found `here <../docker/docker.html>`_. If you're new to our Docker process, we recommend following the `introduction section <../docker/toc.html>`_ first.

Installing from Source
----------------------------

The process for installing Augur's source code for development is essentially the same as detailed in the `Installation <../getting-started/installation.html>`_ section of the Getting Started guide.

**However**, when running the installation script, use the following command instead:

.. code-block:: bash

   $ make install-dev

This will install a few extra dependencies for testing and documentation, as well as install all the Python packages in `editable mode <https://pip-python3.readthedocs.io/en/latest/reference/pip_install.html#editable-installs>`_. This means you will not have to reinstall the package every time you make a change to the Python source code.

This command will also create your ``augur.config.json`` file in the root of your cloned source code directory **instead of** the default location in ``$HOME/.augur/``. This is purely for convenience's sake, as it will allow you to open this file in your text editor with all the other source code files, and also allows you to have multiple developer installations of Augur on the same machine if needed. If Augur finds a config file in both the root of the cloned directory AND in the default location, it will always use the one in the root of the cloned directory.

.. note::
    You can still use ``make clean`` to get rid of the installed binaries if something went wrong and you want to try again.

Conclusion
-----------

All in all, it's pretty similar. For further reading, the `Makefile <make/toc.html>`_ documentation and the `Creating a Metric guide <create-a-metric/toc.html>`_ are good places to start.

Happy hacking!
