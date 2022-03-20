Quickstart
===============

Get going fast! Intended for folks familiar with setting up devops environments. These instructions are tested using Ubuntu 20.04 and Ubuntu 18.04. 

PostgreSQL Installation
~~~~~~~~~~~~~~~~~~~~~~~~
- Gain access to an Ubuntu 18.04 or later environment and install PostgreSQL. Ubuntu 20.04 is recommended because its long term support (LTS) window is longer. 

.. code-block:: bash 

	sudo apt update
	sudo apt upgrade
	sudo apt install software-properties-common
	sudo apt install python3-dev
	sudo apt install postgresql postgresql-contrib postgresql-client
	sudo apt install build-essential


- Create a PostgreSQL database for Augur to use

.. code-block:: bash

    $ sudo su - 
    $ su - postgres
    $ psql 

Then, once you've connected to your PostgreSQL instance\:

.. code-block:: postgresql

    postgres=# CREATE DATABASE augur;
    postgres=# CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
    postgres=# GRANT ALL PRIVILEGES ON DATABASE augur TO augur;

Git Configuration
~~~~~~~~~~~~~~~~~~~~~~~~
- Configure Git: These instructions assume the potential of large repositories that occasionally perform significant refactoring within a small number of commits. Our experience is that nearly all organizations have at least one project that meets these criteria. 

.. code-block:: bash

	git config --global diff.renames true
	git config --global diff.renameLimit 200000
	git config --global credential.helper cache
	git config --global credential.helper 'cache --timeout=9999999999999'

- For each platform, perform a command line login in order to cache Git credentials for the LINUX user who will be operating Augur. This step is required in order to prevent the Facade Commit Counting Diesel from stalling on a command line prompt when repositories move or disappear. 

Install Go
~~~~~~~~~~~~~~~~~~~~~~~~
Two of Augur's workers use the Go programming language, which needs to be installed on your computer. Snap is the easiest way to install Go. If Snap does not work for you, see instructions here: https://www.digitalocean.com/community/tutorials/how-to-install-go-on-ubuntu-20-04

.. code-block:: bash

	sudo apt update
	sudo apt install snapd
	sudo snap install go --classic

Python Virtual Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~
- Set up a Python virtual environment (Python 3.8 and above are now required. Python 3.9 and python 3.10 work as well, though we have tested Python 3.9 on more platforms.) 
- Clone and install Augur as a regular user. 

.. code-block:: bash

	# make sure you are logged in as your own user (i.e. "sean")
	git clone https://github.com/chaoss/augur.git
	cd augur/
	sudo apt install make
	sudo apt-get install python3-venv 
	python3 -m venv $HOME/.virtualenvs/augur_env
	source $HOME/.virtualenvs/augur_env/bin/activate
	sudo apt install python-pip-whl
	sudo apt install python3-pip
	sudo apt install pythonpy
	python -m pip install --upgrade pip
	make install-dev {Follow prompts. You will need database credentials, a file location for cloned repositories, a GitHub Token, and a GitLab token.}

- Seven sample repositories are loaded by default. You can delete them if you want to use your own repositories by deleting the records from the `repo` table first, then deleting the records from the `repo_groups` table. 

.. code-block:: bash

	augur --help
	augur db --help
	augur backend --help

Loading Repositories
~~~~~~~~~~~~~~~~~~~~~~~~
The commands for loading repos are: 

.. code-block:: bash

	augur db add-github-org
	augur db add-repo-groups
	augur db add-repos

We recommend that you test your instance using 50 or fewer repositories before undertaking a more substantial data collection. When you do take on a more substantial collection, you can "collect data faster" by adding additional tokens to the `worker_oauth` table in the `augur_operations` schema, and increasing the number of workers for the pull request and github worker blocks in the `augur.config.json` file that is generated at install. 
