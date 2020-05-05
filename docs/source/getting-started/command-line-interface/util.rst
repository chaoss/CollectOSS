================
Utility Commands
================

``augur util``
===============
The ``augur util`` commands are for performing a variety of different miscellaneous tasks. Below is the list of all the commands including an example parameter if one is needed.

.. hlist::
  :columns: 1

  * ``export-env``
  * ``kill``
  * ``list``
  * ``repo-reset``

``export-env``
---------------
Exports your GitHub key and database credentials to 2 files. The first is ``augur_export_env.sh`` which is an executable shell script that can be used initialize environment variables for each of your credentials. The second is ``docker_env.txt`` which specifies each credential in a key/value pair format that is used to configure the backend Docker containers.

Example usage::

  # to export your environment
  $ augur util export-env

  # contents of augur_export_env.sh
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

``kill``
---------
Terminates all currently running backend Augur processes, including any workers. Will only work in a virtual environment.

Example usage::

  # to stop the server and workers
  $ augur util kill

  # successful output looks like:
  > Killing 70595: /usr/local/bin/augur run
  > Killing 70596: /usr/local/bin/github_worker_start
  > ...


``list``
---------
Outputs the name and process ID (PID) of all currently running backend Augur processes, including any workers. Will only work in a virtual environment.

Example usage::

  # to stop the server and workers
  $ augur util list

  # successful output looks like:
  > 70595 /usr/local/bin/augur run
  > 70596 /usr/local/bin/github_worker_start
  > ...

``repo-reset``
---------------
Refresh repo collection to force data collection. Mostly for debugging.

Example usage::

  # to reset the repo collection status to "New"
  $ augur util repo-reset

  # successful output looks like:
  > Repos successfully reset.



