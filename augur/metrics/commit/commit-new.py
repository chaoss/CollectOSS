SELECT A.repo_id,
	b.repo_group_id,
	A.cmt_committer_timestamp,
	A.cmt_author_name,
	b.repo_git,
	A.cmt_commit_hash,
	SUM ( A.cmt_whitespace ) AS total_commit_lines_whitespace,
	SUM ( A.cmt_added ) AS total_commit_lines_added,
	SUM ( A.cmt_removed ) AS total_commit_lines_removed,
	COUNT ( A.cmt_filename ) AS file_count 
FROM
	commits A,
	repo b 
WHERE
	A.repo_id = b.repo_id 
	AND b.repo_id = 25328 
	AND b.repo_group_id = 25000 
GROUP BY
	A.repo_id,
	b.repo_group_id,
	A.cmt_committer_timestamp,
	A.cmt_author_name,
	b.repo_git,
	A.cmt_commit_hash 
ORDER BY
 repo_group_id, repo_id, cmt_committer_timestamp

@annotate(tag='commit-metadata-with-timestamp')
def commit_metadata_with_timestamp(self, repo_group_id, repo_id=None, timeframe=None):
    """
    For each commit in a repository in a collection of repositories being managed, each COMMIT show the commit timestamp, commit author name, repository git url, commit hash, total whitespace lines, total lines added, total lines removed and total files included.
    Result list in ascending order by timestamp.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param timeframe: the calendar year a repo is created in to be considered "new"
    """
    if timeframe == None:
        timeframe = 'all'

    cdRgCmtMetaWithTimestampSQL = None

    if repo_id:
        if timeframe == 'all':
            cdRgCmtMetaWithTimestampSQL = s.sql.text("""
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
            cdRgCmtMetaWithTimestampSQL = s.sql.text("""
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
            cdRgCmtMetaWithTimestampSQL = s.sql.text("""
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
            cdRgCmtMetaWithTimestampSQL = s.sql.text("""
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
            cdRgCmtMetaWithTimestampSQL = s.sql.text(
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
            cdRgCmtMetaWithTimestampSQL = s.sql.text("""
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


    results = pd.read_sql(cdRgCmtMetaWithTimestampSQL, self.database, params={ "repo_group_id": repo_group_id,
    "repo_id": repo_id})
    return results


@annotate(tag='commit-metadata-with-timestamp')
def commit_metadata_with_timestamp(self, repo_group_id, repo_id = None, calendar_year=None):
    """
    For each commit in a repository in a collection of repositories being managed, each COMMIT show the commit timestamp, commit author name, repository git url, commit hash, total whitespace lines, total lines added, total lines removed and total files included.
    Result list in ascending order by timestamp.

    :param repo_url: the repository's git URL
    :param repo_group: the group of repositories to analyze
    """

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