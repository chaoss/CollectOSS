Overview
=============================================

Getting Started
---------------

See our `Contributing to Augur </CONTRIBUTING.md>`__ guide for specifics
on how we review pull requests. tl;dr: Fork our repo. Make a change. Use
the mailing list for
`CHAOSS <https://lists.linuxfoundation.org/mailman/listinfo/oss-health-metrics>`__,
Submit a pull request.

Building Changes
----------------

After making your changes, run

.. code:: bash

    make build

to update the docs and frontend before adding them to your staging area.

.. code:: bash

    make docs

Augur Development Overview
--------------------------

tl;dr
~~~~~

1. `Installation <2-install.html>`__
2. `Backend Development Guide <3-backend.html>`__
3. `Frontend Development Guide <4-frontend.html>`__
4. `Testing Guide <5-testing.html>`__

Augur's Design Value System
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Augur's architecture is designed with an eye toward fulfilling its
primary missions of rapid open source software metric prototyping and
using data visualization to facilitate discussions among folks who
manage open source communities.

**Core aims**

1. Rapid metrics prototyping
2. Using data visualization to support discussion

**Our visualization design follows two principles:** 1. Allow
comparisons across projects 2. Where logical, show trends over time on a
metric

Project comparison helps people understand what a metric tells them. If
I show you total commits in a month or a year, what does that tell you
about the health of an open source project? If you are able to compare a
project you are managing with a project or two in the same space that
you are familiar with, is that helpful? In most cases the answers are
yes. We aim to produce not only metrics, but enough information for
consumers of Augur to construct meaning. Which then helps the CHAOSS
community build better, more useful metrics.

Time is, in effect, a project focused type of comparison. If you can see
the changes in different metrics on your project over time, its easier
to maintain awareness of how metrics compare with results.

--------------------

Augur's Architecture
--------------------

In our aspiration to implement our value system for metrics in software,
we seperate concerns pragmatically. Any metrics dashboard system has to
do 4 things: 1). Ingest data 2). store data 3). reshape data for
analysis 4). present data

Of course, these "dashboard requirements" can be interpreted and
circumvented. For example, if robust API's are available, like the
`GitHub Version 4 API <https://developer.github.com/v4/>`__, persistence
can be considered optional.

Right now, Augur satisfies the enumerated dashboard system requirements
in concrete ways we describe in the following four sections.

Augur Data Ingestion
~~~~~~~~~~~~~~~~~~~~

We use the GHTorrent database, or its MSR14 little brother to help you
get up and running quickly. You may find this dataset insufficient for a
particular metric you want to build. API's available from a number of
places can be accessed from Augur.

Inside your Augur system root directory there is another directory named
``augur``. This is where the Python library lives, including the data
source plugins (in ``datasources``), functionality plugins (in
``plugins``), and the web API (in ``server.py``). Below is the list of
default data sources shipped with Augur:

1. **ghtorrent** : reads the ghtorrent database you installed
2. **facade** : reads a copy of the Facade database, developed by Brian
   Warner
3. **githubapi** : Pulls data from the GitHub API
4. **downloads** : gathers download statistics for github repositories.
   Currently configured for npm and ruby gems download data.
5. **librariesio** : Pulls data from the libraries.io API (Package
   manager download data)
6. **localcsv** : Pulls data from a .csv file you persist.

If you want to ingest substantial amounts of new data, you may want to
contribute to the
`Augur-OSSifragae <https://github.com/chaoss/augur-ossifragae>`__
project, which focuses on systematic, structured ingestion of open
source respository data from heterogeneous sources. (Note: an
`Ossifragae <https://en.wikipedia.org/wiki/Bearded_Vulture>`__ is a
bearded vulture that is one of a handful of birds said to yield valid
signs for ancient Roman Augurs (visionaries) to follow. We think the
existance of "OSS" at the beginning of the birds name is a sign. We took
it.)

Augur Data Storage
~~~~~~~~~~~~~~~~~~

The database system that you built with GHTorrent or MSR14 is our
principle data storage environment right now. We have added a few small
details to the GHTorrent database in a seperate schema called
GHTorrent\_Plus. This schema is built on deployment, and supports
aggregations of the GHTorrent Schema information so that metrics can be
generated more quickly in a few cases.

Augur Data Reshaping for Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that you understand the basic structure of Augur, our `Back End
Development Guide <3-backend.md>`__ will be the place to start for
reshaping data and building out analysis endpoints. The end result of
new back end code is a **REST API Endpoint.**

Augur Data Presentation
~~~~~~~~~~~~~~~~~~~~~~~

Once you have a **REST API Endpoint**, you can stop and say, "I have
built an endpoint. Here is my pull request". OR, you can build front end
visualizations for those endpoints, following our `Front End Development
Guide <4-frontend.md>`__.

--------------

Important notes about contributing metrics
------------------------------------------

Before we start, there are a few things we would like to go over. Please
take the time to read this section carefully; not only will it will make
your life much easier, but also the lives of all the other contributors!

Some of the metrics we develop are defined more formally by metrics
committees and working groups; some are not. Should you choose to work
on implementing any of these metrics that are formally defined, they
should be placed under their respective category, wherever you are
adding it.

Across the project, metric groups are ordered as such: 1). Diversity and
Inclusion (D&I) 2). Growth, Maturity, and Decline (GMD) 3). Risk 4).
Value 5). Experimental

This order is followed across the project. Data source files, test
files, ``server.py``, ``AugurAPI.js``, frontend cards, and other places
that metrics appear in should adhere to this order for maximum
uniformity (In ``AugurAPI.js``, Git metrics have their own section).

If you are adding a new metric that does **not** fall under one of these
categories, it should be placed in the Experimental group in the correct
sub-category. If you would like to add a new Experimental sub-category,
please open a pull request with your proposed addition. In addition,
please update the file mentioned above to include your new metric: it
can be found at ``augur/docs/scratchpad/master-metrics-order.md``.

Files where metrics appear should include a header for every group, even
if there are no relevant metrics in that group. The exception to this
rule are the frontend tab cards; these are already grouped.
