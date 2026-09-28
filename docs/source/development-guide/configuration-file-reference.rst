Configuration file reference
===============================

CollectOSS's configuration template file, which generates your locally deployed ``augur.config.json`` file, is found at ``collectoss/config.py``. You will notice a small collection of workers are turned on to start with, by examining the ``switch`` variable within the ``Workers`` block of the config file. You can also specify the number of processes to spawn for each worker using the ``workers`` command. The default is one, and we recommend you start here. If you are going to spawn multiple workers, be sure you have enough credentials cached in the ``operations.worker_oath`` table for the platforms you use.

Facade Worker Settings
-----------------------

The following settings live under the ``Facade`` section of the configuration.

``max_clone_size_kb``
~~~~~~~~~~~~~~~~~~~~~

**Description:**
Maximum allowed estimated repository size (in kilobytes) before CollectOSS refuses to clone it.
This prevents unexpectedly large repositories from consuming disk space or stalling the facade worker.

**Default:** ``5242880`` (5 GB)

**Disable:** Set to ``0`` to disable the limit entirely and clone all repositories regardless of size.

**Notes:**

- The size estimate combines the repository's bare size (from the forge API) with the sum of blob
  sizes in the working tree. For very large repositories (over 100,000 tree entries), the tree
  response may be truncated, making the estimate a lower bound. If you have repositories close to
  your configured limit, set the limit conservatively to account for this.
- When a clone is blocked, an error is logged with the estimated size and the configured limit.
  Check the facade worker logs if repositories are unexpectedly skipped.
- GitHub and GitLab repositories are supported. For other forges, cloning is blocked when a limit
  is configured, since size cannot be determined.

If you have questions or would like to help please open an issue on GitHub_.

.. _GitHub: https://github.com/chaoss/collectoss/issues
