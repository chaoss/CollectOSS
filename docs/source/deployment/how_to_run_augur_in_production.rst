Running Augur in Production
===========================

This guide explains how to run Augur in a production environment and how to configure
important environment variables such as ``AUGUR_RESET_LOGS``.

Prerequisites
-------------

Before deploying Augur in production, ensure the following are installed and configured:

- Docker and Docker Compose
- PostgreSQL (configured and accessible)
- Redis (installed and running)

Environment Variables
---------------------

Augur uses several environment variables in production. Make sure to configure the ones relevant
to your deployment:

- ``AUGUR_DB`` — PostgreSQL database connection string  
- ``AUGUR_REDIS_URL`` — Redis connection string  
- ``AUGUR_RESET_LOGS`` — controls automatic log reset on server startup

Resetting Logs with AUGUR_RESET_LOGS
-------------------------------------

Augur provides the ``AUGUR_RESET_LOGS`` environment variable to control whether logs are reset when
the server starts. This gives system administrators flexibility over log management.

Default Behavior
~~~~~~~~~~~~~~~~

If ``AUGUR_RESET_LOGS`` is **not set**, it defaults to **True**, meaning Augur will reset logs
on startup to prevent unbounded log growth.

Custom Behavior
~~~~~~~~~~~~~~~~

If set to ``False`` (or common variations), Augur will **not** reset logs automatically.  
In this case, log rotation or manual log cleanup is the responsibility of the administrator.

Usage Example
~~~~~~~~~~~~~

.. code-block:: bash

   export AUGUR_RESET_LOGS=False

Related Resources
-----------------

- https://github.com/oss-aspen/infra-ansible/
- https://github.com/chaoss/augur-utilities/

Steps to Run in Production
--------------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/chaoss/augur.git
      cd augur

2. Configure all required environment variables  
3. Set up Docker + Docker Compose or your deployment infrastructure  
4. Start Augur following your deployment method.