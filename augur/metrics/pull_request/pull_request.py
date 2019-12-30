"""
Metrics that provide data about pull requests & their associated activity
"""

import datetime
import sqlalchemy as s
import pandas as pd
from augur.util import annotate, add_metrics

@annotate(tag='pull-requests-merge-contributor-new')
def pull_requests_merge_contributor_new(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """
    Returns a timeseries of the count of persons contributing with an accepted commit for the first time.

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
        commitNewContributor = s.sql.text("""
            SELECT date_trunc(:period, new_date::DATE) as commit_date,
            COUNT(cmt_author_email), repo_name
            FROM ( SELECT repo_name, cmt_author_email, MIN(TO_TIMESTAMP(cmt_author_date,'YYYY-MM-DD')) AS new_date
            FROM commits JOIN repo ON commits.repo_id = repo.repo_id
            WHERE commits.repo_id = :repo_id
            AND TO_TIMESTAMP(cmt_author_date,'YYYY-MM-DD') BETWEEN :begin_date AND :end_date AND cmt_author_email IS NOT NULL
            GROUP BY cmt_author_email, repo_name
            ) as abc GROUP BY commit_date, repo_name
        """)
        results = pd.read_sql(commitNewContributor, self.database, params={'repo_id': repo_id, 'period': period,
                                                                     'begin_date': begin_date,
                                                                     'end_date': end_date})
    else:
        commitNewContributor = s.sql.text("""
            SELECT abc.repo_id, repo_name ,date_trunc(:period, new_date::DATE) as commit_date,
                COUNT(cmt_author_email)
            FROM (SELECT cmt_author_email, MIN(TO_TIMESTAMP(cmt_author_date, 'YYYY-MM-DD')) AS new_date, repo_id
                FROM commits
                WHERE repo_id in (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
                    AND TO_TIMESTAMP(cmt_author_date, 'YYYY-MM-DD') BETWEEN :begin_date AND :end_date
                    AND cmt_author_email IS NOT NULL
                GROUP BY cmt_author_email, repo_id
                ) as abc, repo
            WHERE abc.repo_id = repo.repo_id
            GROUP BY abc.repo_id, repo_name, commit_date
        """)
        results = pd.read_sql(commitNewContributor, self.database,
                              params={'repo_group_id': repo_group_id, 'period': period,
                                      'begin_date': begin_date,
                                      'end_date': end_date})
    return results

@annotate(tag='reviews')
def reviews(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """ Returns a timeseris of new reviews or pull requests opened

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of new reviews/period
    """
    if not begin_date:
        begin_date = '1970-1-1'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    if not repo_id:
        reviews_SQL = s.sql.text("""
            SELECT
                pull_requests.repo_id,
                repo_name,
                DATE_TRUNC(:period, pull_requests.pr_created_at) AS date,
                COUNT(pr_src_id) AS pull_requests
            FROM pull_requests JOIN repo ON pull_requests.repo_id = repo.repo_id
            WHERE pull_requests.repo_id IN
                (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND pull_requests.pr_created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD')
                AND to_timestamp(:end_date, 'YYYY-MM-DD')
            GROUP BY pull_requests.repo_id, repo_name, date
            ORDER BY pull_requests.repo_id, date
        """)

        results = pd.read_sql(reviews_SQL, self.database,
                              params={'period': period, 'repo_group_id': repo_group_id,
                                      'begin_date': begin_date, 'end_date': end_date })
        return results

    else:
        reviews_SQL = s.sql.text("""
            SELECT
                repo_name,
                DATE_TRUNC(:period, pull_requests.pr_created_at) AS date,
                COUNT(pr_src_id) AS pull_requests
            FROM pull_requests JOIN repo ON pull_requests.repo_id = repo.repo_id
            WHERE pull_requests.repo_id = :repo_id
            AND pull_requests.pr_created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS')
                AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY date, repo_name
            ORDER BY date
        """)

        results = pd.read_sql(reviews_SQL, self.database,
                              params={'period': period, 'repo_id': repo_id,
                                      'begin_date': begin_date, 'end_date': end_date})
        return results

@annotate(tag='reviews-accepted')
def reviews_accepted(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """Returns a timeseries of number of reviews or pull requests accepted.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of accepted reviews/period
    """
    if not begin_date:
        begin_date = '1970-1-1'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    if not repo_id:
        reviews_accepted_SQL = s.sql.text("""
            SELECT
                pull_requests.repo_id,
                repo.repo_name,
                DATE_TRUNC(:period, pull_requests.pr_merged_at) AS date,
                COUNT(pr_src_id) AS pull_requests
            FROM pull_requests JOIN repo ON pull_requests.repo_id = repo.repo_id
            WHERE pull_requests.repo_id IN
                (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND pr_merged_at IS NOT NULL
            AND pr_merged_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD')
                AND to_timestamp(:end_date, 'YYYY-MM-DD')
            GROUP BY pull_requests.repo_id, repo_name, date
            ORDER BY pull_requests.repo_id, date
        """)

        results = pd.read_sql(reviews_accepted_SQL, self.database,
                              params={'period': period, 'repo_group_id': repo_group_id,
                                      'begin_date': begin_date, 'end_date': end_date})
        return results
    else:
        reviews_accepted_SQL = s.sql.text("""
            SELECT
                repo.repo_name,
                DATE_TRUNC(:period, pull_requests.pr_merged_at) AS date,
                COUNT(pr_src_id) AS pull_requests
            FROM pull_requests JOIN repo ON pull_requests.repo_id = repo.repo_id
            WHERE pull_requests.repo_id = :repo_id
            AND pr_merged_at IS NOT NULL
            AND pr_merged_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD')
                AND to_timestamp(:end_date, 'YYYY-MM-DD')
            GROUP BY date, repo.repo_name
            ORDER BY date
        """)

        results = pd.read_sql(reviews_accepted_SQL, self.database,
                              params={'period': period, 'repo_id': repo_id,
                                      'begin_date': begin_date, 'end_date': end_date})
        return results

@annotate(tag='reviews-declined')
def reviews_declined(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """ Returns a time series of reivews declined

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of declined reviews/period
    """
    if not begin_date:
        begin_date = '1970-1-1'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    if not repo_id:
        reviews_declined_SQL = s.sql.text("""
            SELECT
                pull_requests.repo_id,
                repo.repo_name,
                DATE_TRUNC(:period, pull_requests.pr_closed_at) AS date,
                COUNT(pr_src_id) AS pull_requests
            FROM pull_requests JOIN repo ON pull_requests.repo_id = repo.repo_id
            WHERE pull_requests.repo_id IN
                (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND pr_src_state = 'closed' AND pr_merged_at IS NULL
            AND pr_closed_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD')
                AND to_timestamp(:end_date, 'YYYY-MM-DD')
            GROUP BY pull_requests.repo_id, repo_name, date
            ORDER BY pull_requests.repo_id, date
        """)

        results = pd.read_sql(reviews_declined_SQL, self.database,
                              params={'period': period, 'repo_group_id': repo_group_id,
                                      'begin_date': begin_date, 'end_date': end_date })
        return results
    else:
        reviews_declined_SQL = s.sql.text("""
            SELECT
                repo.repo_name,
                DATE_TRUNC(:period, pull_requests.pr_closed_at) AS date,
                COUNT(pr_src_id) AS pull_requests
            FROM pull_requests JOIN repo ON pull_requests.repo_id = repo.repo_id
            WHERE pull_requests.repo_id = :repo_id
            AND pr_src_state = 'closed' AND pr_merged_at IS NULL
            AND pr_closed_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD')
                AND to_timestamp(:end_date, 'YYYY-MM-DD')
            GROUP BY date, repo.repo_name
            ORDER BY date
        """)

        results = pd.read_sql(reviews_declined_SQL, self.database,
                              params={'period': period, 'repo_id': repo_id,
                                      'begin_date': begin_date, 'end_date': end_date})
        return results

@annotate(tag='review-duration')
def review_duration(self, repo_group_id, repo_id=None, begin_date=None, end_date=None):
    """ Returns the duration of each accepted review.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of pull request id with the corresponding duration
    """
    if not begin_date:
        begin_date = '1970-1-1'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    if not repo_id:
        review_duration_SQL = s.sql.text("""
            SELECT
                pull_requests.repo_id,
                repo.repo_name,
                pull_requests.pull_request_id,
                pull_requests.pr_created_at AS created_at,
                pull_requests.pr_merged_at AS merged_at,
                (pr_merged_at - pr_created_at) AS duration
            FROM pull_requests JOIN repo ON pull_requests.repo_id = repo.repo_id
            WHERE pull_requests.repo_id IN
                (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND pr_merged_at IS NOT NULL
            AND pr_created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD')
                AND to_timestamp(:end_date, 'YYYY-MM-DD')
            ORDER BY pull_requests.repo_id, pull_requests.pull_request_id
        """)

        results = pd.read_sql(review_duration_SQL, self.database,
                              params={'repo_group_id': repo_group_id,
                                      'begin_date': begin_date,
                                      'end_date': end_date})
        results['duration'] = results['duration'].astype(str)
        return results
    else:
        review_duration_SQL = s.sql.text("""
            SELECT
                repo_name,
                pull_request_id,
                pr_created_at AS created_at,
                pr_merged_at AS merged_at,
                (pr_merged_at - pr_created_at) AS duration
            FROM pull_requests JOIN repo ON pull_requests.repo_id = repo.repo_id
            WHERE pull_requests.repo_id = :repo_id
            AND pr_merged_at IS NOT NULL
            AND pr_created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD')
                AND to_timestamp(:end_date, 'YYYY-MM-DD')
            ORDER BY pull_requests.repo_id, pull_request_id
        """)

        results = pd.read_sql(review_duration_SQL, self.database,
                              params={'repo_id': repo_id,
                                      'begin_date': begin_date,
                                      'end_date': end_date})
        results['duration'] = results['duration'].astype(str)
        return results

@annotate(tag='pull-request-acceptance-rate')
def pull_request_acceptance_rate(self, repo_group_id, repo_id=None, begin_date=None, end_date=None, group_by='week'):
    """
    Timeseries of pull request acceptance rate (expressed as the ratio of pull requests merged on a date to the count of pull requests opened on a date)

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: DataFrame with ratio/day
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not repo_id:
        prAccRateSQL = s.sql.text("""
            SELECT DATE(date_created) AS "date", CAST(num_approved AS DECIMAL)/CAST(num_open AS DECIMAL) AS "rate"
            FROM
                (
                    SELECT count(issue_events.issue_id) AS num_approved,
                        date_trunc(:group_by,issue_events.created_at) AS accepted_on
                    FROM issue_events JOIN issues ON issues.issue_id = issue_events.issue_id
                        JOIN repo ON issues.repo_id = repo.repo_id
                    WHERE action = 'merged'
                    AND issues.pull_request IS NOT NULL 
                    AND repo_group_id = :repo_group_id
                    AND issue_events.created_at BETWEEN :begin_date AND :end_date
                    GROUP BY accepted_on
                    ORDER BY accepted_on
                ) accepted
            JOIN
                (
                    SELECT count(issue_events.issue_id) AS num_open,
                        date_trunc(:group_by,issue_events.created_at) AS date_created
                    FROM issue_events JOIN issues ON issues.issue_id = issue_events.issue_id
                        JOIN repo ON issues.repo_id = repo.repo_id
                    WHERE action = 'ready_for_review'
                    AND issues.pull_request IS NOT NULL 
                    AND repo_group_id = :repo_group_id
                    AND issue_events.created_at BETWEEN :begin_date AND :end_date
                    GROUP BY date_created
                    ORDER BY date_created
                ) opened
            ON opened.date_created = accepted.accepted_on
        """)
        results = pd.read_sql(prAccRateSQL, self.database, params={'repo_group_id': repo_group_id, 'group_by': group_by,
                                                        'begin_date': begin_date, 'end_date': end_date})
        return results
    else:
        prAccRateSQL = s.sql.text("""
            SELECT DATE(date_created) AS "date", CAST(num_approved AS DECIMAL)/CAST(num_open AS DECIMAL) AS "rate"
            FROM
                (
                    SELECT count(issue_events.issue_id) AS num_approved,
                        date_trunc(:group_by,issue_events.created_at) AS accepted_on
                    FROM issue_events JOIN issues ON issues.issue_id = issue_events.issue_id
                    WHERE action = 'merged'
                    AND issues.pull_request IS NOT NULL
                    AND repo_id = :repo_id
                    AND issue_events.created_at BETWEEN :begin_date AND :end_date
                    GROUP BY accepted_on
                    ORDER BY accepted_on
                ) accepted
            JOIN
                (
                    SELECT count(issue_events.issue_id) AS num_open,
                        date_trunc(:group_by,issue_events.created_at) AS date_created
                    FROM issue_events JOIN issues ON issues.issue_id = issue_events.issue_id
                    WHERE action = 'ready_for_review'
                    AND issues.pull_request IS NOT NULL 
                    AND repo_id = :repo_id
                    AND issue_events.created_at BETWEEN :begin_date AND :end_date
                    GROUP BY date_created
                    ORDER BY date_created
                ) opened
            ON opened.date_created = accepted.accepted_on
        """)
        results = pd.read_sql(prAccRateSQL, self.database, params={'repo_id': repo_id, 'group_by': group_by,
                                                        'begin_date': begin_date, 'end_date': end_date})
        return results

def create_pull_request_metrics(metrics):
    add_metrics(metrics, __name__)
