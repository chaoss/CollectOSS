Running CollectOSS in Production
================================

This page collects practical tips, configuration notes, and important considerations
for deploying CollectOSS in a production environment. This is a reference to help
configure CollectOSS effectively.

Environment Variables
---------------------

CollectOSS uses several environment variables in production. Make sure to configure the ones relevant
to your deployment:

- ``COLLECTOSS_RESET_LOGS`` : Controls automatic log reset on server startup
- ``COLLECTOSS_DB`` : PostgreSQL database connection string (used if variable not set)

COLLECTOSS_RESET_LOGS
---------------------

**Description:**  
Controls whether CollectOSS resets its log files every time the server starts. Useful for managing log size or integrating with external log rotation systems.

**Type:**  
boolean

**Default:**  
`True` : CollectOSS clears old logs at startup.

**Environment Variable:**  
COLLECTOSS_RESET_LOGS

**Notes:**  
If set to `False`, CollectOSS will not reset logs automatically. Administrators must ensure log rotation or cleanup is handled manually.

**Usage Example:**

.. code-block:: bash

   export COLLECTOSS_RESET_LOGS=False

COLLECTOSS_DB
-------------

**Description:**  
Specifies the connection string for the PostgreSQL database used by CollectOSS. If omitted, the default Docker database is used.

**Type:**  
string

**Default:**  
Docker container database (if `COLLECTOSS_DB` is not specified)

**Environment Variable:**  
COLLECTOSS_DB

Related Resources
-----------------

- https://github.com/oss-aspen/infra-ansible/
- https://github.com/chaoss/collectoss-utilities/