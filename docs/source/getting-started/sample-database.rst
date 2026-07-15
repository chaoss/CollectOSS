Sample Database
===============

We have a ready-to-use PostgreSQL database that acts as a structurally-correct sample dataset. This is a postgres container image pre-loaded with data collected by CollectOSS that can be used to help you get started quickly with your downstream project that relies on CollectOSS data, whether thats running `8Knot <https://github.com/oss-aspen/8Knot>`_, using jupyter notebooks for research, or building your own dashboard.

Image: ``ghcr.io/oss-aspen/sample-collected-data:latest``


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


