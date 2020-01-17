~~~~~~~~~~~~~~~~~~
Library Commmands
~~~~~~~~~~~~~~~~~~

Augur provides a few handy scripts and options for controlling the backend processes. They're broken up into 3 main categories: ``run``, ``db``, and ``util``.

``run``
========
The collection of the ``run`` commands controls the actual starting and stopping of the server. For right now, only the default command ``augur run`` is implemented. This will initialize the backend server by itself and show the logs in the terminal. Press ``CTRL-C`` to kill it.

Example\:

.. code:: bash

  # to run just the backend server
  augur run

.. note::

  The built-in data collection housekeeper can significantly slow down startup. If you're debugging or testing the server/API and don't need to do any data collection, pass the ``--disable-housekeeper`` flag to prevent it from starting up.


``db`` 
========
The collection of the ``db`` commands is for interacting with the database. 

``add_repos``
--------------
The ``add_repos`` command is used to load new repos. When given a path to correctly formatted ``.csv`` file, it will insert each repo specified in the file into its corresponding repo group in the database that's specified in the config file.

The ``.csv`` file must have the following format:
.. code-block::

  <repo_group_id>,<git_repo_url> 
  ...

where ``<repo_group_id>`` is a valid repository group ID, and ``<git_repo_url>`` is the url to the repository's Git repository, e.g. ``https://github.com/chaoss/augur.git``. 
Each pair of values should be on its own line (indicated by the ...), without quotes, and there should be no column headers.

Example\:

.. code:: bash

  # to add repos to the database
  augur db add_repos repos.csv

  # contents of repos.csv
  1,https://github.com/chaoss/augur.git
  2,https://github.com/chaoss/wg-evolution.git
  3,https://github.com/chaoss/metrics.git

``add_repo_groups``
--------------------
The ``add_repo_groups`` command is used to create new repo groups. When given a path to correctly formatted ``.csv`` file, it will create each repo group specified in the file with the corresponding ID and name.

The ``.csv`` file must have the following format:
.. code-block::

  <repo_group_id>,<repo_group_name>
  ...

Where <repo_group_id> is the desired ID of the new repo group, and <repo_group_name> is the desired name of the new repo group.

Each pair of values should be on its own line (indicated by the ...), without quotes, and there should be no column headers.

Example\:

.. code:: bash

  # to add repos to the database
  augur db add_repo_groups repo_groups.csv

  # contents of repo_groups.csv
  20,Apache Camel
  21,Apache DeltaSpike
  22,Apache Qpid
  23,Apache Tomcat


``get_repo_groups``
--------------------
The ``get_repo_groups`` command will return the ID, name, and description of all repo groups in the database.

Example\:

.. code:: bash

  # to add repos to the database
  augur db get_repo_groups

   repo_group_id  rg_name    rg_description
   1              Default    Default repo group


``util``
========
The collection of the ``util`` commands provides various miscelleanous functions that don't fit elsewhere. For the sake of brevity, we'll briefly cover the most useful one: ``augur util shell``. 

This command will drop you into an iPython shell with an instance of Augur's ``Application`` class already instantiated and ready for use. You can access this via the ``app`` variable once you're in the shell. See the `Python Library documentation <python.html>`_. for more info.

When you're finished in the iPython shell, press ``CTRL + D`` or type ``exit()`` in the interpreter and then press enter.

Example\:

.. code:: bash

  # drop into the shell
  augur util shell

  # inside the shell
  -- Augur Shell --
  augur [1]: print(app)
  <augur.application.Application object at 0x10966b860>

  augur [2]: print(app.metrics.issues_new(20, 21000))
     repo_name                      date  issues
  0        rails 2009-04-01 00:00:00+00:00       1
  1        rails 2009-04-17 00:00:00+00:00       1
  2        rails 2009-04-28 00:00:00+00:00       1
  3        rails 2011-04-28 00:00:00+00:00       7
  ...      ...                                 ...
  2092     rails 2019-09-22 00:00:00+00:00       1
  2093     rails 2019-09-23 00:00:00+00:00       4
  2094     rails 2019-09-24 00:00:00+00:00       4

  [2095 rows x 3 columns]

  augur [3]: exit()
