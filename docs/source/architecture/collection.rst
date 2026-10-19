CollectOSS Data Collection Flow
===============================

Overview
--------

The diagram below shows the end-to-end flow from a user adding a repository to
data from the supported forges being stored in the database.

.. image:: images/collection-data-flow.png
    :width: 100%
    :alt: CollectOSS Data Collection Flow

The rest of this page walks through that flow step by step.

1. Adding a repository
----------------------

A user adds a repository through one of three entry points: the frontend UI,
the CLI, or the REST API. All three submit the request to the same backend
application, which writes the repository record to the Postgres database.

2. Storing the repository
-------------------------

The backend/application layer persists the new repository (and its related
operational state) in the Postgres database. 

See the :doc:`database <../schema/toc>` section for more details.

If the repository already exists, it is simply updated or skipped rather than duplicated.

3. Scheduled collection
-----------------------

Data collection is driven by a scheduled Celery task,
``collection_monitor`` (see ``collectoss/tasks/start_tasks.py``).
This task is scheduled to run periodically (every 30 sec by default) and detects
new repositories that need to be collected or recollected.

4. Dispatching collection tasks
-------------------------------

On each run, the collection monitor task will:

1. Queries the database for repositories due for collection, based on the
   per-phase collection intervals configured in ``SystemConfig``
   (core, secondary, facade, and ML phases).
2. Builds a :class:`~collectoss.tasks.util.collection_util.CollectionRequest`
   per enabled phase and dispatches the individual collection tasks.

These dispatched collection tasks are routed onto separate Celery queues:

- The core task queue is used for collecting "core" data (issues, pull requests, and other basic first-level information). This task, at least for github, primarily relies on the github REST API.
- The secondary task queue is used for collecting "secondary" data (issue comments, pr comments, and other second-level information). This task, at least for github, primarily relies on the github GraphQL API.
- The facade task queue is used for collecting "facade" data (commit messages, commit author information, and other information). This task is primarily responsible for data acquired via a git clone.
- The ML task queue is used for metrics processed using ML techniques.
- the scheduling queue is used for the collection machinery itself, ``collection_monitor``,  periodic cleanup tasks, etc.

These queues are all managed through Celery, which uses RabbitMQ
as its message broker and Redis/Valkey as its result backend.

5. Fetching API keys
--------------------

Before a task can talk to a forge, it obtains the appropriate API credentials
from Keyman, the key management service. This credential rotation helps allow Collection
to continue, even if one credential hits its rate limit.

6. Fetching data
-----------------

Collection tasks query the appropriate forges (Currently github, soon to be configurable)
pull the data for their repository (commits, issues, pull requests, etc., as
enabled per phase)


7. Writing data
---------------

The collection tasks write the results into the ``data`` schema of the
Postgres database. This is the same database schema that the repository record was written to in step 2.