=======================
Configuration Commands
=======================

``augur config``
====================
The ``augur config`` commands are for interacting with Augur's configuration file.

``init``
------------
The ``init`` command is used to create a configuration file, by default named ``augur.config.json``.
Each of the available parameters is optional, and can also be configured using an existing environment variable.
Below is the list of available parameters, their defaults, and the corresponding environment variable.

--db_name       Database name for your data collection database. Defaults to ``augur``. Set by the ``AUGUR_DB_NAME`` environment variable

--db_host       Host for your data collection database. Defaults to ``localhost``. Set by the ``AUGUR_DB_HOST`` environment variable

--db_user       User for your data collection database. Defaults to ``augur``. Set by the ``AUGUR_DB_USER`` environment variable

--db_port       Port for your data collection database. Defaults to ``5432``. Set by the ``AUGUR_DB_PORT`` environment variable

--db_password       Password for your data collection database. Defaults to ``augur``. Set by the ``AUGUR_DB_PASSWORD`` environment variable

--github_api_key        GitHub API key for data collection from the GitHub API. Defaults to ``key``. Set by the ``AUGUR_GITHUB_API_KEY`` environment variable

--facade_repo_directory     The directory on this machine where Facade should store its cloned repos. Defaults to ``repos/``. Set by the ``AUGUR_FACADE_REPO_DIRECTORY`` environment variable

--rc-config-file        Path to a file an existing Augur config whose values will be used as the defaults. Defaults to ``None``. This paramter does not support being set by an environment variable.

--write-to-src          Flag for writing the generated config file to the source code tree, instead of the default ``$HOME/.augur``. For developer use only. Defaults to ``False``.

Example usage\:

.. code-block:: bash

  # to generate an augur.config.json file with all the defaults
  $ augur config init

  # to generate an augur.config.json given all credentials as literals
  $ augur config init --db_name "db_name" --db_host "host" --db_port "port" --db_user "db_user" --db_password "password" --github_api_key "github_api_key" --facade_repo_directory "facade_repo_directory"

  # to generate an augur.config.json given all credentials alsod environment variables
  $ augur config init --db_name $AUGUR_DB_NAME --db_host $AUGUR_DB_HOST --db_port $AUGUR_DB_PORT --db_user $AUGUR_DB_DB_USER --db_password $AUGUR_DB_PASSWORD --github_api_key $AUGUR_GITHUB_API_KEY --facade_repo_directory $AUGUR_FACADE_REPO_DIRECTORY

  # successful output looks like:
  > CLI: [config.init] [INFO] Config written to /Users/carter/.augur/augur.config.json




