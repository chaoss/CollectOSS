Data Model
===========

The latest version of Augur includes a schema_ that brings together data from : 

1. git repositories, including GitHub
2. issue trackers
3. mailing lists
4. library dependency trees
5. the Linux Foundation's badging program
6. code complexity and contribution counting ... and MUCH MUCH MORE. 

This document details how to create the schema as well as some information on its contents and design.

-----------------------
Creating the schema
-----------------------

The process for creating the schema is detailed in the  `database section <../getting-started/database.html>`_ of the Getting Started guide.

----------------
Schema Overview
----------------

Augur Data
----------

The ``augur_data`` schema contains *most* of the information analyzed
and constructed by Augur. The origin’s of the data inside of augur are:

1. ``workers/augur_github_worker``: Pulls data from the GitHub API.
Presently this is focused on issues, including issue_comments,
issue_events, issue_labels and contributors. Note that all messages are
stored in Augur in the ``messages`` table. This is to facilitate easy
analysis of the tone and characteristics of text communication in a
project from one place.

2. ``workers/facade_worker``: Based on
http://www.github.com/brianwarner/facade, but substantially modified in
the fork located at http://github.com/sgoggins/facade. The modifications
include modularization of code, connections to Postgresql data instead
of MySQL and other changes noted in the commit logs.

3. ``workers/insight_worker``: Generates summarizations from raw data
gathered from commits, issues, and other info.

4. ``workers/linux_badge_worker``: Pulls data from the Linux Foundation’s
badging program.

5. ``workers/value_worker``: Populates the table
``repo_labor`` using the “SCC” tool provided the
https://github.com/boyter/scc project. “SCC” required Go to be installed on your system. Visit `this resource <https://golang.org/doc/install>`__ for instructions on Go installation.

6. ``workers/pull_request_worker``: Collects Pull Request related data such as commits, contributors,assignees, etc. from the Github API and stores it in the Augur database.

Augur Operations
----------------

The ``augur_operations`` tables are where most of the operations tables
are going to exist. There are a few, like ``settings`` that remain in
``augur_data`` for now, but will be moved. They keep records related to
analytical history and data provenance for data in the schema. They also
store information including API keys.

SPDX
----

The ``spdx`` schema serves the storage for software bill of materials
and license declarations scans on projects, conducted using this fork of
the DoSOCSv2 project: https://github.com/Nebrethar/DoSOCSv2

.. _schema:

--------------------
Complete Data Model
--------------------
.. image:: schema.png
  :width: 1200
  :alt: Augur Unified Schema 
