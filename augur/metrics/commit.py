#SPDX-License-Identifier: MIT
"""
Metrics that provide data about commits & their associated activity
"""

import datetime
import sqlalchemy as s
import pandas as pd
from augur.util import register_metric

@register_metric()
def committers(self, repo_group_id, repo_id=None, begin_date=None, end_date=None, period='month'):
    """
    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of persons/period
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    committersSQL = None

    if repo_id:
        committersSQL = s.sql.text(
            """
                SELECT DATE,
                    repo_name,
                    rg_name,
                    COUNT ( author_count ) 
                FROM
                    (
                    SELECT
                        date_trunc(:period, commits.cmt_author_date::date) as date,
                        repo_name,
                        rg_name,
                        cmt_author_name,
                        cmt_author_email,
                        COUNT ( cmt_author_name ) AS author_count 
                    FROM
                        commits, repo, repo_groups
                    WHERE
                        commits.repo_id = :repo_id AND commits.repo_id = repo.repo_id
                        AND repo.repo_group_id = repo_groups.repo_group_id
                        AND commits.cmt_author_date BETWEEN :begin_date and :end_date
                    GROUP BY date, repo_name, rg_name, cmt_author_name, cmt_author_email 
                    ORDER BY date DESC
                    ) C
                GROUP BY
                    C.DATE,
                    repo_name,
                    rg_name 
                ORDER BY C.DATE desc 
            """
        )
    else:
        committersSQL = s.sql.text(
            """
                SELECT DATE,
                    rg_name,
                    COUNT ( author_count ) 
                FROM
                    (
                    SELECT
                        date_trunc(:period, commits.cmt_author_date::date) as date,
                        rg_name,
                        cmt_author_name,
                        cmt_author_email,
                        COUNT ( cmt_author_name ) AS author_count 
                    FROM
                        commits, repo, repo_groups
                    WHERE
                        commits.repo_id = repo.repo_id
                        AND repo.repo_group_id = repo_groups.repo_group_id
                        AND commits.cmt_author_date BETWEEN :begin_date and :end_date
                        AND repo.repo_group_id = :repo_group_id
                    GROUP BY date, rg_name, cmt_author_name, cmt_author_email 
                    ORDER BY date DESC
                    ) C
                GROUP BY
                    C.DATE,
                    rg_name 
                ORDER BY C.DATE desc 
            """
        )

    results = pd.read_sql(committersSQL, self.database, params={'repo_id': repo_id, 
        'repo_group_id': repo_group_id,'begin_date': begin_date, 'end_date': end_date, 'period':period})

    return results

@register_metric()
def annual_commit_count_ranked_by_new_repo_in_repo_group(self, repo_group_id, repo_id=None, begin_date=None, end_date=None, period='month'):
    """
    For each repository in a collection of repositories being managed, each REPO that first appears in the parameterized
    calendar year (a new repo in that year), show all commits for that year (total for year by repo).
    Result ranked from highest number of commits to lowest by default.

    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of data
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    

    cdRgNewrepRankedCommitsSQL = None

    if not repo_id:
        table = 'dm_repo_group_annual' if period == 'year' or period == 'all' else 'dm_repo_group_monthly' if period == 'month' else 'dm_repo_group_weekly'
        cdRgNewrepRankedCommitsSQL = s.sql.text("""
            SELECT repo_groups.repo_group_id, rg_name, year, sum(cast(added AS INTEGER) - cast(removed AS INTEGER) - cast(whitespace AS INTEGER)) AS net, sum(cast(patches AS INTEGER)) AS commits
            FROM {0}, repo_groups
            WHERE {0}.repo_group_id = repo_groups.repo_group_id            
            AND repo_groups.repo_group_id = :repo_group_id
            AND (
                year > date_part('year', TIMESTAMP :begin_date)
                OR (
                    year = date_part('year', TIMESTAMP :begin_date) 
                    AND {1} >= date_part('{1}', TIMESTAMP :begin_date)
                )
            )
            AND (
                year < date_part('year', TIMESTAMP :end_date)
                OR (
                    year = date_part('year', TIMESTAMP :end_date) 
                    AND {1} <= date_part('{1}', TIMESTAMP :end_date)
                )
            )
            GROUP BY repo_groups.repo_group_id, rg_name, YEAR
            ORDER BY YEAR ASC
        """.format(table, period))
    else:
        table = 'dm_repo_annual' if period == 'year' or period == 'all' else 'dm_repo_monthly' if period == 'month' else 'dm_repo_weekly'
        cdRgNewrepRankedCommitsSQL = s.sql.text("""
            SELECT repo.repo_id, repo_name, year, sum(cast(added AS INTEGER) - cast(removed AS INTEGER) - cast(whitespace AS INTEGER)) AS net, sum(cast(patches AS INTEGER)) AS commits
            FROM {0}, repo
            WHERE {0}.repo_id = repo.repo_id            
            AND repo.repo_id = :repo_id
            AND (
                year > date_part('year', TIMESTAMP :begin_date)
                OR (
                    year = date_part('year', TIMESTAMP :begin_date) 
                    AND {1} >= date_part('{1}', TIMESTAMP :begin_date)
                )
            )
            AND (
                year < date_part('year', TIMESTAMP :end_date)
                OR (
                    year = date_part('year', TIMESTAMP :end_date) 
                    AND {1} <= date_part('{1}', TIMESTAMP :end_date)
                )
            )
            GROUP BY repo.repo_id, repo_name, YEAR
            ORDER BY YEAR ASC
        """.format(table, period))
    results = pd.read_sql(cdRgNewrepRankedCommitsSQL, self.database, params={'repo_id': repo_id, 
        'repo_group_id': repo_group_id,'begin_date': begin_date, 'end_date': end_date})
    return results

@register_metric()
def annual_commit_count_ranked_by_repo_in_repo_group(self, repo_group_id, repo_id=None, timeframe=None):
    """
    For each repository in a collection of repositories being managed, each REPO's total commits during the current Month,
    Year or Week. Result ranked from highest number of commits to lowest by default.
    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of data
    """
    if timeframe == None:
        timeframe = 'all'

    cdRgTpRankedCommitsSQL = None

    if repo_id:
        if timeframe == 'all':
            cdRgTpRankedCommitsSQL = s.sql.text("""
                SELECT repo.repo_id, repo_name as name, SUM(added - removed - whitespace) as net, patches
                FROM dm_repo_annual, repo, repo_groups
                WHERE repo.repo_group_id = (select repo.repo_group_id from repo where repo.repo_id = :repo_id)
                AND repo.repo_group_id = repo_groups.repo_group_id
                AND dm_repo_annual.repo_id = repo.repo_id
                group by repo.repo_id, patches
                order by net desc
                LIMIT 10
            """)
        elif timeframe == 'year':
            cdRgTpRankedCommitsSQL = s.sql.text("""
                SELECT repo.repo_id, repo_name as name, SUM(added - removed - whitespace) as net, patches
                FROM dm_repo_annual, repo, repo_groups
                WHERE repo.repo_group_id = (select repo.repo_group_id from repo where repo.repo_id = :repo_id)
                AND repo.repo_group_id = repo_groups.repo_group_id
                AND dm_repo_annual.repo_id = repo.repo_id
                AND date_part('year', repo_added) = date_part('year', CURRENT_DATE)
                group by repo.repo_id, patches
                order by net desc
                LIMIT 10
            """)
        elif timeframe == 'month':
            cdRgTpRankedCommitsSQL = s.sql.text("""
                SELECT repo.repo_id, repo_name as name, SUM(added - removed - whitespace) as net, patches
                FROM dm_repo_monthly, repo, repo_groups
                WHERE repo.repo_group_id = (select repo.repo_group_id from repo where repo.repo_id = :repo_id)
                AND repo.repo_group_id = repo_groups.repo_group_id
                AND dm_repo_monthly.repo_id = repo.repo_id
                AND date_part('year', repo_added) = date_part('year', CURRENT_DATE)
                AND date_part('month', repo_added) = date_part('month', CURRENT_DATE)
                group by repo.repo_id, patches
                order by net desc
                LIMIT 10
            """)
    else:
        if timeframe == 'all':
            cdRgTpRankedCommitsSQL = s.sql.text("""
                SELECT repo.repo_id, repo_name as name, SUM(added - removed - whitespace) as net, patches
                FROM augur_data.dm_repo_annual, repo, repo_groups
                WHERE repo.repo_group_id = :repo_group_id
                AND repo.repo_group_id = repo_groups.repo_group_id
                AND dm_repo_annual.repo_id = repo.repo_id
                group by repo.repo_id, patches
                order by net desc
                LIMIT 10
            """)
        elif timeframe == "year":
            cdRgTpRankedCommitsSQL = s.sql.text(
                """
                SELECT repo.repo_id, repo_name as name, SUM(added - removed - whitespace) as net, patches
                FROM dm_repo_annual, repo, repo_groups
                WHERE repo.repo_group_id = :repo_group_id
                AND repo.repo_group_id = repo_groups.repo_group_id
                AND dm_repo_annual.repo_id = repo.repo_id
                AND date_part('year', repo_added) = date_part('year', CURRENT_DATE)
                group by repo.repo_id, patches
                order by net desc
                LIMIT 10
                """
            )
        elif timeframe == 'month':
            cdRgTpRankedCommitsSQL = s.sql.text("""
                SELECT repo.repo_id, repo_name as name, SUM(added - removed - whitespace) as net, patches
                FROM dm_repo_annual, repo, repo_groups
                WHERE repo.repo_group_id = :repo_group_id
                AND repo.repo_group_id = repo_groups.repo_group_id
                AND dm_repo_annual.repo_id = repo.repo_id
                AND date_part('year', repo_added) = date_part('year', CURRENT_DATE)
                AND date_part('month', repo_added) = date_part('month', CURRENT_DATE)
                group by repo.repo_id, patches
                order by net desc
                LIMIT 10
            """)

    results = pd.read_sql(cdRgTpRankedCommitsSQL, self.database, params={ "repo_group_id": repo_group_id,
    "repo_id": repo_id})
    return results

@register_metric()
def top_committers(self, repo_group_id, repo_id=None, year=None, threshold=0.5):
    """
    Returns a list of contributors contributing N% of all commits.

    :param repo_group_id: Repo group ID
    :param repo_id: Repo ID.
    :param year: Year. eg: 2018, 2107. Defaults to current year.
    :param threshold: The threshold to specify N%. Defaults to 0.5
    """
    threshold = float(threshold)
    if threshold < 0 or threshold > 1:
        raise ValueError('threshold should be between 0 and 1')

    if year is None:
        year = datetime.datetime.now().year

    if not repo_id:
        total_commits_SQL = s.sql.text("""
            SELECT SUM(patches)::int
            FROM
                (SELECT repo_group_id, email, year, patches
                FROM dm_repo_group_annual
                WHERE year = :year AND repo_group_id = :repo_group_id
                ORDER BY patches DESC) a
        """)

        results = pd.read_sql(total_commits_SQL, self.database,
                            params={'year': year, 'repo_group_id': repo_group_id})
    else:
        total_commits_SQL = s.sql.text("""
            SELECT SUM(patches)::int
            FROM
                (SELECT repo_id, email, year, patches
                FROM dm_repo_annual
                WHERE year = :year AND repo_id = :repo_id
                ORDER BY patches DESC) a
        """)

        results = pd.read_sql(total_commits_SQL, self.database,
                            params={'year': year, 'repo_id': repo_id})

    total_commits = int(results.iloc[0]['sum'])
    threshold_commits = round(threshold * total_commits)

    if not repo_id:
        committers_SQL = s.sql.text("""
            SELECT
                a.repo_group_id,
                rg_name AS repo_group_name,
                a.email,
                SUM(a.patches)::int AS commits
            FROM
                (SELECT repo_group_id, email, year, patches
                FROM dm_repo_group_annual
                WHERE year = :year AND repo_group_id = :repo_group_id
                ORDER BY patches DESC) a, repo_groups
            WHERE a.repo_group_id = repo_groups.repo_group_id
            GROUP BY a.repo_group_id, repo_group_name, a.email
            ORDER BY commits DESC
        """)

        results = pd.read_sql(committers_SQL, self.database,
                            params={'year': year, 'repo_group_id': repo_group_id})
    else:
        committers_SQL = s.sql.text("""
            SELECT
                a.repo_id,
                repo.repo_name,
                a.email,
                SUM(a.patches)::int AS commits
            FROM
                (SELECT repo_id, email, year, patches
                FROM dm_repo_annual
                WHERE year = :year AND repo_id = :repo_id
                ORDER BY patches DESC) a, repo
            WHERE a.repo_id = repo.repo_id
            GROUP BY a.repo_id, repo.repo_name, a.email
            ORDER BY commits DESC
        """)

        results = pd.read_sql(committers_SQL, self.database,
                              params={'year': year, 'repo_id': repo_id})

    cumsum = 0
    for i, row in results.iterrows():
        cumsum += row['commits']
        if cumsum >= threshold_commits:
            results = results[:i + 1]
            break

    if not repo_id:
        rg_name = results.iloc[0]['repo_group_name']
        results.loc[i+1] = [repo_group_id, rg_name, 'other_contributors',
                            int(total_commits - cumsum)]
    else:
        repo_name = results.iloc[0]['repo_name']
        results.loc[i+1] = [repo_id, repo_name, 'other_contributors',
                            int(total_commits - cumsum)]

    return results
