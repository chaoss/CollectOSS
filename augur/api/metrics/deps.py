#SPDX-License-Identifier: MIT
"""
Metrics that provide data about software dependencies. 
"""

import sqlalchemy as s
import pandas as pd
import datetime
from flask import current_app

from augur.api.util import register_metric


@register_metric()
def deps(repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """
    Returns a list of all the dependencies in a project/repo/repo_group.

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

        depsSQL = s.sql.text("""
            SELECT
            augur_data.repo_dependencies.*,
            augur_data.repo_groups.repo_group_id 
            FROM
            augur_data.repo_dependencies,
            augur_data.repo_groups,
            augur_data.repo,
            ( SELECT MAX ( date_trunc( 'day', augur_data.repo_dependencies.data_collection_date ) ) AS data_collection_date FROM repo_dependencies WHERE repo_id = repo_id ) C 
            WHERE
            repo_dependencies.repo_id = repo.repo_id 
            AND repo.repo_group_id = repo_groups.repo_group_id 
            AND date_trunc( 'day', repo_dependencies.data_collection_date ) = C.data_collection_date 
            AND repo_dependencies.repo_id = :repo_id
            """)

        with current_app.engine.connect() as conn:
            results = pd.read_sql(depsSQL, conn, params={'repo_id': repo_id})    	

    else:

        depsSQL = s.sql.text("""
            SELECT
            augur_data.repo_dependencies.*,
            augur_data.repo_groups.repo_group_id 
            FROM
            augur_data.repo_dependencies,
            augur_data.repo_groups,
            augur_data.repo,
            ( SELECT MAX ( date_trunc( 'day', augur_data.repo_dependencies.data_collection_date ) ) AS data_collection_date 
            FROM repo_dependencies, repo, repo_groups 
            WHERE repo.repo_group_id = repo_groups.repo_group_id and 
            repo_dependencies.repo_id = repo.repo_id and
            repo_groups.repo_group_id = :repo_group_id ) C 
            WHERE
            repo_dependencies.repo_id = repo.repo_id 
            AND repo.repo_group_id = repo_groups.repo_group_id 
            AND date_trunc( 'day', repo_dependencies.data_collection_date ) = C.data_collection_date 
            AND repo.repo_group_id = :repo_group_id
            """)

        with current_app.engine.connect() as conn:
            results = pd.read_sql(depsSQL, conn, params={'repo_group_id': repo_group_id})
    return results


@register_metric()
def libyear(repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """
    Returns a list of all the dependencies in a project/repo/repo_group.

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

        libyearSQL = s.sql.text("""
            SELECT
                rg_name,
                repo_group_id,
                repo_name,
                d.repo_id,
                repo_git,
                forked_from,
                repo_archived,
                c.name, 
                c.libyear,
                MAX ( C.data_collection_date ) AS most_recent_collection
            FROM
                (
                SELECT A.rg_name AS rg_name,
                    A.repo_group_id AS repo_group_id,
                    b.repo_name AS repo_name,
                    b.repo_id AS repo_id,
                    b.repo_git AS repo_git,
                    b.forked_from AS forked_from,
                    b.repo_archived AS repo_archived 
                FROM
                    repo_groups A,
                    repo b 
                WHERE
                    A.repo_group_id = b.repo_group_id 
                ORDER BY
                    rg_name,
                    repo_name 
                ) d,
                (
                SELECT DISTINCT
                    f.repo_id,
                    f.NAME,
                    f.libyear, 
                    f.data_collection_date
                FROM
                    ( SELECT repo_id, NAME, MAX ( data_collection_date ) AS data_collection_date FROM augur_data.repo_deps_libyear WHERE repo_id = :repo_id GROUP BY repo_id, NAME ORDER BY NAME ) e,
                    augur_data.repo_deps_libyear f 
                WHERE
                    e.data_collection_date = f.data_collection_date and 
                    e.repo_id = f.repo_id 
                ORDER BY
                NAME 
                ) C 
            WHERE
                d.repo_id = C.repo_id 
                AND C.repo_id = :repo_id
            GROUP BY
                rg_name,
                repo_git,
                repo_group_id,
                repo_name,
                d.repo_id,
                forked_from,
                repo_archived, 
                c.name, 
                c.libyear
            ORDER BY
                repo_id;
            """)

        with current_app.engine.connect() as conn:
            results = pd.read_sql(libyearSQL, conn, params={'repo_id': repo_id})    	

    else:

        libyearSQL = s.sql.text("""
            Select w.* from 
            (
            SELECT
                rg_name,
                repo_group_id,
                repo_name,
                d.repo_id,
                repo_git,
                forked_from,
                repo_archived,
                c.name, 
                c.libyear,
                MAX ( C.data_collection_date ) AS most_recent_collection
            FROM
                (
                SELECT A.rg_name AS rg_name,
                    A.repo_group_id AS repo_group_id,
                    b.repo_name AS repo_name,
                    b.repo_id AS repo_id,
                    b.repo_git AS repo_git,
                    b.forked_from AS forked_from,
                    b.repo_archived AS repo_archived 
                FROM
                    repo_groups A,
                    repo b 
                WHERE
                    A.repo_group_id = b.repo_group_id 
                ORDER BY
                    rg_name,
                    repo_name 
                ) d,
                (
                SELECT DISTINCT
                    f.repo_id,
                    f.NAME,
                    f.libyear, 
                    f.data_collection_date
                FROM
                    ( SELECT repo_id, NAME, MAX ( data_collection_date ) AS data_collection_date FROM augur_data.repo_deps_libyear GROUP BY repo_id, NAME ORDER BY NAME ) e,
                    augur_data.repo_deps_libyear f 
                WHERE
                    e.data_collection_date = f.data_collection_date and 
                    e.repo_id = f.repo_id 
                ORDER BY
                NAME 
                ) C 
            WHERE
                d.repo_id = C.repo_id 
            GROUP BY
                rg_name,
                repo_git,
                repo_group_id,
                repo_name,
                d.repo_id,
                forked_from,
                repo_archived, 
                c.name, 
                c.libyear
            ORDER BY
                repo_id) w, 
                repo_groups y, 
                repo z 
            where w.repo_id=z.repo_id and 
            y.repo_group_id=z.repo_group_id
            and z.repo_group_id = :repo_group_id
            """)

        with current_app.engine.connect() as conn:
            results = pd.read_sql(libyearSQL, conn, params={'repo_group_id': repo_group_id})
    return results

