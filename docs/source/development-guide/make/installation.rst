Installation
=============

**THIS SECTION IS UNDER CONSTRUCTION.**

If you have questions or would like to help please open an issue on GitHub_.

.. _GitHub: https://github.com/chaoss/augur/issues

These commands are used to manage your local installation of Augur.

---------------

``make install``
-----------------
Installs the project dependencies, sets up default configuration file, and gathers database credentials.

Example\:

.. code-block:: bash

  $ make install

---------------

``make install-dev``
---------------------
The same as ``make install``, except it installs the additional developer dependencies and installs the packages in editable mode.

Example\:

.. code-block:: bash

  $ make install-dev

---------------

``make clean``
----------------
Removes logs, caches, and some other cruft that can get annoying. Use when things aren't building properly or you think an old version of augur is getting in the way.

Example\:

.. code-block:: bash

  $ make clean

---------------

``make rebuild``
----------------
Used in conjunction with ``make clean`` to remove all build/compiled files and binaries and reinstall the project. Useful for upgrading in place.

Example\:

.. code-block:: bash

  $ make rebuild

---------------

``make rebuild-dev``
---------------------
The same as ``make rebuild``, except it installs the additional developer dependencies and installs the packages in editable mode.

.. note::

  You can still use ``make clean`` as normal if something went wrong.

Example\:

.. code-block:: bash

  $ make rebuild-dev
