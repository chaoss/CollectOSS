~~~~~~~~~~~~~~~~~~~~~~~
Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~~

Augur provides a command line interface (CLI) for interacting with your Augur installation. It's broken up into a few categories: ``db``, ``run``, ``util``, ``configure``, and ``logging``.

Each command is invoked by first specifying the category, then the command name, and then the parameters/options; e.g. the ``list`` command under ``augur util`` would be invoked as ``augur util list --option1 ...``. The only exception is ``run``; it only has a single command, so it is invoked as ``augur run``.

.. note::

    Throughout this section of the documentation, all lines that start with a ``$`` denote a ``bash`` command, and lines with ``>`` denote some sample output of command.

.. toctree::
   :maxdepth: 1

   db
   run
   util
   configure
   logging