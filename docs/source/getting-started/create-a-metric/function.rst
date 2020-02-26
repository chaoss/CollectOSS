--------------------------------------
Create a Metric Function
--------------------------------------

There are 2 discrete steps in creating a new metric function:

1. Write a PostgreSQL query against Augur's schema to pull out your desired data
2. Wrap & parameterize the SQL query in a metric function in the :py:mod:`augur.metrics` module

Writing a SQL query
--------------------

We highly recommend using a database visualization tool to rapidly test and write your query.
`pgAdmin <https://www.pgadmin.org/>`_ is a great free and open source tool for this task, and comes highly recommended by most of the Augur team (who are primarly college students and can't afford professional database administration tooling).

.. seealso::
    Details about Augur's schema can be found `here <../../architecture/data-model.html#schema-overview>`_.

For this guide, we will be using the following PostgreSQL queries\:

  .. code-block:: postgresql
    :linenos:
    :emphasize-lines: 1, 14

    -- repo_group form of the issues_new metric
    SELECT
        issues.repo_id,
        repo_name,
        date_trunc(:period, issues.created_at::DATE) as date,
        COUNT(issue_id) as issues
    FROM issues JOIN repo ON issues.repo_id = repo.repo_id
    WHERE issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
    AND issues.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
    AND issues.pull_request IS NULL
    GROUP BY issues.repo_id, date, repo_name
    ORDER BY issues.repo_id, date

    -- repo form of the issues_new metric
    SELECT
        repo_name,
        date_trunc(:period, issues.created_at::DATE) as date,
        COUNT(issue_id) as issues
    FROM issues JOIN repo ON issues.repo_id = repo.repo_id
    WHERE issues.repo_id = :repo_id
    AND issues.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
    AND issues.pull_request IS NULL
    GROUP BY date, repo_name
    ORDER BY date;

.. note::
    ``:period``, ``:repo_group_id``, ``:begin_date``, ``:end_date``, and ``:repo_id`` are all query parameters. When you're testing, you'll need to use actual values, like ``20`` for the ``:repo_id``. We'll cover more on query parameters in the section below.

Once you've written your SQL query, it's time to wrap it in a metric function. 

``repo``/``repo_group`` functions
-------------------------------------------

Any new metric you want to implement must be implemented as a function in ``augur/metrics/<model>/<model>.py``, where ``model`` is the name of the conceptual data model for which the metric provides data. 

.. seealso:: 
    For all model definitions please refer to the :py:mod:`augur.metrics` module in the `Python library documentation`__.

__ ../../library-documentation/python.html#metric-modules

Let's first break down the basic structure of one of these typical ``repo``/``repo_group`` metric functions. 
As with most things, we'll start at the beginning: the function name and docstring.

    .. code-block:: python
        :linenos:

        @annotate(tag=<metric-tag>)
        def <metric_name>(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
        """
        <brief description of the metric>

        :param repo_group_id: The repository's repo_group_id
        :param repo_id: The repository's repo_id, defaults to None
        :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
        :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
        :param end_date: Specifies the end date, defaults to datetime.now()
        :return: DataFrame of <whatever the metric calculates, e.g. new issues per day>
        """

Here, we define a metric function called ``<metric_name>`` that requires a ``repo_group_id``, and optionally takes a ``repo_id``, ``period``, ``begin_date``, and ``end_date``. The reason why ``repo_id`` is optional will become clear shortly.

When defining a function, you must provide a docstring with a brief description of what the metric calculates, as well as a description of the parameters and return type. For all ``repo``/``repo_group_id``, you can use the parameter/return type section in the snippet above. 

.. note::

    **All metric functions must return a DataFrame.**

We must also decorate the function as a metric with ``@annotate``, and provide a valid metric tag. This decorator is what tells Augur that this is a metric function, so that the function will be available to be used in an endpoint. You must provide a ``<metric-tag>`` argument to this function, which by convention is the name of the metric function with a ``-`` in place of any ``_`` that may appear (e.g. a metric named ``issue_response_time`` would have the tag ``issue-reponse-time``).

Next, we'll set our date parameters.

    .. code-block:: python
        :lineno-start: 14

        if not begin_date:
            begin_date = '1970-1-1 00:00:00'

        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

This sections handles the defaults for the ``begin_date`` and ``end_date`` query parameters, if they were not specified.

Now, we'll set up and execute the correct SQL query. Before, we do that however, it's time to explain why a ``repo``/``repo_group`` metric function must be passed both a ``repo_id`` and a ``repo_group_id``.


Every ``repo``/``repo_group_id`` metric function *must* contain the defintion for both the ``repo`` and ``repo_group`` form. This is because we feel that more often than not, the forms will be very similar, and having
the SQL queries defined in the same function makes it easier to cross-reference one query when working on the other. Let's look at an example.

First, the ``repo_group`` form\:

    .. code-block:: python
        :lineno-start: 20

        <metric_name_SQL> = ''

        if not repo_id:
            <metric_name_SQL> = s.sql.text("""
                <repo_group form of the query>
            """)

            results = pd.read_sql(<metric_name_SQL>, self.database, params={'repo_group_id': repo_group_id, 'period': period,'begin_date': begin_date, 'end_date': end_date})

            # if necessary, do some more transformations or calculations on the result

            return results

We know we need to execute the ``repo_group`` form because we were not given a ``repo_id`` to use, so instead we will use the ``repo_group_id`` that we were given.
After setting the correct query and executing it, one may wish to do additional calculations or transformations of the data if necessary. After that, the results are returned.

Now, let's look at the ``repo`` form\:

    .. code-block:: python
        :lineno-start: 33

        else:
            <metric_name_SQL> = s.sql.text("""
                <repo form of the SQL query>
            """)

            results = pd.read_sql(<metric_name_SQL>, self.database, params={'repo_id': repo_id, 'period': period, 'begin_date': begin_date, 'end_date': end_date})

            # if necessary, do some more transformations or calculations on the result

            return results

In the ``else`` block of the ``if`` statement on line BLANK of snippet above this one, a ``repo_id`` has been passed in, and so that form will be calculated instead. As with the ``repo_group`` form, after retrieving the data, additional 
calculations or transformations will be applied and then the results are returned.


.. note:: 
    Query parameters (lines 40 & 54) are used to dynamically insert values (like the given ``repo_id``) into a SQL statement. The use of these query pameters in the ``pd.read_sql()`` method prevents SQL injection, and **must be used when implementing a metric**.

Now that we've looked at each piece of the template, let's look at it put together:

    .. code-block:: python
        :linenos:

        @annotate(tag=<metric_tag>)
        def <metric_name>(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
            """
            <brief description of the metric>

            :param repo_group_id: The repository's repo_group_id
            :param repo_id: The repository's repo_id, defaults to None
            :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
            :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
            :param end_date: Specifies the end date, defaults to datetime.now()
            :return: DataFrame of new issues/period
            """

            if not begin_date:
                begin_date = '1970-1-1 00:00:00'

            if not end_date:
                end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            <metric_name_SQL> = ''

            if not repo_id:
                <metric_name_SQL> = s.sql.text("""
                    <repo_group form of the query>
                """)

                results = pd.read_sql(<metric_name_SQL>, self.database, params={'repo_group_id': repo_group_id, 'period': period,'begin_date': begin_date, 'end_date': end_date})

                # if necessary, do some more transformations or calculations on the result

                return results

            else:
                <metric_name_SQL> = s.sql.text("""
                    <repo form of the SQL query>
                """)

                results = pd.read_sql(<metric_name_SQL>, self.database, params={'repo_id': repo_id, 'period': period, 'begin_date': begin_date, 'end_date': end_date})

                # if necessary, do some more transformations or calculations on the result

                return results

And now, with our sample ``issues_new`` metric.

  .. code-block:: python
    :linenos:

    @annotate(tag='issues-new')
    def issues_new(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """Returns a timeseries of new issues opened.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of new issues/period
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:00'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    issues_new_SQL = ''

    if not repo_id:
        issues_new_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo_name,
                date_trunc(:period, issues.created_at::DATE) as date,
                COUNT(issue_id) as issues
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND issues.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            AND issues.pull_request IS NULL
            GROUP BY issues.repo_id, date, repo_name
            ORDER BY issues.repo_id, date
        """)

        results = pd.read_sql(issues_new_SQL, self.database, params={'repo_group_id': repo_group_id, 'period': period, 'begin_date': begin_date, 'end_date': end_date})

        return results

    else:
        issues_new_SQL = s.sql.text("""
            SELECT
                repo_name,
                date_trunc(:period, issues.created_at::DATE) as date,
                COUNT(issue_id) as issues
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id = :repo_id
            AND issues.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            AND issues.pull_request IS NULL
            GROUP BY date, repo_name
            ORDER BY date;
        """)

        results = pd.read_sql(issues_new_SQL, self.database, params={'repo_id': repo_id, 'period': period, 'begin_date': begin_date, 'end_date': end_date})
        return results


Other functions
-----------------
Not all metrics must be a ``repo``/``repo_group`` metric. If your metric doesn't return a timeseries or requires additional parameters, the process of creating a metric function is in essence the same, but might have a few key differences. For example, you might require a GitHub login for a contributor-specific metric, or you might define a metric that is only applicable to ``repo`` and not to ``repo_groups``. Regardless of the differences, all metrics **must**:

1. Return a DataFrame
2. Be decorated with ``@annotate``
3. Have a complete docstring
4. Have a unique function name

Other than those 4 requirements, the rest is up to you!

Now that we've implemented our metric function, it's time to move on to creating the endpoint.
