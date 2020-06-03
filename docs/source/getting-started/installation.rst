Installation
=============

This section of the documentation details how to build Augur and its data workers from source. We currently officially support installation of Augur from source on macOS, Ubuntu, and Fedora (but most UNIX-like systems will probably work with a few tweaks). If you don't have a required dependency, please follow the provided links to install and
configure each piece of software.

Dependencies
~~~~~~~~~~~~~

Backend
---------
Required dependencies:

-  `GitHub Access Token <https://github.com/settings/tokens>`__ (``repo`` and all ``read`` scopes except ``enterprise``)
-  `GitLab Access Token <https://gitlab.com/profile/personal_access_tokens>`__ 
-  `Python 3.6 or later <https://www.python.org/downloads/>`__

Our REST API & data collection workers are written in Python 3.6. GitLab and a GitHub access keys are **required** for data collection.
We query the GitHub & GitLab API to collect data about issues, pull requests, contributors, and other information about a repository.

Optional dependencies:

-  `Go 1.12 or higher installation <https://https://golang.org/doc/install>`__ 

The ``value_worker`` uses a Go package called `scc <https://github.com/boyter/scc>`_ to run COCOMO calculations.

Frontend
---------
If you're interested in using our visualizations as well, you can optionally install the frontend dependencies.
You will need:

-  `npm <https://www.npmjs.com/>`__ On Ubuntu, for example, ``sudo apt-get install npm``
-  `Vue.js <https://vuejs.org/>`__  ``npm install vue``
-  `vue-cli <https://cli.vuejs.org/>`__  ``npm install vue-cli``
-  `node <https://nodejs.org/en/>`__  ``npm install node`` 

We use Vue.js as our frontend web framework, and ``npm`` as our package manager.

=================
Installing Augur
=================

Lines that start with a ``$`` denote a bash command.

0. Clone the repository.

.. code-block:: bash

   $ git clone https://github.com/chaoss/augur.git
   $ cd augur/

1. Create a virtual environment in your home environment. Be sure to use
   the correct ``python`` command for your installation of Python 3.6+ - on most systems, this is ``python3``, but yours may differ.

.. code-block:: bash

    # to create the environment
    $ python3 -m venv $HOME/.virtualenvs/augur_env

    # to activate the environment
    $ source $HOME/.virtualenvs/augur_env/bin/activate

2. Run the install script. This script will:

- install Augur’s metrics API & data collection controllers
- install Augur's data collection workers
- generate a configuration file using your database credentials
- if needed, install the schema in configured the database
- optionally, install Augur’s frontend and its dependencies 

.. note::

    At the very end, the install script will also generate an Augur API key for your database. This key will be automatically inserted into your database and then printed to your terminal. It's required to use the repo & repo group creation endpoints, so **make sure you save it off somehwere!** There is only one key per database.

.. code-block:: bash

   $ make install

If you think something went wrong, check the log files under ``logs/install/``. If you want to try again, you can use ``make clean`` to delete any build files before running ``make install`` again.

.. note::

  If you chose to install Augur's frontend dependencies, you might see a bunch of ``canvas@1.6.x`` and ``canvas-prebuilt@1.6.x`` errors in the installation logs. These are harmless and are caused by a few of our dependencies having *optional* requirements for old versions of these libraries. If they seem to be causing you trouble, feel free to open an `issue <https://github.com/chaoss/augur/issues>`_.

Once everything is installed, you're ready to `configure your data collection workers <collecting-data.html>`_!
