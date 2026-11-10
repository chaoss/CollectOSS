Running CollectOSS in Production
================================

This page collects practical tips, configuration notes, and important considerations
for deploying CollectOSS in a production environment. This is a reference to help
configure CollectOSS effectively.


Architecture
------------

A production deployment runs CollectOSS as a Docker Compose stack of six services:

- ``database`` — PostgreSQL 16. Holds all collected data.
- ``redis`` — Used for caching and key management.
- ``keyman`` — Manages API keys. Runs as a non-root user.
- ``rabbitmq`` — Message broker for Celery tasks.
- ``core`` — The main CollectOSS application and API (port 5000).
- ``flower`` — Celery task monitoring dashboard (port 5555).

All services use ``restart: unless-stopped``. The ``core`` service is started only
after the database and rabbitmq pass their healthchecks.

.. note::
   RabbitMQ's ``consumer_timeout`` is disabled in production, because collection
   tasks can run for longer than the default timeout allows.

Version pinning
---------------

It is recommended to pin a specific release rather than running ``latest``, so deployments are
repeatable and rollbacks are possible. Images are published to
``ghcr.io/chaoss/collectoss`` and ``ghcr.io/chaoss/collectoss-keyman``:

.. code-block:: yaml

   image: ghcr.io/chaoss/collectoss:v1.0.0

Environment Variables
---------------------

CollectOSS uses several environment variables in production. Make sure to configure the ones relevant
to your deployment:

Database
^^^^^^^^

- ``COLLECTOSS_DB`` : Full SQLAlchemy connection string for PostgreSQL
- ``COLLECTOSS_DB_NAME`` : Database name (also used by the PostgreSQL container)
- ``COLLECTOSS_DB_USER`` : Database user (also used by the PostgreSQL container)
- ``COLLECTOSS_DB_PASSWORD`` : Database password (also used by the PostgreSQL container)

``COLLECTOSS_DB`` must be a complete connection URL, not a bare database name:

.. code-block:: bash

   export COLLECTOSS_DB=postgresql+psycopg2://user:password@database:5432/collectoss

Message broker and cache
^^^^^^^^^^^^^^^^^^^^^^^^

- ``REDIS_CONN_STRING`` : Redis connection string (e.g. ``redis://redis:6379``)
- ``RABBITMQ_CONN_STRING`` : AMQP connection string, including vhost
- ``COLLECTOSS_RABBITMQ_USERNAME`` : RabbitMQ user (also used by the RabbitMQ container)
- ``COLLECTOSS_RABBITMQ_PASSWORD`` : RabbitMQ password (also used by the RabbitMQ container)
- ``COLLECTOSS_RABBITMQ_VHOST`` : RabbitMQ vhost

API credentials
^^^^^^^^^^^^^^^

- ``COLLECTOSS_GITHUB_USERNAME`` / ``COLLECTOSS_GITHUB_API_KEY``
- ``COLLECTOSS_GITLAB_USERNAME`` / ``COLLECTOSS_GITLAB_API_KEY``

Storage and logging
^^^^^^^^^^^^^^^^^^^

- ``CONFIG_DATADIR`` : Directory containing ``collectoss.json`` (see below)
- ``CACHE_DATADIR`` : Directory for cached data
- ``CACHE_LOCKDIR`` : Directory for cache lock files
- ``COLLECTOSS_LOGS_DIRECTORY`` : Where application logs are written
- ``COLLECTOSS_RESET_LOGS`` : See below
- ``COLLECTOSS_DOCKER_DEPLOY`` : Set to ``1`` when running under Docker Compose
- ``COLLECTOSS_FLAGS`` : Comma-separated feature flags

COLLECTOSS_RESET_LOGS
---------------------

**Description:**
Controls whether CollectOSS resets its log files every time the server starts.

**Type:**
boolean

**Default:**
``True`` — CollectOSS clears old logs at startup.

**Notes:**
Production deployments should set this to ``False`` so logs survive restarts, and
instead handle rotation externally (for example, via Docker's ``json-file`` log
driver with ``max-size`` and ``max-file`` options). Combine with
``COLLECTOSS_LOGS_DIRECTORY`` to place logs on a dedicated volume.

**Usage Example:**

.. code-block:: bash

   export COLLECTOSS_RESET_LOGS=False

Configuration File
------------------

Most runtime behavior is configured through a ``collectoss.json`` file placed in the
directory pointed to by ``CONFIG_DATADIR``. Notable sections:

- ``Server`` — API host, port, and number of workers
- ``Celery`` — worker counts for core, secondary, and facade tasks
- ``Tasks`` — collection intervals (in days) for each task group
- ``Facade`` — facade behavior flags (multithreading, cache rebuilds, repo pulls)
- ``Task_Routine`` — which collection phases are enabled

Database Considerations
-----------------------

**Shutdown time:** with a large database, PostgreSQL can take a long time to shut
down cleanly. Set a generous ``stop_grace_period`` on the database container
(30 minutes in the reference deployment) and a matching ``shutdown-timeout`` in
the Docker daemon configuration.

**Storage:** keep PostgreSQL data on a dedicated volume, and maintain ample free
space — checkpointing and backup activity during collection can generate large
amounts of WAL. The reference deployment keeps 500 GB of headroom on the data
volume.

Host-Level Configuration
------------------------

- **Docker log rotation:** configure the ``json-file`` log driver with
  ``max-size`` and ``max-file`` limits so container logs cannot fill the disk.
- **Monitoring:** expose Docker daemon metrics (``metrics-addr``) and install
  ``prometheus-node-exporter`` for host metrics. Flower (port 5555) provides
  visibility into Celery task queues.

Related Resources
-----------------

- `CollectOSS v1.0 Migration Guide <https://github.com/chaoss/CollectOSS/wiki/Migration-Guide>`_
- `CollectOSS Utilities <https://github.com/chaoss/collectoss-utilities>`_ repo for one-off data migrations and fix scripts that may help older instances.
- `CollectOSS Monitoring Grafana Stack <https://github.com/chaoss/collectoss-monitoring>`_