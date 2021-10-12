Configuration file reference
===============================

Augur's configuration template file, which generates your locally deployed ``augur.config.json`` file, is found at ``augur/config.py``. You will notice a small collection of workers are turned on to start with, by examining the ``switch`` variable within the ``Workers`` block of the config file. You can also specify the number of processes to spawn for each worker using the ``workers`` command. The default is one, and we recommend you start here. If you are going to spawn multiple workers, be sure you have enough credentials cached in the ``augur_operations.worker_oath`` table for the platforms you use. 

If you have questions or would like to help please open an issue on GitHub_.

.. _GitHub: https://github.com/chaoss/augur/issues