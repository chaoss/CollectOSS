====================
Logging Commands
====================

``augur logging``
==================

The collection of the ``augur logging`` commands is for interacting with the database.

``directory``
--------------
Prints the location of the directory to which Augur is configured to write its logs.

Example usage::

  # to print the logs directory
  $ uv run augur logging directory

  # successful output looks like:
  > /Users/carter/projects/work/augur/logs/


``tail``
---------
Prints the last ``n`` lines of each ``.log`` and ``.err`` file in the logs directory. ``n`` defaults to 20.

Example usage::

  # to print the last 20 lines of each log file
  $ uv run augur logging tail

  # successful output looks like:
  > ********** Logfile: augur.log
    <contents of augur.log>

  > ********** Logfile: augur.err
    <contents of augur.err>
