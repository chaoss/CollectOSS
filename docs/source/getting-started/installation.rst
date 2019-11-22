~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This documents details how to install Augur and its dependencies.

================
Dependencies
================

Data collection
---------------
You will need:

-  A `PostgreSQL 10 or higher <https://www.postgresql.org/download/>`__ installation.
   
.. code::

sudo apt-get install postgresql


One of the reasons that Augur is so powerful is because of our `unified data model <../architecture/data-model.rst>`_.
In order to ensure this data model remains performant even with large amounts of data, we use PostgreSQL as
our database engine. 

Before you start the installation, you will need to make sure you have write access to a PostgreSQL 10+ database.
During the installation process you will be asked to provide the following credentials for the database:

- database name
- host
- port
- user
- password for the user specified above

.. note::

   The code block below contains the commands you need to install postgres and create an augur user. 

.. code:: 

    sudo apt-get install postgresql 
    sudo -u postgres 
    psql
    postgres=# create database augur;
    postgres=# create user augur with encrypted password 'mypass';
    postgres=# grant all privileges on database augur to augur;

The installation process will automatically set up the schema for the data model if it hasn't been created yet.
After the schema has been set up, you'll be asked if you want to load the schema with some sample data (around 24 MB).
If you're just curious about Augur and want to see our visualizations, this is a good way to get going quickly.

.. note::

    We also provide an option for connecting to a database with the schema already installed.

Backend
---------
You will need:

-  `GitHub Access Token <https://github.com/settings/tokens>`__ (no write access required)
-  `Python 3.6 or higher <https://www.python.org/downloads/>`__

Our REST API & data collection workers are written in Python 3, and a GitHub access key is **required** for data collection.
We query the GitHub API to collect issue/pull request data, among other things.

Frontend
---------
You will need:

-  `Vue.js <https://vuejs.org/>`__
-  `vue-cli <https://cli.vuejs.org/>`__
-  `node <https://nodejs.org/en/>`__
-  `npm <https://www.npmjs.com/>`__

.. note::

   The code block below contains the commands you need to install these dependencies.  
   
.. code::

    sudo apt-get install python3-pip
    sudo pip3 install virtualenv 
    sudo apt install npm
    npm config set prefix ~/.npm
    npm install -g @vue/cli
    npm install vue.js 

We use Vue.js as our frontend web framework, and ``npm`` as our package manager.

=================
Installing Augur
=================

0. Clone the repository.

.. code:: bash

   git clone https://github.com/chaoss/augur.git
   cd augur/

1. Create a virtual environment in your home environment. Be sure to use
   the correct ``python`` command for your installation of Python 3.6+ - on most systems, this is ``python3``,
   but yours may differ.

.. code:: bash

    # to create the environment
    python3 -m venv $HOME/.virtualenvs/augur_env

    # to activate it in bash
    source $HOME/.virtualenvs/augur_env/bin/activate

2. Begin the installation process.

.. code:: bash

   make install

This process will:

- install Augur’s backend 
- install the data collection workers
- generate documentation
- generate the configuration file
- optionally, install the database schema and load sample data 
- optionally, install Augur’s frontend and its dependencies 

Once everything is installed, you're ready to get started using Augur. Check out the `Makefile commands <usage/make-commands.html#development>`_ section to learn how to run Augur, or if you're interested in collecting your own data, check out the `data collection documentation <../data-collection/starting-collection-workers.html>`_.

Happy hacking!