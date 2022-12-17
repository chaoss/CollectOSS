#SPDX-License-Identifier: MIT

"""
Metrics that provide data about messages (of any form) & their associated activity
"""

import datetime
import sqlalchemy as s
import pandas as pd
from augur.api.util import register_metric

from augur.application.db.engine import create_database_engine
engine = create_database_engine()


@register_metric()
def repo_messages(repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
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

    repomessagesSQL = None


    if repo_id:

        repomessagesSQL = s.sql.text("""
            SELECT
                date_trunc( :period, message.msg_timestamp :: DATE ) AS message_date,
                COUNT ( * ),
                repo_name 
            FROM
                augur_data.repo,
                augur_data.message 
            WHERE
                augur_data.repo.repo_id = augur_data.message.repo_id 
                AND
                augur_data.repo.repo_id = :repo_id 
                AND 
                message.msg_timestamp BETWEEN :begin_date AND :end_date
            GROUP BY
                message_date,
                repo_name 
            ORDER BY
                repo_name,
                message_date

        """)


        results = pd.read_sql(repomessagesSQL, engine, params={'repo_id': repo_id, 'period': period,
                                                                    'begin_date': begin_date, 'end_date': end_date})
    else: 

        repomessagesSQL = s.sql.text("""

            SELECT
                date_trunc( :period, message.msg_timestamp :: DATE ) AS message_date,
                COUNT ( * ),
                rg_name 
            FROM
                augur_data.repo,
                augur_data.repo_groups,
                augur_data.message 
            WHERE
                augur_data.repo.repo_id = augur_data.message.repo_id 
                AND augur_data.repo_groups.repo_group_id = repo.repo_group_id 
                AND
                augur_data.repo_groups.repo_group_id = :repo_group_id 
                AND 
                message.msg_timestamp BETWEEN :begin_date AND :end_date
            GROUP BY
                message_date,
                rg_name 
            ORDER BY
                rg_name,
                message_date
        """)
            
        results = pd.read_sql(repomessagesSQL, engine,
                              params={'repo_group_id': repo_group_id, 'period': period,
                                      'begin_date': begin_date, 'end_date': end_date})

    return results


