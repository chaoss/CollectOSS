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
Exports your GitHub key and database credentials to 2 files. The first is ``augur_export_env.sh`` which is an executable shell script that can be used initialize environment variables for some of your credentials. The second is ``docker_env.txt`` which specifies each credential in a key/value pair format that is used to configure the backend Docker containers.

Example usage::

  # to export your environment
  $ augur util export-env

  # successful output looks like:
  > CLI: [util.export_env] [INFO] Exporting AUGUR_GITHUB_API_KEY
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_HOST
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_NAME
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_PORT
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_USER
  > CLI: [util.export_env] [INFO] Exporting AUGUR_DB_PASSWORD

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

``stop``
---------
Gracefully terminates all currently running backend Augur processes, including any workers. Will only work in a virtual environment.

Example usage::

  # to stop the server and workers
  $ augur util stop

  # successful output looks like:
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33607
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33775
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33776
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33777
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33778
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33780
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33781
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33782
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33783
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33784
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33785
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33786
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33787
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33788
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33789
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33790
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33792
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33793
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33794
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33795
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33798
  > CLI: [util.cli_stop_processes] [INFO] Killing process 33962

``kill``
---------
Forcefully terminates all currently running backend Augur processes, including any workers, by using ``SIGKILL``. Will only work in a virtual environment.

Example usage::

  # to stop the server and workers
  $ augur util kill

  # successful output looks like:
  > CLI: [util.kill_processes] [INFO] Killing process 87340
  > CLI: [util.kill_processes] [INFO] Killing process 87573
  > CLI: [util.kill_processes] [INFO] Killing process 87574
  > CLI: [util.kill_processes] [INFO] Killing process 87575
  > CLI: [util.kill_processes] [INFO] Killing process 87576


``list``
---------
Outputs the process ID (PID) of all currently running backend Augur processes, including any workers. Will only work in a virtual environment.

Example usage::

  # to stop the server and workers
  $ augur util list

  # successful output looks like:
  > CLI: [util.list_processes] [INFO] Found process 33607
  > CLI: [util.list_processes] [INFO] Found process 33775
  > CLI: [util.list_processes] [INFO] Found process 33776
  > CLI: [util.list_processes] [INFO] Found process 33777
  > CLI: [util.list_processes] [INFO] Found process 33778
  > CLI: [util.list_processes] [INFO] Found process 33780
  > CLI: [util.list_processes] [INFO] Found process 33781
  > CLI: [util.list_processes] [INFO] Found process 33782
  > CLI: [util.list_processes] [INFO] Found process 33783
  > CLI: [util.list_processes] [INFO] Found process 33784
  > CLI: [util.list_processes] [INFO] Found process 33785
  > CLI: [util.list_processes] [INFO] Found process 33786
  > CLI: [util.list_processes] [INFO] Found process 33787
  > CLI: [util.list_processes] [INFO] Found process 33788
  > CLI: [util.list_processes] [INFO] Found process 33789
  > CLI: [util.list_processes] [INFO] Found process 33790
  > CLI: [util.list_processes] [INFO] Found process 33792
  > CLI: [util.list_processes] [INFO] Found process 33793
  > CLI: [util.list_processes] [INFO] Found process 33794
  > CLI: [util.list_processes] [INFO] Found process 33795
  > CLI: [util.list_processes] [INFO] Found process 33798
  > CLI: [util.list_processes] [INFO] Found process 33962

``repo-reset``
---------------
Refresh repo collection to force data collection. Mostly for debugging.

Example usage::

  # to reset the repo collection status to "New"
  $ augur util repo-reset

  # successful output looks like:
  > CLI: [util.repo_reset] [INFO] Repos successfully reset



