---------
Overview
---------

Metric Forms
-------------

.. note::
    
    In this document, and for the rest of section, we use the term ``repo`` to refer to a `software repository`__ - usually a Git repository.

__ https://en.wikipedia.org/wiki/Software_repository

Our metrics come in one of three forms: 

1. ``repo`` metrics
2. ``repo_group`` metrics
3. everything else

In the context of Augur, a repo group is a user-defined collection of repositories which have some relevance to each other: perhaps they exist in the same software ecosystem, are owned by the same company, or are similar in functionality. 

We strive to provide all of our metrics against both individual repos and these collections of repos, as repositories rarely exist solely by themselves and more often than not being able to get an overview of a specific group of repositories is highly useful.

We will cover how to build all 3 types of metric, starting with ``repo`` metrics. But first, let's cover the similarities between the first two.

Definition of Repo & Repo Group Metrics
----------------------------------------

``repo`` and ``repo_group`` metrics are defined by two key facts:

1. they are `timeseries <https://en.wikipedia.org/wiki/Time_series>`_ metrics (meaning each data point is only a time and some calculate value), and
2. they are filterable by time period (day/week/month/year), a begin date, and an end date.

Essentially, both provide a way to measure the different values of calculation for each point in a configurable time period.

In the context of Augur, this means that ``repo`` and ``repo_group`` metrics **must** have the following function signature:

.. code:: python

   # this is a generic signature
   metric_name(repo_group_id, repo_id, period, begin_date, end_date)

.. note:: 

    You might be asking why we include both ``repo_group_id`` and ``repo_id`` in the function, when we have thus far defined them to be two separate functions. We will see more about why this later, but in essence we define both forms of the metric in the same function, so that they stay tightly coupled and you can reference the implementation of one metric while working on the other.

By default, specifying only a ``repo_group_id`` will calculate the ``repo_group`` form of the metric across a collection of repositories, while specifying both a ``repo_id`` and a ``repo_group_id`` will calculate the ``repo`` form of the metric for a single repository. We provide convienient helper methods for creating ``repo`` and ``repo_group`` metrics, which will we cover later when creating an endpoint for a metric.

Other Metrics
--------------
All metrics with methods that deviate from this signature fall outside of the ``repo`` or ``repo_group`` classifications and must be defined more explicity, and their API endpoints must be defined more explicity - more on that later.


.. TODO: make this image better
.. image new-metric.png

Data
-----

Of course, in order to create a metric, you'll first need some data. This data can come from a variety of sources: Git repositories, issue trackers, mailing lists, Linux Foundation Badging programs, code coverage analysis tools - if it can be collected, we can help you measure it.

All this data will be persisted by Augur's workers in our database. Once the data's there, it's ready to be served through our REST API, which can be consumed by Augur's frontend or by any other presentation environment chosen.

.. seealso::

  To learn more about data collection with Augur, check out our `worker documentation`__.

__ ../../data-collection/data-collection-toc.rst
