Collecting Data
===============

Once you've installed Augur's backend, it's time to configure your data collection setup.

There are 2 pieces to data collection with Augur: the data collection workers and housekeeper. The workers are responsible for collecting data, and the housekeeper is responsible for creating tasks for the workers to carry out based on what you've asked it to collect. We'll cover the workers first, and then the housekeeper, after which we'll go over how to add repos to the database for collection.

Here's a TL;DR\:
If you just have Python installed, set the ``switch`` option to ``1`` for the following workers:

- ``facade_worker``
- ``github_worker``
- ``pull_request_worker``
- ``repo_info_worker``
- ``linux_badge_worker``

After you've collected the data, set the switch option to ``1`` for the ``insight_worker`` to detect anomalous activity in your repos.

Workers
--------

Here are the workers that ship ready to work with Augur by default:

- ``facade_worker`` (collects raw commit and contributor data from Git logs)
- ``github_worker`` (collects issue and contributor data from the GitHub API)
- ``pull_request_worker`` (collects pull request data from the GitHub API)
- ``repo_info_worker`` (collects repository statistics from the GitHub API)
- ``release_worker`` (collects release data from the GitHub API)
- ``linux_badge_worker`` (collects `CII <https://bestpractices.coreinfrastructure.org/en>`_ data from the CII API)
- ``insight_worker`` (queries Augur's metrics API to find interesting anomalies in the collected data)

If you have ``go`` 1.12 or later installed. you can also use the ``value_worker``, which uses a Go package called `scc <https://github.com/boyter/scc>`_ to run COCOMO calculations.

Augur's workers are configured using an ``augur.config.json`` file, which will be generated the first time ``make install`` is run. All worker configuration options are found in the ``Workers`` block of the config file, with each worker having its own configuration block within.

A full config file reference can be found on the next page, but we recommend leaving the defaults and only changing them when necessary; read on for more on how to make sure your workers are properly configured.


Standard configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each worker has 3 configuration options that are standard across all workers. The worker-specific options are detailed in the sections following this one.

The standard options are:

- ``switch``, a binary flag indicating if the worker should automatically be started with Augur. Defaults to ``0`` (false).
- ``workers``, which is the number of instances of the worker that Augur should spawn if ``switch`` is set to ``1``. Defaults to ``1``.
- ``port``, which is the base TCP port the worker will use the communicate with Augur's broker. Defaults to ``50x00``, where ``x`` is between 1 and 8 depending on the worker. If the ``workers`` parameter is > 1, then workers will bind to ``port`` + ``i`` for the 'i' th worker spawned

For your first collection run, we suggest turning on the ``switch`` flag for the ``facade_worker``, the ``github_worker``, the ``pull_request_worker``, the ``repo_info_worker``, and the ``linux_badge_worker``. The data collection time can vary greatly, depending on the number of repos you're collecting and what kind of machine you're running on.

Once those have collected all data, we suggest then running the ``value_worker`` (if you have it installed) and the ``insight_worker``. This is because the ``value_worker`` depends the source files of the repositories cloned by the ``facade_worker``, and the ``insight_worker`` uses the data from all the other workers to identify anomalies in the data by by performing statistical analysis on the data returned from Augur's metrics API.

Keeping ``workers`` at 1 should be fine for small collection sets, but if you have a lot of repositories to collect data for, you can raise it. We also suggest double checking that the ports ``50100`` through ``50800`` are free on your machine. For each ``worker`` instance, the worker will find the next lowest available port starting at value of ``port`` (e.g. worker one has ``501000``, worker 2 has ``50101``, worker 3 has ``50102``, etc), so if you're going to use multiple instances you'll need to check those ports as well.


Worker-specific configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


``facade_worker``
::::::::::::::::::

- ``repo_directory``, which is where the ``facade_worker`` clones the repositories to on your local machine. Defaults to ``repos/``, but you'll need to either create it or set it to a valid path on installation. 

``insight_worker``
::::::::::::::::::

We recommend leaving the defaults in place for the insight worker unless you interested in other metrics, or anomalies for a different time period. 

- ``training_days``, which specifies the date range that the ``insight_worker`` should use as its baseline for the statistical comparison. Defaults to ``365``, meaning that the worker will identify metrics that have had anomalies compared to their values over the course of the past year, starting at the current date.

- ``anomaly_days``, which specifies the date range in which the ``insight_worker`` should look for anomalies. Defaults to ``2``, meaning that the worker will detect anomalies that have only occured within the past two days, starting at the current date.

- ``contamination``, which is the "sensitivity" parameter for detecting anomalies. Acts as an estimated percentage of the training_days that are expected to be anomalous. The default is ``0.041`` for the default training days of 365: 4.1% of 365 days means that about 15 data points of the 365 days are expected to be anomalous.

- ``metrics``, which specifies which metrics the ``insight_worker`` should run the anomaly detection algorithm on. This is structured like so::

    {
        'endpoint_name_1': 'field_1_of_endpoint',
        'endpoint_name_1': 'field_2_of_endpoint',
        'endpoint_name_2': 'field_1_of_endpoint',
        ...
    } 

    # defaults to the following

    {
        "issues-new": "issues", 
        "code-changes": "commit_count", 
        "code-changes-lines": "added", 
        "reviews": "pull_requests", 
        "contributors-new": "new_contributors"
    }

``value_worker``
::::::::::::::::::


- ``scc_bin``, the command that the ``value_worker`` should use to invoke ``scc``. If installed with ``go get github.com/boyter/scc``, then the default of ``scc`` should probably work, but double check for your particular Go installation.

Housekeeper
------------

**We strongly recommend leaving the default housekeeper blocks generated by the installation process, but if you would like to know more, or fine-tune them to your needs, read on.**

The housekeeper is responsible for generating the tasks that will tell the workers what data to collect, and how. Housekeeper configuration options are found in the ``Housekeeper`` block of the config file. The ``Housekeeper`` block has a single key, ``jobs``, which is an array of tasks the housekeeper should create. Each task has the following structure::

    {
        "delay": <int>,
        "given": [
            "<string>"
        ],
        "model": "<string>",
        "repo_group_id": <int>,
        ... //other task-specific parameters
    }

- the ``delay`` parameter is the amount of time the housekeeper should wait before scheduling a new update task
- the ``given`` parameter is used in conjunction with the ``model`` parameter to determine which workers can accept a data collection task. Each worker can collect data if it is "given" data in a certain format, for example a ``github_url`` (in the case of the ``github_worker`` and ``pull_request_worker``) or perhaps just any valid ``git_url`` (as in the case of the ``facade_worker``)
- the ``model`` parameter is the other parameter used to determine which workers can accept a given task. It represents the part of the conceptual data model that the worker can fulfill; for example, the ``facade_worker`` fills out the ``commits`` model since it primarly gathers data about commits, and the ``github_worker`` fills out both the ``issues`` and ``contributors`` model.
- the ``repo_group_id`` parameter specifies which group of repos the housekeeper should collect data for; use the default of ``0`` to specify ALL repo groups in the database.

Adding repos for collection
-----------------------------------

If you're using the Docker container, you can use the `provided UI <../docker/usage.html>`_ to load your repositories. Otherwise, you'll need to use the `Augur CLI <command-line-interface/db.html>`_ to load your repositories. Please see the respective sections of the documenation for precise instructions on how to accomplish both of these steps.

Next steps
-----------

Congratuations! At this point you (hopefully) have a fully functioning and configured Augur instance. 

You can now run Augur and start the data collection by running ``augur run`` in the root ``augur/`` directory, or check out the `CLI <command-line-interface/toc.html>`_ to learn more about how to control Augur. 

Happy collecting!