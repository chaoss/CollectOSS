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
-  `Python 3.6 or later <https://www.python.org/downloads/>`__

Our REST API & data collection workers are written in Python 3.6, and a GitHub access key is **required** for data collection.
We query the GitHub API to collect data about issues, pull requests, contributors, and other information about a repository.

Optional dependencies:

-  `Go 1.12 or higher installation <https://https://golang.org/doc/install>`__ 

The ``value_worker`` uses a Go package called `scc <https://github.com/boyter/scc>`_ to run COCOMO calculations.

Frontend
---------
If you're interested in using our visualizations as well, you can optionally install the frontend dependencies.
You will need:

-  `Vue.js <https://vuejs.org/>`__
-  `vue-cli <https://cli.vuejs.org/>`__
-  `node <https://nodejs.org/en/>`__
-  `npm <https://www.npmjs.com/>`__

We use Vue.js as our frontend web framework, and ``npm`` as our package manager.

=================
Installing Augur
=================

Lines that start with a ``$`` denote a bash command.

0. Clone the repository.

.. code:: bash

   $ git clone https://github.com/chaoss/augur.git
   $ cd augur/

1. Create a virtual environment in your home environment. Be sure to use
   the correct ``python`` command for your installation of Python 3.6+ - on most systems, this is ``python3``,
   but yours may differ.

.. code:: bash

    # to create the environment
    $ python3 -m venv $HOME/.virtualenvs/augur_env

    # to activate the environment in bash
    $ source $HOME/.virtualenvs/augur_env/bin/activate

.. note::
    If you aren't using ``bash``, your activation command might be a little different. For example, if you were using
    ``fish`` it would be ``source $HOME/.virtualenvs/augur_env/bin/activate.fish``.

2. Run the install script. This script will:

- install Augur’s metrics API
- install Augur's Python data collection workers
- generate a configuration file using your database credentials
- if needed, create the schema in your configuired database
- optionally, install Augur’s frontend and its dependencies 

.. code:: bash

   $ make install

.. note::
  
  If you think something went wrong, you can use ``make clean`` to delete the build files, then run ``make install`` again.

.. note::

  If you choose to install Augur's frontend, you might see a bunch of ``node-pre-gyp`` and ``canvas`` errors the installation logs after they're done. These are harmless and are caused by a few of our dependencies. If they seem to be causing you trouble, feel free to open an `issue <https://github.com/chaoss/augur/issues>`_ on our GitHub.

Once everything is installed, you're ready to `configure your data collection workers <collecting-data.html>`_!
