Collecting data
===============

Now that you've installed Augur's application server, it's time to configure your data collection workers.

There are 2 pieces to data collection with Augur: the housekeeper, and the data collection workers. The housekeeper creates long-running "jobs" that specify what kind of data to collect for what set of repositories. The data collection workers can then accept these jobs, after which it will use the information provided in the job to find the repositories in question and collect the requested data.

Since the default housekeeper setup will work for most use cases, we'll first cover how to configure the workers and then briefly touch on the housekeeper configuration options, after which we'll cover how to add repos and repo groups to the database.

Configuring the Workers
------------------------

There are a few workers that ship ready to collect out of the box:

- ``facade_worker`` (collects raw commit and contributor data by parsing Git logs)
- ``github_worker`` (collects issue data from the GitHub API)
- ``contributor_worker`` (collects contributor data from the GitHub API)
- ``pull_request_worker`` (collects pull request data from the GitHub API)
- ``repo_info_worker`` (collects repository statistics from the GitHub API)
- ``release_worker`` (collects release data from the GitHub API)
- ``linux_badge_worker`` (collects `CII badging <https://bestpractices.coreinfrastructure.org/en>`_ data from the CII API)
- ``insight_worker`` (queries Augur's metrics API to find interesting anomalies in the collected data)

All worker configuration options are found in the ``Workers`` block of the ``augur.config.json`` file (which was generated for you at the end of the previous section). This file is located at ``$HOME/.augur/augur.config.json``. Each worker has its own subsection with same title as the the worker's name. We recommend leaving the defaults and only changing them when explicitly necessary, as the default parameters will work for most use cases. Read on for more on how to make sure your workers are properly configured.

Standard configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each worker has 3 configuration options that are standard across all workers. The worker-specific options are detailed in the sections following this one.

The standard options are:

- ``switch``, a boolean flag indicating if the worker should automatically be started with Augur. Defaults to ``0`` (false).
- ``workers``, the number of instances of this worker that Augur should spawn if ``switch`` is set to ``1``. Defaults to ``1`` for all workers except the ``value_worker`` and ``insight_worker``.
- ``port``, which is the base TCP port the worker will use the communicate with Augur's broker. The default is different for each worker, but the lowest is ``50100`` and each worker increments the default starting port by 100. If the ``workers`` parameter is > 1, then workers will bind to ``port`` + ``i`` for the ``i``'th worker spawned

Keeping ``workers`` at 1 should be fine for small collection sets, but if you have a lot of repositories to collect data for, you can raise it. We also suggest double checking that the default  worker ports are free on your machine.

Worker-specific configuration options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next up are the configuration options specific to each worker (but some workers require no additional configuration beyond the defaults). The most pertinent of these options is the ``facade_worker``'s ``repo_directory``, so make sure to pay attention to that one.

``facade_worker``
::::::::::::::::::

- ``repo_directory``, which is the local directory where the ``facade_worker`` will clone the repositories it needs to analyze. You should have been prompted for this during installation, but if you need to change it, make sure that it's an absolute path (environment variables like ``$HOME`` are not supported) and that the directory already exists. Defaults to ``repos/``, but it's highly recommended you change this.

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
-----------------------------

If you're using the Docker container, you can use the `provided UI <../docker/usage.html>`_ to load your repositories. Otherwise, you'll need to use the `Augur CLI <command-line-interface/db.html>`_ to load your repositories. Please reference the respective sections of the documenation for detailed instructions on how to accomplish both of these steps.

Running collections
--------------------

Congratuations! At this point you (hopefully) have a fully functioning and configured Augur instance.

After you've loaded your repos, you're ready for your first collection run. We recommend running only the default workers first to gather the initial data. If you're collecting data for a lot of repositories, or repositories with a lot of data, we recommend increasing the number of ``github_workers`` and ``pull_request_workers``.

You can now run Augur and start the data collection by issuing the ``augur backend start`` command in the root ``augur`` directory. All your logs (including worker logs and error files) will be saved to a ``logs/`` subdirectory in that same folder, but this can be customized - more on that and other logging utilities `in the development guide <../development-guide/logging.html>`_.

Once you've finished the initial data collection, we suggest then running the ``value_worker`` (if you have it installed) and the ``insight_worker``. This is because the ``value_worker`` depends the source files of the repositories cloned by the ``facade_worker``, and the ``insight_worker`` uses the data from all the other workers to identify anomalies in the data by by performing statistical analysis on the data returned from Augur's metrics API.

You're now ready to start exploring the data Augur can gather and metrics we can generate. If you're interested in contributing to Augur's codebase, you can check out the `development guide <../development-guide/toc.html>`_. For information about Augur's frontend, keep reading!

Happy collecting!
