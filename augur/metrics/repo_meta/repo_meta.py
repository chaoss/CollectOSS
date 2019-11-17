"""
General repo metrics like provides general overview data about repositories, including things like lines of code change, licenses, stars, CII best practices badging, and more
"""

import datetime
import sqlalchemy as s
import pandas as pd
from augur.util import logger, annotate, add_metrics

@annotate(tag='code-changes')
def code_changes(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
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
        begin_date = '1970-1-1 00:00:00:00'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    code_changes_SQL = ''

    if not repo_id:
        code_changes_SQL = s.sql.text("""
            SELECT
                commits.repo_id,
                repo_name,
                date_trunc(:period, cmt_committer_date::DATE) as date,
                COUNT(DISTINCT cmt_commit_hash) as commit_count
            FROM commits JOIN repo ON repo.repo_id = commits.repo_id
            WHERE commits.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND cmt_committer_date BETWEEN :begin_date AND :end_date
            GROUP BY commits.repo_id, date, repo_name
            ORDER BY commits.repo_id, date
        """)

        results = pd.read_sql(code_changes_SQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                                 'begin_date': begin_date, 'end_date': end_date})
        return results

    else:
        code_changes_SQL = s.sql.text("""
            SELECT
                repo_name,
                date_trunc(:period, cmt_committer_date::DATE) as date,
                COUNT(DISTINCT cmt_commit_hash) as commit_count
            FROM commits JOIN repo ON commits.repo_id = repo.repo_id
            WHERE commits.repo_id = :repo_id
            AND cmt_committer_date BETWEEN :begin_date AND :end_date
            GROUP BY date, repo_name
            ORDER BY date
        """)

        results = pd.read_sql(code_changes_SQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                                 'begin_date': begin_date, 'end_date': end_date})
        return results

@annotate(tag='code-changes-lines')
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



@annotate(tag='sub-projects')
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



@annotate(tag='sbom-download')
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

@annotate(tag='cii-best-practices-badge')
def cii_best_practices_badge(self, repo_group_id, repo_id=None):
    """Returns the CII best practices badge level

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: CII best parctices badge level
    """
    # Welcome to the Twilight Zone
    if repo_id:
        cii_best_practices_badge_SQL = s.sql.text("""
            SELECT repo_name, rg_name, repo_badging.data, repo_badging.created_at as date
            FROM repo_badging, repo, repo_groups
            WHERE repo.repo_group_id = repo_groups.repo_group_id AND repo.repo_id = repo_badging.repo_id
            AND repo_badging.repo_id = :repo_id
            ORDER BY date DESC
            LIMIT 1
        """)

        params = {'repo_id': repo_id}

    else:
        cii_best_practices_badge_SQL = s.sql.text("""
            SELECT repo_name, rg_name, repo_badging.data, repo_badging.created_at as date
            FROM repo_badging, repo, repo_groups
            WHERE repo.repo_group_id = repo_groups.repo_group_id AND repo.repo_id = repo_badging.repo_id
            AND repo.repo_group_id = :repo_group_id
            ORDER BY date DESC
            LIMIT 1
        """)

        params = {'repo_group_id': repo_group_id, 'repo_id': repo_id}

    raw_df = pd.read_sql(cii_best_practices_badge_SQL, self.database, params=params)
    badging_data = raw_df.iloc[0,2]

    result = {
        "repo_name": raw_df.iloc[0,0],
        "rg_name": raw_df.iloc[0,1]
    }

    for item in badging_data.items():
        if item[0] in ["badge_level", "achieve_passing_status", "achieve_silver_status", "tiered_percentage", "repo_url", "id"]:
            result[item[0]] = item[1]

    return pd.DataFrame(result, index=[0])

@annotate(tag='forks')
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

@annotate(tag='fork-count')
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

@annotate(tag='languages')
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

@annotate(tag='license-declared')
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
    select a.license_id, b.short_name, count(*) from files_licenses a, licenses b, augur_repo_map c, packages d, files e
    where a.license_id = b.license_id
    and
    d.package_id = c.dosocs_pkg_id
    and
    e.file_id = a.file_id
    and
    e.package_id = d.package_id
    and
    c.repo_id = :repo_id
    group by a.license_id, b.short_name
    order by b.short_name;
    """)

    results = pd.read_sql(license_declared_SQL, self.spdx_db, params={'repo_id': repo_id})
    return results

@annotate(tag='license-coverage')
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

@annotate(tag='license-count')
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


@annotate(tag='stars')
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

@annotate(tag='stars-count')
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

@annotate(tag='watchers')
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

@annotate(tag='watchers-count')
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

@annotate(tag='annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')
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
        calendar_year = 2019

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

@annotate(tag='annual-lines-of-code-count-ranked-by-repo-in-repo-group')
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

@annotate(tag='lines-of-code-commit-counts-by-calendar-year-grouped')
def lines_of_code_commit_counts_by_calendar_year_grouped(self, repo_url, calendar_year=None, interval=None):
    """
    For a single repository, all the commits and lines of code occuring for the specified year, grouped by the specified interval (week or month)

    :param repo_url: the repository's URL
    :param calendar_year: the calendar year a repo is created in to be considered "new"
    :param interval: Month or week. The periodocity of which to examine data within the given calendar_year
    """

    if calendar_year == None:
        calendar_year = 2018

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

def create_repo_meta_metrics(metrics):
    add_metrics(metrics, __name__)
