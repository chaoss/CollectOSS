"""
Directory, which is for utility/non-metric endpoints.
"""

import datetime
import base64
import sqlalchemy as s
import pandas as pd
from augur.util import annotate, add_metrics

@annotate(tag='repo-groups')
def repo_groups(self):
    """
    Returns number of lines changed per author per day

    :param repo_url: the repository's URL
    """
    repoGroupsSQL = s.sql.text("""
        SELECT *
        FROM repo_groups
        ORDER BY rg_name
    """)
    results = pd.read_sql(repoGroupsSQL, self.database)
    return results

@annotate(tag='downloaded-repos')
def downloaded_repos(self):
    """
    Returns all repository names, URLs, and base64 URLs in the facade database
    """
    downloadedReposSQL = s.sql.text("""
        SELECT
            repo.repo_id,
            repo.repo_name,
            repo.description,
            repo.repo_git AS url,
            repo.repo_status,
            a.commits_all_time,
            b.issues_all_time ,
            rg_name,
            repo.repo_group_id
        FROM
            repo
            left outer join
            (select repo_id,    COUNT ( commits.cmt_id ) AS commits_all_time from commits group by repo_id ) a on
            repo.repo_id = a.repo_id
            left outer join
            (select repo_id, count ( * ) as issues_all_time from issues where issues.pull_request IS NULL  group by repo_id) b
            on
            repo.repo_id = b.repo_id
            JOIN repo_groups ON repo_groups.repo_group_id = repo.repo_group_id
        order by repo_name
    """)
    results = pd.read_sql(downloadedReposSQL, self.database)
    results['url'] = results['url'].apply(lambda datum: datum.split('//')[1])
    # if self.projects:
    #     results = results[results.project_name.isin(self.projects)]
    if self.projects:
          results = results[results.project_name.isin(self.projects)]

    b64_urls = []
    for i in results.index:
        b64_urls.append(base64.b64encode((results.at[i, 'url']).encode()))
    results['base64_url'] = b64_urls

    return results

@annotate(tag='repos-in-repo-groups')
def repos_in_repo_groups(self, repo_group_id):
    """
    Returns a list of all the repos in a repo_group

    :param repo_group_id: The repository's repo_group_id
    """
    repos_in_repo_groups_SQL = s.sql.text("""
        SELECT
            repo.repo_id,
            repo.repo_name,
            repo.description,
            repo.repo_git AS url,
            repo.repo_status,
            a.commits_all_time,
            b.issues_all_time
        FROM
            repo
            left outer join
            (select repo_id, COUNT ( commits.cmt_id ) AS commits_all_time from commits group by repo_id ) a on
            repo.repo_id = a.repo_id
            left outer join
            (select repo_id, count ( issues.issue_id) as issues_all_time from issues where issues.pull_request IS NULL group by repo_id) b
            on
            repo.repo_id = b.repo_id
            JOIN repo_groups ON repo_groups.repo_group_id = repo.repo_group_id
        WHERE
            repo_groups.repo_group_id = :repo_group_id
        ORDER BY repo.repo_git
    """)

    results = pd.read_sql(repos_in_repo_groups_SQL, self.database, params={'repo_group_id': repo_group_id})
    return results

@annotate(tag='get-repo-by-git-name')
def get_repo_by_git_name(self, owner, repo):
    """
    Returns repo id and repo group id by owner and repo

    :param owner: the owner of the repo
    :param repo: the name of the repo
    """
    getRepoSQL = s.sql.text("""
        SELECT repo.repo_id, repo.repo_group_id, rg_name
        FROM repo JOIN repo_groups ON repo_groups.repo_group_id = repo.repo_group_id
        WHERE repo_name = :repo AND repo_path LIKE :owner
        GROUP BY repo_id, rg_name
    """)

    results = pd.read_sql(getRepoSQL, self.database, params={'owner': '%{}_'.format(owner), 'repo': repo,})

    return results

@annotate(tag='get-repo-by-name')
def get_repo_by_name(self, rg_name, repo_name):
    """
    Returns repo id and repo group id by rg_name and repo_name

    :param rg_name: the repo group of the repo
    :param repo_name: the name of the repo
    """

    repoSQL = s.sql.text("""
        SELECT repo_id, repo.repo_group_id, repo_git as url
        FROM repo, repo_groups
        WHERE repo.repo_group_id = repo_groups.repo_group_id
        AND LOWER(rg_name) = LOWER(:rg_name)
        AND LOWER(repo_name) = LOWER(:repo_name)
    """)
    results = pd.read_sql(repoSQL, self.database, params={'rg_name': rg_name, 'repo_name': repo_name})
    results['url'] = results['url'].apply(lambda datum: datum.split('//')[1])
    return results

def get_group_by_name(self, rg_name):
    """
    Returns repo group id by repo group name

    :param rg_name:
    """
    groupSQL = s.sql.text("""
        SELECT repo_group_id, rg_name
        FROM repo_groups
        WHERE lower(rg_name) = lower(:rg_name)
    """)
    results = pd.read_sql(groupSQL, self.database, params={'rg_name': rg_name})
    return results

@annotate(tag='dosocs-repos')
def get_repos_for_dosocs(self):
    """ Returns a list of repos along with their repo_id & path """
    get_repos_for_dosocs_SQL = s.sql.text("""
        SELECT b.repo_id, CONCAT(a.value || b.repo_group_id || chr(47) || b.repo_path || b.repo_name) AS path
        FROM settings a, repo b
        WHERE a.setting='repo_directory'
    """)

    results = pd.read_sql(get_repos_for_dosocs_SQL, self.database)
    return results

@annotate(tag="get-issues")
def get_issues(self, repo_group_id, repo_id=None):
    if not repo_id:
        issuesSQL = s.sql.text("""
            SELECT issue_title,
                issues.issue_id,
                issues.repo_id,
                issues.html_url,
                issue_state                                 AS STATUS,
                issues.created_at                           AS DATE,
                count(issue_events.event_id),
                MAX(issue_events.created_at)                AS LAST_EVENT_DATE,
                EXTRACT(DAY FROM NOW() - issues.created_at) AS OPEN_DAY
            FROM issues,
                issue_events
            WHERE issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND issues.issue_id = issue_events.issue_id
            AND issues.pull_request is NULL
            GROUP BY issues.issue_id
            ORDER by OPEN_DAY DESC
        """)
        results = pd.read_sql(issuesSQL, self.database, params={'repo_group_id': repo_group_id})
        return results
    else:
        issuesSQL = s.sql.text("""
            SELECT issue_title,
                issues.issue_id,
                issues.repo_id,
                issues.html_url,
                issue_state                                 AS STATUS,
                issues.created_at                           AS DATE,
                count(issue_events.event_id),
                MAX(issue_events.created_at)                AS LAST_EVENT_DATE,
                EXTRACT(DAY FROM NOW() - issues.created_at) AS OPEN_DAY,
                repo_name
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id, issue_events
            WHERE issues.repo_id = :repo_id
            AND issues.pull_request IS NULL 
            AND issues.issue_id = issue_events.issue_id
            GROUP BY issues.issue_id, repo_name
            ORDER by OPEN_DAY DESC
        """)
        results = pd.read_sql(issuesSQL, self.database, params={'repo_id': repo_id})
        return results

@annotate(tag="aggregate-summary")
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

def create_util_metrics(metrics):
    add_metrics(metrics, __name__)
