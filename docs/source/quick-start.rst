Quickstart
===============

Get going fast! Intended for folks familiar with setting up devops environments. 

PostgreSQL Installation
~~~~~~~~~~~~~~~~~~~~~~~~
- Gain access to an Ubuntu 18.04 or later environment and install PostgreSQL

.. code-block:: bash 

	sudo apt update
	sudo apt install software-properties-common
	sudo apt install postgresql postgresql-contrib
	sudo apt install build-essential


- Create a PostgreSQL database for Augur to use

.. code-block:: bash

    $ psql -h localhost -U postgres -p 5432

Then, once you've connected to your PostgreSQL instance\:

.. code-block:: postgresql

    postgres=# CREATE DATABASE augur;
    postgres=# CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
    postgres=# GRANT ALL PRIVILEGES ON DATABASE augur TO augur;

- Configure Git: These instructions assume the potential of large repositories that occasionally perform significant refactoring within a small number of commits. Our experience is that nearly all organizations have at least one project that meets these criteria. 

.. code-block:: bash

	git config --global diff.renames true
	git config --global diff.renameLimit 200000
	git config --global credential.helper cache
	git config --global credential.helper 'cache --timeout=9999999999999'

- For each platform, perform a command line login in order to cache Git credentials for the LINUX user who will be operating Augur. This step is required in order to prevent the Facade Commit Counting Diesel from stalling on a command line prompt when repositories move or disappear. 

- Set up a Python virtual environment (Python 3.6 - 3.8 work. Python 3.9 is not fully tested due to machine learning dependency lag.) 
- Clone and install Augur as a regular user. 

.. code-block:: bash

	su - ubuntu
	git clone https://github.com/chaoss/augur.git
	cd augur/
	sudo apt install make
	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt-get install python3-venv 
	python3 -m venv $HOME/.virtualenvs/augur_env
	source $HOME/.virtualenvs/augur_env/bin/activate
	sudo apt install python3-pip
	sudo apt install pythonpy
	python -m pip install --upgrade pip
	pip install tensorflow==2.5.0  
	#if previous line does not work try
	$ pip install tensorflow==2.5.0 --no-cache-dir
	#then:
	make install-dev {Follow prompts. You will need database credentials, a file location for cloned repositories, a GitHub Token, and a GitLab token.}

- Load a sample set of repositories. This can be accomplished through the Augur Command Line Interface (CLI). You can see available commands using 

.. code-block:: bash

	augur --help
	augur db --help
	augur backend --help

The commands for loading repos are: 

.. code-block:: bash

	augur db add-github-org
	augur db add-repo-groups
	augur db add-repos

We recommend that you test your instance using 50 or fewer repositories before undertaking a more substantial data collection. When you do take on a more substantial collection, you can "collect data faster" by adding additional tokens to the `worker_oauth` table in the `augur_operations` schema, and increasing the number of workers for the pull request and github worker blocks in the `augur.config.json` file that is generated at install. 
