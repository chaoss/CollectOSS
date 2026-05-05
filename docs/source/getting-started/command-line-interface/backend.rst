=================
Backend Commands
=================

``collectoss backend``
======================
The ``collectoss backend`` CLI group is for controlling CollectOSS's API server & data collection workers. All commands are invoked like::

  $ collectoss backend <command name>

``start``
============
This command is for starting CollectOSS's API server & (optionally) data collection workers. Example usages are shown below the parameters. After starting up, it will run indefinitely (but might not show any output, unless it's being queried or the data collection is working).

--disable-collection      Flag that turns off the data collection. Useful for testing the REST API or if you want to pause data collection without editing your config.

--skip-cleanup      Flag that disables the old process cleanup that runs before CollectOSS starts. Useful for Python scripts where CollectOSS needs to be run in the background: see the `test/api/runner.py` file for an example.

**To start the backend normally:**

.. code-block::

  uv run collectoss backend start

  
To start the backend as a background process:

.. code-block:: bash

  uv run nohup collectoss backend start >logs/base.log 2>logs/base.err &

Successful output looks like the generation of standard CollectOSS logfiles in the logs/ directory.

To start the backend server without the housekeeper:

.. code-block:: bash

  uv run collectoss backend start --disable-housekeeper


``stop``
---------
**Gracefully** attempts to stop all currently running backend CollectOSS processes, including any workers. Will only work in a virtual environment.

Example usage:

.. code-block:: bash

  uv run collectoss backend stop

Successful output looks like:

.. code-block:: bash

  > CLI: [backend.stop] [INFO] Stopping process 33607
  > CLI: [backend.stop] [INFO] Stopping process 33775
  > CLI: [backend.stop] [INFO] Stopping process 33776
  > CLI: [backend.stop] [INFO] Stopping process 33777

``kill``
---------
**Forcefully** terminates (using ``SIGKILL``) all currently running backend CollectOSS processes, including any workers. Will only work in a virtual environment.
Should only be used when ``uv run collectoss backend stop`` is not working.

Example usage:

.. code-block:: bash

  uv run collectoss backend kill

  # successful output looks like:
  > CLI: [backend.kill] [INFO] Killing process 87340
  > CLI: [backend.kill] [INFO] Killing process 87573
  > CLI: [backend.kill] [INFO] Killing process 87574
  > CLI: [backend.kill] [INFO] Killing process 87575
  > CLI: [backend.kill] [INFO] Killing process 87576


``processes``
--------------
Outputs the process ID (PID) of all currently running backend CollectOSS processes, including any workers. Will only work in a virtual environment.

Example usage:

.. code-block:: bash

  uv run collectoss backend processes

Successful output looks like:

.. code-block:: bash

  > CLI: [backend.processes] [INFO] Found process 14467
  > CLI: [backend.processes] [INFO] Found process 14725


To enable log parsing for errors, you need to install `Elasticsearch <https://www.elastic.co/downloads/elasticsearch>`_ and `Logstash <https://www.elastic.co/downloads/past-releases/logstash-6-8-10>`_.

.. warning::
   Please note, that Logstash v7.0 and above has unresolved issues that affect this functionality.
   In order to use it in the near future, please download v6.8.
   If you use a package manager, it defaults to v7+, so we recommend downloading `binary <https://www.elastic.co/downloads/past-releases/logstash-6-8-10>`_.
   This change is tested with Elasticserach v7.8.0_2 and Logstash v6.8.10.

Set ``ELASTIC_SEARCH_PATH`` and ``LOGSTASH_PATH`` variables to point to elasticsearch and logstash binaries. For example:

.. code-block:: bash

  # If not specified, defaults to /usr/local/bin/elasticsearch
  $ export ELASTIC_SEARCH_PATH=<path_to_elastic_search_binary>

  # If not specified, defaults to /usr/local/bin/logstash
  $ export LOGSTASH_PATH=<path_to_logstash_binary>

  $ export ROOT_PROJECT_REPO_DIRECTORY=<path_to_augur>

Start the http server with::

  $ cd $ROOT_PROJECT_REPO_DIRECTORY/log_analysis/http
  $ python http_server.py

Then start CollectOSS with ``logstash`` flag::

  $ uv run collectoss backend start --logstash

If you'd like to clean all previously collected errors, run::

  $ uv run collectoss backend start --logstash-with-cleanup

Open http://localhost:8003 and select workers to check for errors.


``export-env``
---------------
Exports your GitHub key and database credentials to 2 files. The first is ``collectoss_export_env.sh`` which is an executable shell script that can be used to initialize environment variables for some of your credentials. The second is ``docker_env.txt`` which specifies each credential in a key/value pair format that is used to configure the backend Docker containers.

Example usage:

.. code-block:: bash

  # to export your environment
  $ uv run collectoss util export-env

Successful output looks like:

.. code-block:: bash

  > CLI: [util.export_env] [INFO] Exporting AUGUR_GITHUB_API_KEY
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_HOST
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_NAME
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_PORT
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_USER
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_PASSWORD

  # contents of collectoss_export_env.sh
  #!/bin/bash
  export AUGUR_GITHUB_API_KEY="your_key_here"
  export AUGUR_DB_HOST="your_host"
  export AUGUR_DB_NAME="your_db_name"
  export AUGUR_DB_PORT="your_db_port"
  export AUGUR_DB_USER="your_db_user"
  export AUGUR_DB_PASSWORD="your_db_password"

  # contents of docker_env.txt
  AUGUR_GITHUB_API_KEY="your_key_here"
  AUGUR_DB_HOST="your_host"
  AUGUR_DB_NAME="your_db_name"
  AUGUR_DB_PORT="your_db_port"
  AUGUR_DB_USER="your_db_user"
  AUGUR_DB_PASSWORD="your_db_password"


``repo-reset``
---------------
Refresh repo collection to force data collection. Mostly for debugging.

Example usage:

.. code-block:: bash

  # to reset the repo collection status to "New"
  $ uv run collectoss util repo-reset

  # successful output looks like:
  > CLI: [util.repo_reset] [INFO] Repos successfully reset
