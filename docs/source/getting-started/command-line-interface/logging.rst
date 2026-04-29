====================
Logging Commands
====================

``collectoss logging``
==================

The collection of the ``collectoss logging`` commands is for interacting with the database.

``directory``
--------------
Prints the location of the directory to which CollectOSS is configured to write its logs.

Example usage::

  # to print the logs directory
  $ uv run collectoss logging directory

  # successful output looks like:
  > /Users/carter/projects/work/collectoss/logs/


``tail``
---------
Prints the last ``n`` lines of each ``.log`` and ``.err`` file in the logs directory. ``n`` defaults to 20.

Example usage::

  # to print the last 20 lines of each log file
  $ uv run collectoss logging tail

  # successful output looks like:
  > ********** Logfile: collectoss.log
    <contents of collectoss.log>

  > ********** Logfile: collectoss.err
    <contents of collectoss.err>
