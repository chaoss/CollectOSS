====================
Database Commands
====================

``augur db``
=============

The collection of the ``augur db`` commands is for interacting with the database. Below is the list of all the database commands including an example parameter if one is needed.

.. hlist::
  :columns: 1

  * ``add-repo-groups filename.csv``
  * ``add-repos filename.csv``
  * ``get-repo-groups``
  * ``update-repo-directory REPO_DIRECTORY``
  * ``generate-api-key``
  * ``get-api-key``
  * ``print-db-version``
  * ``upgrade-db-version``
  * ``create-schema``

``add-repo-groups``
--------------------
The ``add-repo-groups`` command is used to create new repo groups. When given a path to a correctly formatted ``.csv`` file, it will create each repo group specified in the file with the corresponding ID and name.

The ``.csv`` file must have the following format::

  <repo_group_id>,<repo_group_name>
  ...

Where ``<repo_group_id>`` is the desired ID of the new repo group, and ``<repo_group_name>`` is the desired name of the new repo group.

Each pair of values should be on its own line (indicated by the ...), without quotes, and there should be no column headers.

Example usage\:

.. code-block:: bash

  # to add new repos to the database
  $ augur db add-repo-groups repo_groups.csv

  # contents of repo_groups.csv
  10,Repo Group 1
  20,Repo Group 2


``get-repo-groups``
--------------------
The ``get-repo-groups`` command will return the ID, name, and description of all repo groups in the database.

Example usage\:

.. code-block:: bash

  # to add repos to the database
  $ augur db get-repo-groups

  # successful output looks like:
  > repo_group_id  rg_name    rg_description
    1              Default    Default repo group


``add-repos``
--------------
The ``add-repos`` command is used to load new repos. When given a path to a correctly formatted ``.csv`` file, it will insert each repo specified in the file into its corresponding repo group in the database specified in the config file.

The ``.csv`` file must have the following format:

.. code::

  <repo_group_id>,<git_repo_url> 
  ...

where ``<repo_group_id>`` is an **existing** repository group ID, and ``<git_repo_url>`` is the url to the repository's Git repository, e.g. ``https://github.com/chaoss/augur.git``. 
Each pair of values should be on its own line (indicated by the ...), without quotes, and there should be no column headers.

Example usage\:

.. code-block:: bash

  # contents of repos.csv
  10,https://github.com/chaoss/augur.git
  10,https://github.com/chaoss/grimoirelab.git
  20,https://github.com/chaoss/wg-evolution.git
  20,https://github.com/chaoss/wg-risk.git
  20,https://github.com/chaoss/wg-common.git
  20,https://github.com/chaoss/wg-value.git
  20,https://github.com/chaoss/wg-diversity-inclusion.git
  20,https://github.com/chaoss/wg-app-ecosystem.git


  # to add repos to the database
  $ augur db add-repos repos.csv

.. note::

  If you don't know what ``repo_group_id`` to use, run the ``augur db get-repo-groups`` command to view the repo groups that are currently in your DB; unless you've deleted it, there should be a default one that you can use.

``update-repo-directory``
-------------------------
The ``update-repo-directory`` command will update the Facade worker repo cloning directory. When given an existing repo directory, it will modify existing records in the database and continue to update until there are no more rows to be inserted. 

Example usage\:

.. code-block:: bash

  # to update a repo in the database
  $ augur db update-repo-directory REPO_DIRECTORY  

  # successful output looks like:
  > Successfully updated the Facade worker repo directory.


``generate-api-key``
-------------------------
The ``generate-api-key`` command will generate a new Augur API key and update the database with the new key. Output is the generated key.

Example usage\:

.. code-block:: bash

  # to generate a key
  $ augur db generate-api-key

  # successful output looks like (this will be an actual key):
  > some_new_key_abc_123


``get-api-key``
-------------------------
The ``get-api-key`` command will return the API key of the currently configured database. Output is the API key.

Example usage\:

.. code-block:: bash

  # to retrieve the key
  $ augur db get-api-key

  # successful output looks like (this will be an actual key):
  > some_existing_key_def_456


``print-db-version``
-------------------------
The ``print-db-version`` command will give the user the current version of the configured database on their system. 

Example usage\:

.. code-block:: bash

  # to return the current database version
  $ augur db print-db-version

  # successful output looks like:
  > 15


``upgrade-db-version``
-------------------------
The ``upgrade-db-version`` command will upgrade the user's current database to the latest version.

Example usage\:

.. code-block:: bash

  # to upgrade the user's database to the current version
  $ augur db upgrade-db-version

  # successful output looks like this your DB is up to date
  > Your database is already up to date. 

  # successful output looks like this if your DB needs to be upgraded
  > Upgrading from 11 to 12. 


``create-schema``
------------------
The ``create-schema`` command will attempt to create the Augur schema in the database defined in your config file. 

Example usage\:

.. code-block:: bash

  # to create the schema
  $ augur db create-schema

.. note::
  If this runs sucessfully, you should see a bunch of schema creation commands fly by pretty fast. If everything worked you should see: ``update "augur_operations"."augur_settings" set value = 14 where setting = 'augur_data_version';`` at the end.
