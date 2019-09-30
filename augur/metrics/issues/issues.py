import datetime
import sqlalchemy as s
import pandas as pd
from augur.util import annotate

def create_issue_metrics(metrics):

    database = metrics.db

    @annotate(tag='issues-first-time-opened')
    def issues_first_time_opened(repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
        """
        Returns a timeseries of the count of persons opening an issue for the first time.

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

        if repo_id:
            issueNewContributor = s.sql.text("""
                SELECT
                    date_trunc(:period, new_date::DATE) as issue_date,
                    COUNT(gh_user_id),
                    repo_name
                FROM (
                    SELECT
                        gh_user_id,
                        MIN(issues.created_at) AS new_date,
                        repo_name
                    FROM
                        issues JOIN repo ON issues.repo_id = repo.repo_id
                    WHERE
                        issues.repo_id = :repo_id
                        AND issues.pull_request IS NULL
                        AND issues.created_at BETWEEN :begin_date AND :end_date
                    GROUP BY gh_user_id, repo_name
                ) as abc
                GROUP BY issue_date, repo_name
                ORDER BY issue_date
            """)
            results = pd.read_sql(issueNewContributor, database, params={'repo_id': repo_id, 'period': period,
                                                                        'begin_date': begin_date, 'end_date': end_date})
        else:
            issueNewContributor = s.sql.text("""
                SELECT
                    repo.repo_id,
                    repo_name,
                    date_trunc(:period, new_date::DATE) as issue_date,
                    COUNT(gh_user_id)
                FROM (
                    SELECT
                        repo_id,
                        gh_user_id,
                        MIN(created_at) AS new_date
                    FROM
                        issues
                    WHERE
                        issues.pull_request IS NULL 
                        AND repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                        AND created_at BETWEEN :begin_date AND :end_date
                    GROUP BY gh_user_id, repo_id
                ) as abc, repo
                WHERE repo.repo_id= abc.repo_id
                GROUP BY repo.repo_id, issue_date
                ORDER BY issue_date
            """)
            results = pd.read_sql(issueNewContributor, database,
                                  params={'repo_group_id': repo_group_id, 'period': period,
                                          'begin_date': begin_date, 'end_date': end_date})
        return results

    metrics.issues_first_time_opened = issues_first_time_opened
