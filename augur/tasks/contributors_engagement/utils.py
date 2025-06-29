import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy import text
from augur.application.db.lib import get_session, bulk_insert_dicts
from augur.application.db.models import ContributorEngagement, Contributor


def get_d0_engagement_data(repo_id: int, logger: logging.Logger, full_collection: bool = True) -> List[Dict[str, Any]]:
    """
    Get D0 level engagement data (basic engagement: forks, stars/watches)
    
    Args:
        repo_id: Repository ID
        logger: Logger instance
        full_collection: Whether to perform full collection or incremental
        
    Returns:
        List of dictionaries containing D0 engagement data
    """
    
    logger.info(f"Executing D0 engagement query for repo_id: {repo_id} (full_collection: {full_collection})")
    
    time_filter = ""
    if not full_collection:
        time_filter = "AND cr.created_at >= NOW() - INTERVAL '30 days'"
    
    d0_query = text(f"""
        SELECT DISTINCT ON (c.cntrb_login, cr.cntrb_category)
          c.cntrb_id,
          c.cntrb_login AS username,
          c.cntrb_full_name AS full_name,
          c.cntrb_country_code AS country,
          CASE 
            WHEN cr.repo_git ILIKE '%gitlab%' THEN 'GitLab'
            WHEN cr.repo_git ILIKE '%github%' THEN 'GitHub'
            ELSE 'Unknown'
          END AS platform,
          (cr.cntrb_category = 'ForkEvent') AS forked,
          (cr.cntrb_category = 'WatchEvent') AS starred_or_watched,
          cr.created_at AS engagement_timestamp
        FROM 
          augur_data.contributors c
        JOIN 
          augur_data.contributor_repo cr ON cr.cntrb_id = c.cntrb_id
        WHERE 
          cr.cntrb_category IN ('ForkEvent', 'WatchEvent')
          AND cr.repo_git = (SELECT repo_git FROM augur_data.repo WHERE repo_id = :repo_id)
          {time_filter}
        ORDER BY
          c.cntrb_login, cr.cntrb_category, cr.created_at
    """)
    
    try:
        with get_session() as session:
            result = session.execute(d0_query, {"repo_id": repo_id})
            data = [dict(row._mapping) for row in result.fetchall()]
            logger.info(f"Retrieved {len(data)} D0 engagement records ({'full' if full_collection else 'incremental'} collection)")
            return data
    except Exception as e:
        logger.error(f"Error executing D0 engagement query: {e}")
        return []


def get_d1_engagement_data(repo_id: int, logger: logging.Logger, full_collection: bool = True) -> List[Dict[str, Any]]:
    """
    Get D1 level engagement data (issue/review engagement)
    
    Args:
        repo_id: Repository ID
        logger: Logger instance
        full_collection: Whether to perform full collection or incremental
        
    Returns:
        List of dictionaries containing D1 engagement data
    """
    
    logger.info(f"Executing D1 engagement query for repo_id: {repo_id} (full_collection: {full_collection})")
    
    time_filter = "1 year"
    if not full_collection:
        time_filter = "30 days"
    
    d1_query = text(f"""
        SELECT
          c.cntrb_id,
          c.cntrb_login AS username,
          c.cntrb_full_name AS full_name,
          c.cntrb_country_code AS country,
          'GitHub' AS platform,
          MIN(i.created_at) AS first_issue_created_at,
          MIN(pr.pr_created_at) AS first_pr_opened_at,
          MIN(pm.msg_timestamp) AS first_pr_commented_at
        FROM
          augur_data.contributors c

        LEFT JOIN augur_data.issues i
          ON i.reporter_id = c.cntrb_id AND i.repo_id = :repo_id

        LEFT JOIN augur_data.pull_requests pr
          ON pr.pr_augur_contributor_id = c.cntrb_id AND pr.repo_id = :repo_id

        LEFT JOIN augur_data.pull_request_message_ref pmr
          ON pmr.pull_request_id = pr.pull_request_id
        LEFT JOIN augur_data.message pm
          ON pm.msg_id = pmr.msg_id AND pm.cntrb_id = c.cntrb_id AND pm.repo_id = :repo_id

        WHERE
          (i.created_at >= NOW() - INTERVAL '{time_filter}'
           OR pr.pr_created_at >= NOW() - INTERVAL '{time_filter}'
           OR pm.msg_timestamp >= NOW() - INTERVAL '{time_filter}')

        GROUP BY
          c.cntrb_id, c.cntrb_login, c.cntrb_full_name, c.cntrb_country_code
        HAVING
          MIN(i.created_at) IS NOT NULL 
          OR MIN(pr.pr_created_at) IS NOT NULL 
          OR MIN(pm.msg_timestamp) IS NOT NULL
    """)
    
    try:
        with get_session() as session:
            result = session.execute(d1_query, {"repo_id": repo_id})
            data = [dict(row._mapping) for row in result.fetchall()]
            logger.info(f"Retrieved {len(data)} D1 engagement records ({'full' if full_collection else 'incremental'} collection)")
            return data
    except Exception as e:
        logger.error(f"Error executing D1 engagement query: {e}")
        return []


def get_d2_engagement_data(repo_id: int, logger: logging.Logger, full_collection: bool = True) -> List[Dict[str, Any]]:
    """
    Get D2 level engagement data (significant contributions)
    
    Args:
        repo_id: Repository ID
        logger: Logger instance
        full_collection: Whether to perform full collection or incremental
        
    Returns:
        List of dictionaries containing D2 engagement data
    """
    
    logger.info(f"Executing D2 engagement query for repo_id: {repo_id} (full_collection: {full_collection})")
    
    if not full_collection:
        pr_merged_time_filter = "AND pr.pr_merged_at >= NOW() - INTERVAL '90 days'"
        issue_time_filter = "AND i.created_at >= NOW() - INTERVAL '90 days'"
        comment_time_filter = "AND m.msg_timestamp >= NOW() - INTERVAL '90 days'"
        pr_commits_time_filter = "AND pr.pr_created_at >= NOW() - INTERVAL '90 days'"
        comment_pr_time_filter = "AND m.msg_timestamp >= NOW() - INTERVAL '90 days'"
    else:
        pr_merged_time_filter = ""
        issue_time_filter = ""
        comment_time_filter = ""
        pr_commits_time_filter = ""
        comment_pr_time_filter = ""
    
    d2_query = text(f"""
        WITH pr_merged AS (
          SELECT DISTINCT pr.pr_augur_contributor_id
          FROM augur_data.pull_requests pr
          WHERE pr.pr_merged_at IS NOT NULL AND pr.repo_id = :repo_id
          {pr_merged_time_filter}
        ),

        issue_counts AS (
          SELECT reporter_id AS cntrb_id, COUNT(*) AS issue_count
          FROM augur_data.issues i
          WHERE repo_id = :repo_id
          {issue_time_filter}
          GROUP BY reporter_id
        ),

        comment_counts AS (
          SELECT m.cntrb_id, COUNT(*) AS total_comments
          FROM augur_data.message m
          LEFT JOIN augur_data.issue_message_ref imr ON imr.msg_id = m.msg_id
          LEFT JOIN augur_data.pull_request_message_ref pmr ON pmr.msg_id = m.msg_id
          LEFT JOIN augur_data.issues i ON i.issue_id = imr.issue_id
          LEFT JOIN augur_data.pull_requests pr ON pr.pull_request_id = pmr.pull_request_id
          WHERE m.repo_id = :repo_id 
            AND (i.repo_id = :repo_id OR pr.repo_id = :repo_id)
            AND (imr.issue_id IS NOT NULL OR pmr.pull_request_id IS NOT NULL)
            {comment_time_filter}
          GROUP BY m.cntrb_id
        ),

        pr_commits_over_3 AS (
          SELECT pr.pr_augur_contributor_id AS cntrb_id
          FROM augur_data.pull_requests pr
          JOIN augur_data.pull_request_commits prc ON prc.pull_request_id = pr.pull_request_id
          WHERE pr.repo_id = :repo_id
          {pr_commits_time_filter}
          GROUP BY pr.pr_augur_contributor_id, pr.pull_request_id
          HAVING COUNT(prc.pr_cmt_sha) > 3
        ),

        commented_on_multiple_prs AS (
          SELECT m.cntrb_id
          FROM augur_data.message m
          JOIN augur_data.pull_request_message_ref pmr ON pmr.msg_id = m.msg_id
          JOIN augur_data.pull_requests pr ON pr.pull_request_id = pmr.pull_request_id
          WHERE m.repo_id = :repo_id AND pr.repo_id = :repo_id
          {comment_pr_time_filter}
          GROUP BY m.cntrb_id
          HAVING COUNT(DISTINCT pmr.pull_request_id) > 2
        )

        SELECT 
          c.cntrb_id,
          c.cntrb_login AS username,
          c.cntrb_full_name AS full_name,
          c.cntrb_country_code AS country,
          'GitHub' AS platform,
          CASE WHEN pm.pr_augur_contributor_id IS NOT NULL THEN true ELSE false END AS has_merged_pr,
          CASE WHEN ic.issue_count > 5 THEN true ELSE false END AS created_many_issues,
          COALESCE(cc.total_comments, 0) AS total_comments,
          CASE WHEN pco3.cntrb_id IS NOT NULL THEN true ELSE false END AS has_pr_with_many_commits,
          CASE WHEN cmp.cntrb_id IS NOT NULL THEN true ELSE false END AS commented_on_multiple_prs
        FROM augur_data.contributors c
        LEFT JOIN pr_merged pm ON pm.pr_augur_contributor_id = c.cntrb_id
        LEFT JOIN issue_counts ic ON ic.cntrb_id = c.cntrb_id
        LEFT JOIN comment_counts cc ON cc.cntrb_id = c.cntrb_id
        LEFT JOIN pr_commits_over_3 pco3 ON pco3.cntrb_id = c.cntrb_id
        LEFT JOIN commented_on_multiple_prs cmp ON cmp.cntrb_id = c.cntrb_id
        WHERE (pm.pr_augur_contributor_id IS NOT NULL 
               OR ic.cntrb_id IS NOT NULL 
               OR cc.cntrb_id IS NOT NULL 
               OR pco3.cntrb_id IS NOT NULL 
               OR cmp.cntrb_id IS NOT NULL)
    """)
    
    try:
        with get_session() as session:
            result = session.execute(d2_query, {"repo_id": repo_id})
            data = [dict(row._mapping) for row in result.fetchall()]
            logger.info(f"Retrieved {len(data)} D2 engagement records ({'full' if full_collection else 'incremental'} collection)")
            return data
    except Exception as e:
        logger.error(f"Error executing D2 engagement query: {e}")
        return []


def process_engagement_data(
    engagement_data: List[Dict[str, Any]], 
    repo_id: int, 
    task_name: str, 
    logger: logging.Logger,
    engagement_level: str,
    full_collection: bool = True
) -> int:
    """
    Process and insert engagement data into the database
    
    Args:
        engagement_data: List of engagement data dictionaries
        repo_id: Repository ID
        task_name: Name of the task for logging
        logger: Logger instance
        engagement_level: Level of engagement (d0, d1, d2)
        full_collection: Whether to perform full collection or incremental
        
    Returns:
        Number of records processed
    """
    
    if not engagement_data:
        logger.info(f"{task_name}: No engagement data to process")
        return 0
    
    logger.info(f"{task_name}: Processing {len(engagement_data)} {engagement_level} engagement records ({'full' if full_collection else 'incremental'} collection)")
    
    tool_source = "Contributor Engagement Task"
    tool_version = "1.0"
    data_source = "Augur Database"
    
    processed_records = []
    
    for record in engagement_data:
        engagement_record = {
            "repo_id": repo_id,
            "cntrb_id": record.get("cntrb_id"),
            "username": record.get("username", ""),
            "full_name": record.get("full_name"),
            "country": record.get("country"),
            "platform": record.get("platform", "Unknown"),
            "tool_source": tool_source,
            "tool_version": tool_version,
            "data_source": data_source
        }
        
        if engagement_level == "d0":
            engagement_record.update({
                "d0_forked": record.get("forked", False),
                "d0_starred_or_watched": record.get("starred_or_watched", False),
                "d0_engagement_timestamp": record.get("engagement_timestamp")
            })
        elif engagement_level == "d1":
            engagement_record.update({
                "d1_first_issue_created_at": record.get("first_issue_created_at"),
                "d1_first_pr_opened_at": record.get("first_pr_opened_at"),
                "d1_first_pr_commented_at": record.get("first_pr_commented_at")
            })
        elif engagement_level == "d2":
            engagement_record.update({
                "d2_has_merged_pr": record.get("has_merged_pr", False),
                "d2_created_many_issues": record.get("created_many_issues", False),
                "d2_total_comments": record.get("total_comments", 0),
                "d2_has_pr_with_many_commits": record.get("has_pr_with_many_commits", False),
                "d2_commented_on_multiple_prs": record.get("commented_on_multiple_prs", False)
            })
        
        processed_records.append(engagement_record)
    
    try:
        natural_keys = ["repo_id", "cntrb_id"]
        string_fields = ["username", "full_name", "platform"]
        
        bulk_insert_dicts(
            logger, 
            processed_records, 
            ContributorEngagement, 
            natural_keys,
            string_fields=string_fields
        )
        
        logger.info(f"{task_name}: Successfully inserted {len(processed_records)} {engagement_level} engagement records ({'full' if full_collection else 'incremental'} collection)")
        return len(processed_records)
        
    except Exception as e:
        logger.error(f"{task_name}: Error inserting {engagement_level} engagement data: {e}")
        return 0

def create_materialized_views(logger: logging.Logger) -> bool:
    """
    Create materialized views for D0, D1, D2 engagement levels
    
    Args:
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    
    logger.info("Creating contributor engagement materialized views")
    
    # D0 Materialized View
    d0_view_sql = text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS augur_data.d0_contributor_engagement AS
        SELECT DISTINCT ON (c.cntrb_login, cr.cntrb_category)
          c.cntrb_login AS username,
          c.cntrb_full_name AS full_name,
          c.cntrb_country_code AS country,
          CASE 
            WHEN cr.repo_git ILIKE '%gitlab%' THEN 'GitLab'
            WHEN cr.repo_git ILIKE '%github%' THEN 'GitHub'
            ELSE 'Unknown'
          END AS platform,
          cr.cntrb_category = 'ForkEvent' AS forked,
          cr.cntrb_category = 'WatchEvent' AS starred_or_watched,
          cr.created_at AS engagement_timestamp
        FROM 
          augur_data.contributors c
        JOIN 
          augur_data.contributor_repo cr ON cr.cntrb_id = c.cntrb_id
        WHERE 
          cr.cntrb_category IN ('ForkEvent', 'WatchEvent')
        ORDER BY
          c.cntrb_login, cr.cntrb_category, cr.created_at;
    """)
    
    # D1 Materialized View
    d1_view_sql = text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS augur_data.d1_contributor_engagement AS
        SELECT
          c.cntrb_login AS username,
          MIN(i.created_at) AS first_issue_created_at,
          MIN(pr.pr_created_at) AS first_pr_opened_at,
          MIN(pm.msg_timestamp) AS first_pr_commented_at
        FROM
          augur_data.contributors c
        LEFT JOIN augur_data.issues i
          ON i.reporter_id = c.cntrb_id
        LEFT JOIN augur_data.pull_requests pr
          ON pr.pr_augur_contributor_id = c.cntrb_id
        LEFT JOIN augur_data.pull_request_message_ref pmr
          ON pmr.pull_request_id = pr.pull_request_id
        LEFT JOIN augur_data.message pm
          ON pm.msg_id = pmr.msg_id AND pm.cntrb_id = c.cntrb_id
        WHERE
          (i.created_at >= NOW() - INTERVAL '1 year'
           OR pr.pr_created_at >= NOW() - INTERVAL '1 year'
           OR pm.msg_timestamp >= NOW() - INTERVAL '1 year')
        GROUP BY
          c.cntrb_login;
    """)
    
    # D2 Materialized View
    d2_view_sql = text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS augur_data.d2_contributor_engagement AS
        WITH pr_merged AS (
          SELECT DISTINCT pr.pr_augur_contributor_id
          FROM augur_data.pull_requests pr
          WHERE pr.pr_merged_at IS NOT NULL
        ),
        issue_counts AS (
          SELECT reporter_id AS cntrb_id, COUNT(*) AS issue_count
          FROM augur_data.issues
          GROUP BY reporter_id
        ),
        comment_counts AS (
          SELECT m.cntrb_id, COUNT(*) AS total_comments
          FROM augur_data.message m
          LEFT JOIN augur_data.issue_message_ref imr ON imr.msg_id = m.msg_id
          LEFT JOIN augur_data.pull_request_message_ref pmr ON pmr.msg_id = m.msg_id
          WHERE imr.issue_id IS NOT NULL OR pmr.pull_request_id IS NOT NULL
          GROUP BY m.cntrb_id
        ),
        pr_commits_over_3 AS (
          SELECT pr.pr_augur_contributor_id AS cntrb_id
          FROM augur_data.pull_requests pr
          JOIN augur_data.pull_request_commits prc ON prc.pull_request_id = pr.pull_request_id
          GROUP BY pr.pr_augur_contributor_id, pr.pull_request_id
          HAVING COUNT(prc.pr_cmt_sha) > 3
        ),
        commented_on_multiple_prs AS (
          SELECT m.cntrb_id
          FROM augur_data.message m
          JOIN augur_data.pull_request_message_ref pmr ON pmr.msg_id = m.msg_id
          GROUP BY m.cntrb_id
          HAVING COUNT(DISTINCT pmr.pull_request_id) > 2
        )
        SELECT 
          c.cntrb_login AS username,
          CASE WHEN pm.pr_augur_contributor_id IS NOT NULL THEN true ELSE false END AS has_merged_pr,
          CASE WHEN ic.issue_count > 5 THEN true ELSE false END AS created_many_issues,
          COALESCE(cc.total_comments, 0) AS total_comments,
          CASE WHEN pco3.cntrb_id IS NOT NULL THEN true ELSE false END AS has_pr_with_many_commits,
          CASE WHEN cmp.cntrb_id IS NOT NULL THEN true ELSE false END AS commented_on_multiple_prs
        FROM augur_data.contributors c
        LEFT JOIN pr_merged pm ON pm.pr_augur_contributor_id = c.cntrb_id
        LEFT JOIN issue_counts ic ON ic.cntrb_id = c.cntrb_id
        LEFT JOIN comment_counts cc ON cc.cntrb_id = c.cntrb_id
        LEFT JOIN pr_commits_over_3 pco3 ON pco3.cntrb_id = c.cntrb_id
        LEFT JOIN commented_on_multiple_prs cmp ON cmp.cntrb_id = c.cntrb_id;
    """)
    
    try:
        with get_session() as session:
            session.execute(d0_view_sql)
            session.execute(d1_view_sql)
            session.execute(d2_view_sql)
            session.commit()
            
            logger.info("Successfully created contributor engagement materialized views")
            return True
            
    except Exception as e:
        logger.error(f"Error creating materialized views: {e}")
        return False


def refresh_materialized_views(logger: logging.Logger) -> bool:
    """
    Refresh the contributor engagement materialized views
    
    Args:
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    
    logger.info("Refreshing contributor engagement materialized views")
    
    refresh_queries = [
        text("REFRESH MATERIALIZED VIEW augur_data.d0_contributor_engagement;"),
        text("REFRESH MATERIALIZED VIEW augur_data.d1_contributor_engagement;"),
        text("REFRESH MATERIALIZED VIEW augur_data.d2_contributor_engagement;")
    ]
    
    try:
        with get_session() as session:
            for query in refresh_queries:
                session.execute(query)
            session.commit()
            
            logger.info("Successfully refreshed contributor engagement materialized views")
            return True
            
    except Exception as e:
        logger.error(f"Error refreshing materialized views: {e}")
        return False

