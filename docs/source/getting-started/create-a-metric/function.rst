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

For this guide, we will be using the following PosgreSQL queries\:

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
    ``:period``, ``:repo_group_id``, ``:begin_date``, ``:end_date``, and ``:repo_id`` are all query parameters When you're testing, you'll need to use actual values, like ``20`` for the ``:repo_id``. We'll cover more on query parameters in the section below.

Once you've written your SQL query, it's time to wrap it in a metric function. 

Writing the function
---------------------

``repo``/``repo_group`` Metric Functions
-------------------------------------------

Any new metric you want to implement must be implemented as a function in ``augur/metrics/<model>/<model>.py``, where ``model`` is the name of the conceptual data model for which the metric provides data. 

.. seealso:: 
    For all model definitions please refer to the :py:mod:`augur.metrics` module in the `Python library documentation`__.

__ ../../library-documentation/python.html#metric-modules

Let's first break down the basic structure of one of these typical ``repo``/``repo_group`` metric functions. Note the in-line elaboration comments.

    .. code-block:: python
        :linenos:

        # we must call @annotate on the function to tell Augur this is a metric
        @annotate(tag=<metric_tag>)
        def <metric_name>(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
        """
        <brief description of the metric>

        # this part will be the same for all repo/repo_group metrics
        :param repo_group_id: The repository's repo_group_id
        :param repo_id: The repository's repo_id, defaults to None
        :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
        :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
        :param end_date: Specifies the end date, defaults to datetime.now()
        :return: DataFrame of new issues/period
        """

        # if the begin_date doesn't exist, 
        # then set it to the UNIX epoch to 
        # retrieve all data from then until
        # the end_date
        if not begin_date:
            begin_date = '1970-1-1 00:00:00'

        # if the end_date doesn't exist, 
        # then set it to the current time to 
        # retrieve all data from the end_date until 
        # the time the query is run
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        <metric_name_SQL> = ''

        # if we are not passed in a repo_id, then we must be calculating
        # the repo_group form of the metric
        if not repo_id:
            issues_new_SQL = s.sql.text("""
                <repo_group form of the query>
            """)

            # execute the query with the given query parameters
            results = pd.read_sql(issues_new_SQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,'begin_date': begin_date, 'end_date': end_date})

            # if necessary, do some more transformations or calculations on the result

            return results

        # otherwise (meaning we did recieve a repo_id), then we must be calculating
        the repo form of the metric
        else:
            <metric_name_SQL> = s.sql.text("""
                <repo form of the SQL query>
            """)

            # execute the query with the given query parameters
            results = pd.read_sql(issues_new_SQL, self.database, params={'repo_id': repo_id, 'period': period, 'begin_date': begin_date, 'end_date': end_date})

            # if necessary, do some more transformations or calculations on the result

            return results

.. note:: 
    Query parameters (lines 40 & 54) are used to dynamically insert values (like the given ``repo_id``) into a SQL statement. The use of these query pameters in the ``pd.read_sql()`` method prevents SQL injection, and **must be used when implementing a metric**.

.. note:: 
    All metric functions **must** return a DataFrame.

Now that we've looked at the template, let's look at a specific example of the ``issues_new`` metric\:

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

Now that we've implemented our metric function, it's time to move on to creating the endpoint.
