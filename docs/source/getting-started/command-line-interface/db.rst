====================
Database Commands
====================

``augur db``
=============

The collection of the ``augur db`` commands is for interacting with the database. Below is the list of all the database commands including an example parameter if one is needed.

augur db 

.. hlist::
  :columns: 1

  * add-repos
  * get-repo-groups
  * add-repo-groups        filename.csv
  * update-repo-directory  REPO_DIRECTORY
  * print-db-version
  * upgrade-db-version
  * create-schema
  * load-data



``add-repos``
--------------
The ``add-repos`` command is used to load new repos. When given a path to a correctly formatted ``.csv`` file, it will insert each repo specified in the file into its corresponding repo group in the database specified in the config file.

The ``.csv`` file must have the following format:

.. code-block::

  <repo_group_id>,<git_repo_url> 
  ...

where ``<repo_group_id>`` is a valid repository group ID, and ``<git_repo_url>`` is the url to the repository's Git repository, e.g. ``https://github.com/chaoss/augur.git``. 
Each pair of values should be on its own line (indicated by the ...), without quotes, and there should be no column headers.

Example\:

.. code:: bash

  # to add repos to the database
  augur db add-repos repos.csv

  # contents of repos.csv
  1 https://github.com/chaoss/augur.git
  2 https://github.com/chaoss/wg-evolution.git
  3 https://github.com/chaoss/metrics.git

``add-repo-groups``
--------------------
The ``add-repo-groups`` command is used to create new repo groups. When given a path to a correctly formatted ``.csv`` file, it will create each repo group specified in the file with the corresponding ID and name.

The ``.csv`` file must have the following format:

.. code-block::

  <repo_group_id>,<repo_group_name>
  ...

Where <repo_group_id> is the desired ID of the new repo group, and <repo_group_name> is the desired name of the new repo group.

Each pair of values should be on its own line (indicated by the ...), without quotes, and there should be no column headers.

Example\:

.. code:: bash

  # to add new repos to the database
  augur db add-repo-groups repo_groups.csv

  # contents of repo_groups.csv
  20 Apache Camel
  21 Apache DeltaSpike
  22 Apache Qpid
  23 Apache Tomcat


``get-repo-groups``
--------------------
The ``get-repo-groups`` command will return the ID, name, and description of all repo groups in the database.

Example\:

.. code:: bash

  # to add repos to the database
  augur db get-repo-groups

   repo_group_id  rg_name    rg_description
   1              Default    Default repo group


``update-repo-directory``
-------------------------
The ``update-repo-directory`` command will update the Facade worker repo cloning directory. When given an existing repo directory, it will modify existing records in the database and continue to update until there are no more rows to be inserted. 

Example\:

.. code:: bash

  # to update a repo in the database
  augur db update-repo-directory REPO_DIRECTORY  

  "Successfully updated the Facade worker repo directory. "



``print-db-version``
-------------------------
The ``print-db-version`` command will give the user the current version of the configured database on their system. 

Example\:

.. code:: bash

  # to return the current database version
  augur db print-db-version

  Augur DB version: 12


``upgrade-db-version``
-------------------------
The ``upgrade-db-version`` command will upgrade the user's current database to the latest version.

Example\:

.. code:: bash

  # to upgrade the user's database to the current version
  augur db upgrade-db-version

  "Your database is already up to date. "
                  OR
  "Upgrading from 11 to 12. "



``create-schema``
------------------
The ``create-schema`` command will create a schema in the configured database. 

Example\:

.. code:: bash

  # to create a schema
  augur db create-schema

  EXAMPLE

``load-data``
--------------
The ``load-data`` command will load sample data into the configured database.

Example\:

.. code:: bash

  # to load sample data into the database
  augur db create-schema

  EXAMPLE



