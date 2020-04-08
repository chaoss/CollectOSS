~~~~~~~~~~~~~~~~~~~~~~~
Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~~

Augur provides a command line interface (CLI) for controlling interacting with the system. They're broken up into 4 categories: ``run``, ``db``, and ``util``. 

Each command is invoked by first specifying the category, then the command name, and then the parameters/options; e.g. the ``list`` command under ``augur util`` would be invoked as ``augur util list --option1 ...``. ``run`` only has a single command, so it is invoked as ``augur run``.

.. note::

    Throughout this section of the documentation, all lines that start with a ``$`` denote a ``bash`` command, and lines with ``>`` denote some sample output of command.

.. toctree::
   :maxdepth: 1

   db
   run
   util
   configure