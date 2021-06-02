#SPDX-License-Identifier: MIT
"""
General repo metrics like provides general overview data about repositories, including things like lines of code change, licenses, stars, CII best practices badging, and more
"""

import datetime
import sqlalchemy as s
import pandas as pd
import math
import logging

from augur.util import register_metric

logger = logging.getLogger("augur")

@register_metric()
def code_changes(self, repo_group_id, repo_id=None, period='week', begin_date=None, end_date=None):
    """
    Returns a timeseries of the count of commits.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of commits/period
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:00'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    code_changes_SQL = ''

    if not repo_id:
        code_changes_SQL = s.sql.text("""
            SELECT
                repo_name,
                week,
                YEAR,
                SUM(patches) AS commit_count
            FROM dm_repo_weekly JOIN repo ON dm_repo_weekly.repo_id = repo.repo_id
            WHERE dm_repo_weekly.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            GROUP BY repo_name, week, YEAR
            ORDER BY week
        """)

        results = pd.read_sql(code_changes_SQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                                 'begin_date': begin_date, 'end_date': end_date})
        results['week'] = results['week'].apply(lambda x: x - 1)
        results['date'] = results['year'].astype(str) + ' ' + results['week'].astype(str) + ' 0'
        results['date'] = results['date'].apply(lambda x: datetime.datetime.strptime(x, "%Y %W %w"))
        results = results[(results['date'] >= begin_date) & (results['date'] <= end_date)]
        return results

    else:
        code_changes_SQL = s.sql.text("""
            SELECT
                repo_name,
                week,
                YEAR,
                SUM(patches) AS commit_count
            FROM dm_repo_weekly JOIN repo ON dm_repo_weekly.repo_id = repo.repo_id
            WHERE dm_repo_weekly.repo_id = :repo_id
            GROUP BY repo_name, week, YEAR
            ORDER BY week
        """)

        results = pd.read_sql(code_changes_SQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                                 'begin_date': begin_date, 'end_date': end_date})

        results['week'] = results['week'].apply(lambda x: x - 1)
        results['date'] = results['year'].astype(str) + ' ' + results['week'].astype(str) + ' 0'
        results['date'] = results['date'].apply(lambda x: datetime.datetime.strptime(x, "%Y %W %w"))
        results = results[(results['date'] >= begin_date) & (results['date'] <= end_date)]
        return results

@register_metric()
def code_changes_lines(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """Returns a timeseries of code changes added and removed.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of code changes added and removed/period
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:00'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    code_changes_lines_SQL = ''

    if not repo_id:
        code_changes_lines_SQL = s.sql.text("""
            SELECT
                commits.repo_id,
                repo_name,
                date_trunc(:period, cmt_author_date::DATE) as date,
                SUM(cmt_added) as added,
                SUM(cmt_removed) as removed
            FROM commits JOIN repo ON commits.repo_id = repo.repo_id
            WHERE commits.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND cmt_author_date BETWEEN :begin_date AND :end_date
            GROUP BY commits.repo_id, date, repo_name
            ORDER BY commits.repo_id, date
        """)

        results = pd.read_sql(code_changes_lines_SQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                                       'begin_date': begin_date, 'end_date': end_date})

        return results

    else:
        code_changes_lines_SQL = s.sql.text("""
            SELECT
                repo_name,
                date_trunc(:period, cmt_author_date::DATE) as date,
                SUM(cmt_added) AS added,
                SUM(cmt_removed) as removed
            FROM commits JOIN repo ON commits.repo_id = repo.repo_id
            WHERE commits.repo_id = :repo_id
            AND cmt_author_date BETWEEN :begin_date AND :end_date
            GROUP BY date, repo_name
            ORDER BY date;
        """)

        results = pd.read_sql(code_changes_lines_SQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                                       'begin_date': begin_date, 'end_date': end_date})
        return results



@register_metric()
def sub_projects(self, repo_group_id, repo_id=None, begin_date=None, end_date=None):
    """
    Returns number of sub-projects
    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if repo_id:
        sub_projectsSQL = s.sql.text("""
            SELECT COUNT(*)  AS sub_project_count
            FROM repo
            WHERE repo_group_id = (
            SELECT repo_group_id
            FROM repo
            WHERE  repo_id = :repo_id)
            AND repo_added BETWEEN :begin_date AND :end_date
        """)

        results = pd.read_sql(sub_projectsSQL, self.database, params={'repo_id': repo_id,
                                                                'begin_date': begin_date, 'end_date': end_date})
    else:
        sub_projectsSQL = s.sql.text("""
            SELECT COUNT(*) AS sub_project_count
            FROM repo
            WHERE repo_group_id = :repo_group_id
            AND repo_added BETWEEN :begin_date AND :end_date
        """)

        results = pd.read_sql(sub_projectsSQL, self.database, params={'repo_group_id': repo_group_id,
                                                                'begin_date': begin_date, 'end_date': end_date})
    return results



@register_metric()
def sbom_download(self, repo_group_id, repo_id=None):
    """REQUIRES SBOMS TO BE PRESENT IN THE DATABASE

    :param repo_id: The repository's repo_id, defaults to None
    :return: dosocs sbom
    """
    dosocs_SQL = s.sql.text("""
        select * from augur_data.repo_sbom_scans
        where repo_id = :repo_id;
    """)

    logger.debug(dosocs_SQL)
    params = {'repo_id': repo_id}

    return pd.read_sql(dosocs_SQL, self.database, params=params)
    #return [json.dumps(license_information)]

@register_metric()
def cii_best_practices_badge(self, repo_group_id, repo_id=None):
    """Returns the CII best practices badge level

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: CII best parctices badge level
    """
    cii_best_practices_badge_SQL = s.sql.text("""
        SELECT data
        FROM augur_data.repo_badging
        WHERE repo_id = :repo_id
        ORDER BY created_at DESC
        LIMIT 1
    """)

    raw_df = pd.read_sql(cii_best_practices_badge_SQL, self.database, params={'repo_id': repo_id})

    badging_data = raw_df.iloc[0,0][0]

    result = {
        "repo_name": badging_data['name'],
    }

    for item in badging_data.items():
        if item[0] in ["badge_level", "achieve_passing_status", "achieve_silver_status", "tiered_percentage", "repo_url", "id"]:
            result[item[0]] = item[1]

    return pd.DataFrame(result, index=[0])

@register_metric()
def forks(self, repo_group_id, repo_id=None):
    """
    Returns a time series of the fork count

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: Time series of fork count
    """
    if not repo_id:
        forks_SQL = s.sql.text("""
            SELECT
                repo_info.repo_id,
                repo_name,
                repo_info.data_collection_date as date,
                fork_count AS forks
            FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
            WHERE repo_info.repo_id IN
                (SELECT repo_id FROM repo
                 WHERE  repo_group_id = :repo_group_id)
            ORDER BY repo_info.repo_id, date
        """)

        results = pd.read_sql(forks_SQL, self.database, params={'repo_group_id': repo_group_id})
        return results

    else:
        forks_SQL = s.sql.text("""
            SELECT
                repo_name,
                repo_info.data_collection_date as date,
                fork_count AS forks
            FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
            WHERE repo_info.repo_id = :repo_id
            ORDER BY date
        """)

        results = pd.read_sql(forks_SQL, self.database, params={'repo_id': repo_id})
        return results

@register_metric()
def fork_count(self, repo_group_id, repo_id=None):
    """
    Returns the latest fork count

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: Fork count
    """
    if not repo_id:
        fork_count_SQL = s.sql.text("""
            SELECT a.repo_id, repo_name, a.fork_count AS forks
            FROM repo_info a LEFT JOIN repo_info b
            ON (a.repo_id = b.repo_id AND a.repo_info_id < b.repo_info_id), repo
            WHERE b.repo_info_id IS NULL
            AND a.repo_id = repo.repo_id
            AND a.repo_id IN
                (SELECT repo_id FROM repo
                 WHERE  repo_group_id = :repo_group_id)
        """)

        results = pd.read_sql(fork_count_SQL, self.database, params={'repo_group_id': repo_group_id})
        return results
    else:
        fork_count_SQL = s.sql.text("""
            SELECT repo_name, fork_count AS forks
            FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
            WHERE repo_info.repo_id = :repo_id
            ORDER BY repo_info.data_collection_date DESC
            LIMIT 1
        """)

        results = pd.read_sql(fork_count_SQL, self.database, params={'repo_id': repo_id})
        return results

@register_metric()
def languages(self, repo_group_id, repo_id=None):
    """Returns the implementation languages

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: Implementation languages
    """
    if not repo_id:
        languages_SQL = s.sql.text("""
            SELECT repo_name, repo_id, primary_language
            FROM repo
            WHERE repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
        """)

        results = pd.read_sql(languages_SQL, self.database, params={'repo_group_id': repo_group_id})
        return results

    else:
        languages_SQL = s.sql.text("""
            SELECT repo_name, primary_language
            FROM repo
            WHERE repo_id = :repo_id
        """)

        results = pd.read_sql(languages_SQL, self.database, params={'repo_id': repo_id})
        return results

@register_metric(type="license")
def license_files(self, license_id, spdx_binary, repo_group_id, repo_id=None,):
        """Returns the files related to a license

        :param repo_group_id: The repository's repo_group_id
        :param repo_id: The repository's repo_id, defaults to None
        :return: Declared License
        """
        license_data_SQL = None
        repo_id_SQL = None
        repo_name_list = None

        license_data_SQL = s.sql.text("""
        SELECT DISTINCT
            A.license_id as the_license_id,    b.short_name as short_name,    f.file_name
        FROM
            files_licenses A,    licenses b,    augur_repo_map C,    packages d,    files e,
            packages_files f
        WHERE
            A.license_id = b.license_id
            AND d.package_id = C.dosocs_pkg_id
            AND e.file_id = A.file_id
            AND e.package_id = d.package_id
            AND C.repo_id = :repo_id
            AND e.file_id = f.file_id
            AND b.is_spdx_official = :spdx_binary
            AND
                (
                b.license_id = :license_id
                OR
                b.license_id in ( 369,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482));
                """)

        results = pd.read_sql(license_data_SQL, self.spdx_db, params={'repo_id': repo_id, 'spdx_binary': spdx_binary, 'license_id': license_id})
        return results

@register_metric()
def license_declared(self, repo_group_id, repo_id=None):
    """Returns the declared license

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: Declared License
    """
    license_declared_SQL = None
    repo_id_SQL = None
    repo_name_list = None

    license_declared_SQL = s.sql.text("""
    select the_license_id as license_id, short_name, sum(count) as count from
        (SELECT A
        .license_id as the_license_id,
        b.short_name as short_name,
        COUNT ( DISTINCT f.file_name )
        FROM
        files_licenses A,
        licenses b,
        augur_repo_map C,
        packages d,
        files e,
		packages_files f
        WHERE
        A.license_id = b.license_id
        AND d.package_id = C.dosocs_pkg_id
        AND e.file_id = A.file_id
		AND e.file_id = f.file_id
        AND e.package_id = d.package_id
        AND C.repo_id = :repo_id
        AND b.is_spdx_official = 'True'
        GROUP BY
        the_license_id,
        b.short_name
        UNION
        SELECT
        500 as the_license_id,
        'No Assertion' as short_name,
        COUNT ( DISTINCT f.file_name )
        FROM
        files_licenses A,
        licenses b,
        augur_repo_map C,
        packages d,
        files e,
		packages_files f
        WHERE
        A.license_id = b.license_id
        AND d.package_id = C.dosocs_pkg_id
        AND e.file_id = A.file_id
		AND e.file_id = f.file_id
        AND e.package_id = d.package_id
        AND C.repo_id = :repo_id
        AND b.is_spdx_official = 'False'
        GROUP BY
        the_license_id,
        short_name) L
    GROUP BY
    the_license_id,
    short_name
    ORDER BY
    short_name;
    """)

    results = pd.read_sql(license_declared_SQL, self.spdx_db, params={'repo_id': repo_id})
    return results

@register_metric()
def license_coverage(self, repo_group_id, repo_id=None):
    """Returns the declared license

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: Declared License
    """
    license_declared_SQL = None

    if repo_id:
        license_declared_SQL = s.sql.text("""
            SELECT a.name, b.total as total_files, a.licensed as license_declared_files, round(a.licensed/b.total::numeric, 3) as coverage
            FROM (
            SELECT packages.name as name, count(file_license_id) as licensed
            FROM packages,
                files_licenses,
                packages_files,
                repo
            WHERE packages.name = repo.repo_name
            and repo_id = :repo_id
            and packages.package_id = packages_files.package_id
            and packages_files.file_id = files_licenses.file_id
            GROUP BY packages.name) a, (SELECT packages.name as name, count(packages_files.file_id) as total
            FROm packages, repo, packages_files
            WHERE packages.name = repo.repo_name
            and repo_id = :repo_id
            AND packages.package_id = packages_files.package_id
            GROUP BY packages.name
            )b
            WHERE a.name = b.name
            GROUP BY a.name, a.licensed, a.licensed, b.total
        """)
    else:
        license_declared_SQL = s.sql.text("""
            SELECT a.name, b.total as total_files, a.licensed as license_declared_files, round(a.licensed/b.total::numeric, 3) as coverage
            FROM (
            SELECT packages.name as name, count(file_license_id) as licensed
            FROM packages,
                files_licenses,
                packages_files,
                repo
            WHERE packages.name = repo.repo_name
            and repo_group_id = :repo_group_id
            and packages.package_id = packages_files.package_id
            and packages_files.file_id = files_licenses.file_id
            GROUP BY packages.name) a, (SELECT packages.name as name, count(packages_files.file_id) as total
            FROm packages, repo, packages_files
            WHERE packages.name = repo.repo_name
            and repo_group_id = :repo_group_id
            AND packages.package_id = packages_files.package_id
            GROUP BY packages.name
            )b
            WHERE a.name = b.name
            GROUP BY a.name, a.licensed, a.licensed, b.total
        """)

    results = pd.read_sql(license_declared_SQL, self.spdx_db, params={'repo_id': repo_id, 'repo_group_id':repo_group_id})

    return results

@register_metric()
def license_count(self, repo_group_id, repo_id=None):
    """Returns the declared license

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: Declared License
    """
    license_declared_SQL = None

    if repo_id:
        license_declared_SQL = s.sql.text("""
            SELECT a.name, a.number_of_license, b.total > a.licensed as file_without_licenses
            FROM (
            SELECT packages.name as name, count (DISTINCT (files_licenses.license_id)) as number_of_license, count(file_license_id) as licensed
            FROM packages,
                files_licenses,
                packages_files,
                repo
            WHERE packages.name = repo.repo_name
            and repo_id = :repo_id
            and packages.package_id = packages_files.package_id
            and packages_files.file_id = files_licenses.file_id
            GROUP BY packages.name) a, (SELECT packages.name as name, count(packages_files.file_id) as total
            FROm packages, repo, packages_files
            WHERE packages.name = repo.repo_name
            and repo_id = :repo_id
            AND packages.package_id = packages_files.package_id
            GROUP BY packages.name
            )b
            WHERE a.name = b.name
            GROUP BY a.name, a.number_of_license, a.licensed, b.total
        """)
    else:
        license_declared_SQL = s.sql.text("""
            SELECT a.name, a.number_of_license, b.total > a.licensed as file_without_licenses
            FROM (
            SELECT packages.name as name, count (DISTINCT (files_licenses.license_id)) as number_of_license, count(file_license_id) as licensed
            FROM packages,
                files_licenses,
                packages_files,
                repo
            WHERE packages.name = repo.repo_name
            and repo_group_id = :repo_group_id
            and packages.package_id = packages_files.package_id
            and packages_files.file_id = files_licenses.file_id
            GROUP BY packages.name) a, (SELECT packages.name as name, count(packages_files.file_id) as total
            FROm packages, repo, packages_files
            WHERE packages.name = repo.repo_name
            and repo_group_id = :repo_group_id
            AND packages.package_id = packages_files.package_id
            GROUP BY packages.name
            )b
            WHERE a.name = b.name
            GROUP BY a.name, a.number_of_license, a.licensed, b.total
        """)

    results = pd.read_sql(license_declared_SQL, self.spdx_db, params={'repo_id': repo_id, 'repo_group_id':repo_group_id})

    return results


@register_metric()
def stars(self, repo_group_id, repo_id=None):
    """
    Returns a time series of the stars count

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: Time series of stars count
    """
    if not repo_id:
        stars_SQL = s.sql.text("""
            SELECT
                repo_info.repo_id,
                repo_name,
                repo_info.data_collection_date as date,
                stars_count AS stars
            FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
            WHERE repo_info.repo_id IN
                (SELECT repo_id FROM repo
                 WHERE  repo_group_id = :repo_group_id)
            ORDER BY repo_info.repo_id, date
        """)

        results = pd.read_sql(stars_SQL, self.database, params={'repo_group_id': repo_group_id})
        return results

    else:
        stars_SQL = s.sql.text("""
            SELECT
                repo_name,
                repo_info.data_collection_date as date,
                stars_count AS stars
            FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
            WHERE repo_info.repo_id = :repo_id
            ORDER BY date
        """)

        results = pd.read_sql(stars_SQL, self.database, params={'repo_id': repo_id})
        return results

@register_metric()
def stars_count(self, repo_group_id, repo_id=None):
    """
    Returns the latest stars count

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: stars count
    """
    if not repo_id:
        stars_count_SQL = s.sql.text("""
            SELECT a.repo_id, repo_name, a.stars_count AS stars
            FROM repo_info a LEFT JOIN repo_info b
            ON (a.repo_id = b.repo_id AND a.repo_info_id < b.repo_info_id), repo
            WHERE b.repo_info_id IS NULL
            AND a.repo_id = repo.repo_id
            AND a.repo_id IN
                (SELECT repo_id FROM repo
                 WHERE  repo_group_id = :repo_group_id)
        """)

        results = pd.read_sql(stars_count_SQL, self.database, params={'repo_group_id': repo_group_id})
        return results
    else:
        stars_count_SQL = s.sql.text("""
            SELECT repo_name, stars_count AS stars
            FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
            WHERE repo_info.repo_id = :repo_id
            ORDER BY repo_info.data_collection_date DESC
            LIMIT 1
        """)

        results = pd.read_sql(stars_count_SQL, self.database, params={'repo_id': repo_id})
        return results

@register_metric()
def watchers(self, repo_group_id, repo_id=None):
    """
    Returns a time series of the watchers count

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: Time series of watchers count
    """
    if not repo_id:
        watchers_SQL = s.sql.text("""
            SELECT
                repo_info.repo_id,
                repo_name,
                repo_info.data_collection_date as date,
                watchers_count AS watchers
            FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
            WHERE repo_info.repo_id IN
                (SELECT repo_id FROM repo
                 WHERE  repo_group_id = :repo_group_id)
            ORDER BY repo_info.repo_id, date
        """)

        results = pd.read_sql(watchers_SQL, self.database, params={'repo_group_id': repo_group_id})
        return results

    else:
        watchers_SQL = s.sql.text("""
            SELECT
                repo_name,
                repo_info.data_collection_date as date,
                watchers_count AS watchers
            FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
            WHERE repo_info.repo_id = :repo_id
            ORDER BY date
        """)

        results = pd.read_sql(watchers_SQL, self.database, params={'repo_id': repo_id})
        return results

@register_metric()
def watchers_count(self, repo_group_id, repo_id=None):
    """
    Returns the latest watchers count

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: watchers count
    """
    if not repo_id:
        watchers_count_SQL = s.sql.text("""
            SELECT a.repo_id, repo_name, a.watchers_count AS watchers
            FROM repo_info a LEFT JOIN repo_info b
            ON (a.repo_id = b.repo_id AND a.repo_info_id < b.repo_info_id), repo
            WHERE b.repo_info_id IS NULL
            AND a.repo_id = repo.repo_id
            AND a.repo_id IN
                (SELECT repo_id FROM repo
                 WHERE  repo_group_id = :repo_group_id)
        """)

        results = pd.read_sql(watchers_count_SQL, self.database, params={'repo_group_id': repo_group_id})
        return results
    else:
        watchers_count_SQL = s.sql.text("""
            SELECT repo_name, watchers_count AS watchers
            FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
            WHERE repo_info.repo_id = :repo_id
            ORDER BY repo_info.data_collection_date DESC
            LIMIT 1
        """)

        results = pd.read_sql(watchers_count_SQL, self.database, params={'repo_id': repo_id})
        return results

@register_metric()
def annual_lines_of_code_count_ranked_by_new_repo_in_repo_group(self, repo_group_id, repo_id = None, calendar_year=None):
    """
    For each repository in a collection of repositories being managed, each REPO that first appears in the parameterized
calendar year (a new repo in that year), show all commits for that year (total for year by repo).
    Result ranked from highest number of commits to lowest by default.

    :param repo_url: the repository's URL
    :param calendar_year: the calendar year a repo is created in to be considered "new"
    :param repo_group: the group of repositories to analyze
    """
    if calendar_year == None:
        calendar_year = datetime.datetime.now().strftime('%Y')

    cdRgNewrepRankedCommitsSQL = None

    if not repo_id:
        cdRgNewrepRankedCommitsSQL = s.sql.text("""
            SELECT repo.repo_id, sum(cast(added as INTEGER) - cast(removed as INTEGER) - cast(whitespace as INTEGER)) as net, patches, repo_name
            FROM dm_repo_annual, repo, repo_groups
            where  repo.repo_group_id = :repo_group_id
            and dm_repo_annual.repo_id = repo.repo_id
            and date_part('year', repo.repo_added) = :calendar_year
            and repo.repo_group_id = repo_groups.repo_group_id
            group by repo.repo_id, patches, rg_name
            ORDER BY net desc
            LIMIT 10
        """)
    else:
        cdRgNewrepRankedCommitsSQL = s.sql.text("""
            SELECT repo.repo_id, sum(cast(added as INTEGER) - cast(removed as INTEGER) - cast(whitespace as INTEGER)) as net, patches, repo_name
            FROM dm_repo_annual, repo, repo_groups
            where  repo.repo_group_id = (select repo.repo_group_id from repo where repo.repo_id = :repo_id)
            and dm_repo_annual.repo_id = repo.repo_id
            and date_part('year', repo.repo_added) = :calendar_year
            and repo.repo_group_id = repo_groups.repo_group_id
            group by repo.repo_id, patches, rg_name
            ORDER BY net desc
            LIMIT 10
        """)
    results = pd.read_sql(cdRgNewrepRankedCommitsSQL, self.database, params={ "repo_group_id": repo_group_id,
    "repo_id": repo_id, "calendar_year": calendar_year})
    return results

@register_metric()
def annual_lines_of_code_count_ranked_by_repo_in_repo_group(self, repo_group_id, repo_id=None, timeframe=None):
    """
    For each repository in a collection of repositories being managed, each REPO's total commits during the current Month,
    Year or Week. Result ranked from highest number of commits to lowest by default.
    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param calendar_year: the calendar year a repo is created in to be considered "new"
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
                FROM dm_repo_annual, repo, repo_groups
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
def lines_of_code_commit_counts_by_calendar_year_grouped(self, repo_url, calendar_year=None, interval=None):
    """
    For a single repository, all the commits and lines of code occuring for the specified year, grouped by the specified interval (week or month)

    :param repo_url: the repository's URL
    :param calendar_year: the calendar year a repo is created in to be considered "new"
    :param interval: Month or week. The periodocity of which to examine data within the given calendar_year
    """

    if calendar_year == None:
        calendar_year = datetime.datetime.now().strftime('%Y')

    if interval == None:
        interval = 'month'

    cdRepTpIntervalLocCommitsSQL = None

    if interval == "month":
        cdRepTpIntervalLocCommitsSQL = s.sql.text("""
            SELECT sum(cast(IFNULL(added, 0) as signed) - cast(IFNULL(removed, 0) as signed) - cast(IFNULL(whitespace, 0) as signed)) as net_lines_minus_whitespace,
            sum(IFNULL(added, 0)) as added, sum(IFNULL(removed, 0)) as removed, sum(IFNULL(whitespace, 0)) as whitespace,
            IFNULL(patches, 0) as commits, a.month, IFNULL(year, :calendar_year) as year
            FROM (select month from repo_monthly_cache group by month) a
            LEFT JOIN (SELECT name, repo_monthly_cache.added, removed, whitespace, patches, month, IFNULL(year, :calendar_year) as year
            FROM repo_monthly_cache, repos
            WHERE repos_id = (SELECT id FROM repos WHERE git LIKE :repourl LIMIT 1)
            AND year = :calendar_year
            AND repos.id = repos_id
            GROUP BY month) b
            ON a.month = b.month
            GROUP BY month
        """)
    elif interval == "week":
        cdRepTpIntervalLocCommitsSQL = s.sql.text("""
            SELECT  sum(cast(IFNULL(added, 0) as signed) - cast(IFNULL(removed, 0) as signed) - cast(IFNULL(whitespace, 0) as signed)) as net_lines_minus_whitespace,
            sum(IFNULL(added, 0)) as added, sum(IFNULL(removed, 0)) as removed, sum(IFNULL(whitespace, 0)) as whitespace,
            IFNULL(patches, 0) as commits, a.week, IFNULL(year, :calendar_year) as year
            FROM (select week from repo_weekly_cache group by week) a
            LEFT JOIN (SELECT name, repo_weekly_cache.added, removed, whitespace, patches, week, IFNULL(year, :calendar_year) as year
            FROM repo_weekly_cache, repos
            WHERE repos_id = (SELECT id FROM repos WHERE git LIKE :repourl LIMIT 1)
            AND year = :calendar_year
            AND repos.id = repos_id
            GROUP BY week) b
            ON a.week = b.week
            GROUP BY week
        """)

    results = pd.read_sql(cdRepTpIntervalLocCommitsSQL, self.database, params={"repourl": '%{}%'.format(repo_url), 'calendar_year': calendar_year})
    return results

@register_metric()
def average_weekly_commits(self, repo_group_id=None, repo_id=None, calendar_year=None):

    if calendar_year == None:
        calendar_year = datetime.datetime.now().strftime('%Y')

    extra_and = "AND repo.repo_group_id = :repo_group_id" if repo_group_id and not repo_id else "AND repo.repo_id = :repo_id" if repo_group_id and repo_id else ""
    average_weekly_commits_sql = s.sql.text("""
        SELECT repo.repo_id, repo.repo_name, year, sum(patches)/52 AS average_weekly_commits 
        FROM dm_repo_annual, repo
        WHERE YEAR = :calendar_year -- or other year
        AND dm_repo_annual.repo_id = repo.repo_id 
        {}
        GROUP BY repo.repo_id, repo.repo_name, YEAR
        ORDER BY repo_name
    """.format(extra_and))

    results = pd.read_sql(average_weekly_commits_sql, self.database, params={"repo_group_id": repo_group_id,
        "repo_id": repo_id, "calendar_year": calendar_year})
    return results

@register_metric()
def aggregate_summary(self, repo_group_id, repo_id=None, begin_date=None, end_date=None):

    if not begin_date:
        begin_date = datetime.datetime.now()
        # Subtract 1 year and leap year check
        try:
            begin_date = begin_date.replace(year=begin_date.year-1)
        except ValueError:
            begin_date = begin_date.replace(year=begin_date.year-1, day=begin_date.day-1)
        begin_date = begin_date.strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    if not repo_id:
        summarySQL = s.sql.text("""
            SELECT
            (
                SELECT watchers_count AS watcher_count
                FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
                WHERE repo_group_id = :repo_group_id
                ORDER BY last_updated DESC
                LIMIT 1
            ) - (
                SELECT watchers_count AS watcher_count
                FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
                WHERE repo_group_id = :repo_group_id
                AND last_updated >= date_trunc('day', NOW() - INTERVAL '1 year')
                ORDER BY last_updated ASC
                LIMIT 1
            ) AS watcher_count,
            (
                SELECT stars_count AS stars_count
                FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
                WHERE repo_group_id = :repo_group_id
                ORDER BY last_updated DESC
                LIMIT 1
            ) - (
                SELECT stars_count AS stars_count
                FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
                WHERE repo_group_id = :repo_group_id
                AND last_updated >= date_trunc('day', NOW() - INTERVAL '1 year')
                ORDER BY last_updated ASC
                LIMIT 1
            ) AS stars_count,
            (
                SELECT fork_count AS fork_count
                FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
                WHERE repo_group_id = :repo_group_id
                ORDER BY last_updated DESC
                LIMIT 1
            ) - (
                SELECT fork_count AS fork_count
                FROM repo_info JOIN repo ON repo_info.repo_id = repo.repo_id
                WHERE repo_group_id = :repo_group_id
                AND last_updated >= date_trunc('day', NOW() - INTERVAL '1 year')
                ORDER BY last_updated ASC
                LIMIT 1
            ) AS fork_count,
            (
                SELECT count(*) AS merged_count
                FROM (
                    SELECT DISTINCT issue_events.issue_id
                    FROM issue_events JOIN issues ON issues.issue_id = issue_events.issue_id JOIN repo ON issues.repo_id = repo.repo_id
                    WHERE action = 'merged'
                    AND repo_group_id = :repo_group_id
                    AND issue_events.created_at BETWEEN :begin_date AND :end_date
                ) a
            ) AS merged_count,
            committer_count, commit_count FROM (
                SELECT count(cmt_author_name) AS committer_count, sum(commit_count) AS commit_count
                FROM (
                    SELECT DISTINCT cmt_author_name, COUNT(cmt_id) AS commit_count FROM commits JOIN repo ON commits.repo_id = repo.repo_id
                    WHERE repo_group_id = :repo_group_id
                    AND commits.cmt_committer_date BETWEEN :begin_date AND :end_date
                    GROUP BY cmt_author_name
                ) temp
            ) commit_data
        """)
        results = pd.read_sql(summarySQL, self.database, params={'repo_group_id': repo_group_id,
                                                        'begin_date': begin_date, 'end_date': end_date})
        return results
    else:
        summarySQL = s.sql.text("""
            SELECT
            (
                SELECT watchers_count AS watcher_count
                FROM repo_info
                WHERE repo_id = :repo_id
                ORDER BY last_updated DESC
                LIMIT 1
            ) - (
                SELECT watchers_count AS watcher_count
                FROM repo_info
                WHERE repo_id = :repo_id
                AND last_updated >= date_trunc('day', NOW() - INTERVAL '1 year')
                ORDER BY last_updated ASC
                LIMIT 1
            ) AS watcher_count,
            (
                SELECT stars_count AS stars_count
                FROM repo_info
                WHERE repo_id = :repo_id
                ORDER BY last_updated DESC
                LIMIT 1
            ) - (
                SELECT stars_count AS stars_count
                FROM repo_info
                WHERE repo_id = :repo_id
                AND last_updated >= date_trunc('day', NOW() - INTERVAL '1 year')
                ORDER BY last_updated ASC
                LIMIT 1
            ) AS stars_count,
            (
                SELECT fork_count AS fork_count
                FROM repo_info
                WHERE repo_id = :repo_id
                ORDER BY last_updated DESC
                LIMIT 1
            ) - (
                SELECT fork_count AS fork_count
                FROM repo_info
                WHERE repo_id = :repo_id
                AND last_updated >= date_trunc('day', NOW() - INTERVAL '1 year')
                ORDER BY last_updated ASC
                LIMIT 1
            ) AS fork_count,
            (
                SELECT count(*) AS merged_count
                FROM (
                    SELECT DISTINCT issue_events.issue_id
                    FROM issue_events JOIN issues ON issues.issue_id = issue_events.issue_id
                    WHERE action = 'merged'
                    AND repo_id = :repo_id
                    AND issue_events.created_at BETWEEN :begin_date AND :end_date
                ) a
            ) AS merged_count,
            committer_count, commit_count FROM (
                SELECT count(cmt_author_name) AS committer_count, sum(commit_count) AS commit_count
                FROM (
                    SELECT DISTINCT cmt_author_name, COUNT(cmt_id) AS commit_count FROM commits
                    WHERE repo_id = :repo_id
                    AND commits.cmt_committer_date BETWEEN :begin_date AND :end_date
                    GROUP BY cmt_author_name
                ) temp
            ) commit_data
        """)
        results = pd.read_sql(summarySQL, self.database, params={'repo_id': repo_id,
                                                        'begin_date': begin_date, 'end_date': end_date})
        return results