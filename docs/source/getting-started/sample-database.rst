Sample Database
===============

A ready-to-use PostgreSQL database, pre-loaded with real project data collected by CollectOSS,
so you can run `8Knot <https://github.com/oss-aspen/8Knot>`_ — or explore the data from a
notebook — **locally, without access to a remote CollectOSS instance**.

It ships as a published container image, so there is nothing to build and no data
file to supply. ``docker compose up`` pulls it and it should be ready in seconds.

Image: ``ghcr.io/oss-aspen/sample-collected-data:latest``

Quick start with 8Knot
----------------------

1. In your 8Knot checkout, point 8Knot at the local database by setting these values in your ``.env``:

.. code:: shell

    AUGUR_HOST=sample-collected-data
    AUGUR_PORT=5432
    AUGUR_DATABASE=sample_collected_data
    AUGUR_USERNAME=sample_user
    AUGUR_PASSWORD=sample_password
    AUGUR_SCHEMA=data,augur_data

2. Start the stack from the top level of the 8Knot repository:

.. code:: shell

    podman compose up --build

8Knot is at http://localhost:8080 and reads from the sample database. The
``sample-collected-data`` service pulls the image and starts instantly (the data
is baked in, so there is no import step).

Connecting directly (psql, DBeaver, notebooks)
----------------------------------------------

The database is also exposed on **host port 5433** (mapped from the container's
5432, so it won't clash with a local PostgreSQL):

========  =========================
Setting   Value
========  =========================
Host      ``localhost``
Port      ``5433``
Database  ``sample_collected_data``
User      ``sample_user``
Password  ``sample_password``
========  =========================

.. code:: shell

    psql -h localhost -p 5433 -U sample_user -d sample_collected_data

Tables live in the ``data`` schema (the CollectOSS schema name), so qualify
queries — for example ``data.repo``, ``data.commits``, ``data.pull_requests``.

Notes
-----

- **Self-contained** — no CollectOSS credentials, API keys, or dump files required.
- **Data only** — the image contains just the ``data`` schema. The operations
  schema (user accounts, tokens, API keys) is deliberately **not** included.
- **Sample, not live** — the data is a fixed snapshot for local development and
  demos, not a continuously updated instance.
