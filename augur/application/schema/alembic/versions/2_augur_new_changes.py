"""Augur New Changes

Revision ID: 2
Revises: 1
Create Date: 2022-12-11 11:17:31.706564

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text
from augur.tasks.util.AugurUUID import AugurUUID, GithubUUID, UnresolvableUUID


# revision identifiers, used by Alembic.
revision = '2'
down_revision = '1'
branch_labels = None
depends_on = '1'


def upgrade():

    add_update_materialized_views_1()

def downgrade():

    upgrade=False

    add_update_materialized_views_1(upgrade)

def add_update_materialized_views_1(upgrade=True):

    if upgrade:
        conn = op.get_bind()
        conn.execute(text("""
        drop materialized view if exists augur_data.explorer_contributor_actions; 
        drop materialized view if exists augur_data.explorer_entry_list; 
        drop materialized view if exists augur_data.api_get_all_repo_prs;""")) 

        conn = op.get_bind()
        conn.execute(text("""
        create materialized view augur_data.api_get_all_repo_prs as 
        SELECT
            pull_requests.repo_id,
            COUNT ( * ) AS pull_requests_all_time 
        FROM
            augur_data.pull_requests 
        GROUP BY pull_requests.repo_id;"""))

        conn.execute(text("""
        create materialized view augur_data.explorer_entry_list as 
        SELECT DISTINCT r.repo_git,
            rg.rg_name
        FROM (augur_data.repo r
            JOIN augur_data.repo_groups rg ON ((rg.repo_group_id = r.repo_group_id)))
        ORDER BY rg.rg_name;"""))

 
        conn.execute(text("""
        create materialized view augur_data.explorer_contributor_actions as 
         SELECT
            x.cntrb_id,
            x.created_at,
            x.repo_id,
            x.LOGIN,
            x.ACTION,
            x.RANK 
         FROM
            (
            SELECT
               b.cntrb_id,
               b.created_at,
               b.MONTH,
               b.YEAR,
               b.repo_id,
               b.repo_name,
               b.full_name,
               b.LOGIN,
               b.ACTION,
               b.RANK 
            FROM
               (
               SELECT A
                  .ID AS cntrb_id,
                  A.created_at,
                  date_part( 'month' :: TEXT, ( A.created_at ) :: DATE ) AS MONTH,
                  date_part( 'year' :: TEXT, ( A.created_at ) :: DATE ) AS YEAR,
                  A.repo_id,
                  repo.repo_name,
                  A.full_name,
                  A.LOGIN,
                  A.ACTION,
                  RANK ( ) OVER ( PARTITION BY A.ID, A.repo_id ORDER BY A.created_at ) AS RANK 
               FROM
                  (
                  SELECT
                     canonical_full_names.canonical_id AS ID,
                     issues.created_at,
                     issues.repo_id,
                     'issue_opened' :: TEXT AS ACTION,
                     contributors.cntrb_full_name AS full_name,
                     contributors.cntrb_login AS LOGIN 
                  FROM
                     (
                        ( augur_data.issues LEFT JOIN augur_data.contributors ON ( ( contributors.cntrb_id = issues.reporter_id ) ) )
                        LEFT JOIN (
                        SELECT DISTINCT ON
                           ( contributors_1.cntrb_canonical ) contributors_1.cntrb_full_name,
                           contributors_1.cntrb_canonical AS canonical_email,
                           contributors_1.data_collection_date,
                           contributors_1.cntrb_id AS canonical_id 
                        FROM
                           augur_data.contributors contributors_1 
                        WHERE
                           ( ( contributors_1.cntrb_canonical ) :: TEXT = ( contributors_1.cntrb_email ) :: TEXT ) 
                        ORDER BY
                           contributors_1.cntrb_canonical 
                        ) canonical_full_names ON ( ( ( canonical_full_names.canonical_email ) :: TEXT = ( contributors.cntrb_canonical ) :: TEXT ) ) 
                     ) 
                  WHERE
                     ( issues.pull_request IS NULL ) 
                  GROUP BY
                     canonical_full_names.canonical_id,
                     issues.repo_id,
                     issues.created_at,
                     contributors.cntrb_full_name,
                     contributors.cntrb_login UNION ALL
                  SELECT
                     canonical_full_names.canonical_id AS ID,
                     to_timestamp( ( commits.cmt_author_date ) :: TEXT, 'YYYY-MM-DD' :: TEXT ) AS created_at,
                     commits.repo_id,
                     'commit' :: TEXT AS ACTION,
                     contributors.cntrb_full_name AS full_name,
                     contributors.cntrb_login AS LOGIN 
                  FROM
                     (
                        ( augur_data.commits LEFT JOIN augur_data.contributors ON ( ( ( contributors.cntrb_canonical ) :: TEXT = ( commits.cmt_author_email ) :: TEXT ) ) )
                        LEFT JOIN (
                        SELECT DISTINCT ON
                           ( contributors_1.cntrb_canonical ) contributors_1.cntrb_full_name,
                           contributors_1.cntrb_canonical AS canonical_email,
                           contributors_1.data_collection_date,
                           contributors_1.cntrb_id AS canonical_id 
                        FROM
                           augur_data.contributors contributors_1 
                        WHERE
                           ( ( contributors_1.cntrb_canonical ) :: TEXT = ( contributors_1.cntrb_canonical ) :: TEXT ) 
                        ORDER BY
                           contributors_1.cntrb_canonical 
                        ) canonical_full_names ON ( ( ( canonical_full_names.canonical_email ) :: TEXT = ( contributors.cntrb_canonical ) :: TEXT ) ) 
                     ) 
                  GROUP BY
                     commits.repo_id,
                     canonical_full_names.canonical_email,
                     canonical_full_names.canonical_id,
                     commits.cmt_author_date,
                     contributors.cntrb_full_name,
                     contributors.cntrb_login UNION ALL
                  SELECT
                     message.cntrb_id AS ID,
                     commit_comment_ref.created_at,
                     commits.repo_id,
                     'commit_comment' :: TEXT AS ACTION,
                     contributors.cntrb_full_name AS full_name,
                     contributors.cntrb_login AS LOGIN 
                  FROM
                     augur_data.commit_comment_ref,
                     augur_data.commits,
                     (
                        ( augur_data.message LEFT JOIN augur_data.contributors ON ( ( contributors.cntrb_id = message.cntrb_id ) ) )
                        LEFT JOIN (
                        SELECT DISTINCT ON
                           ( contributors_1.cntrb_canonical ) contributors_1.cntrb_full_name,
                           contributors_1.cntrb_canonical AS canonical_email,
                           contributors_1.data_collection_date,
                           contributors_1.cntrb_id AS canonical_id 
                        FROM
                           augur_data.contributors contributors_1 
                        WHERE
                           ( ( contributors_1.cntrb_canonical ) :: TEXT = ( contributors_1.cntrb_email ) :: TEXT ) 
                        ORDER BY
                           contributors_1.cntrb_canonical 
                        ) canonical_full_names ON ( ( ( canonical_full_names.canonical_email ) :: TEXT = ( contributors.cntrb_canonical ) :: TEXT ) ) 
                     ) 
                  WHERE
                     ( ( commits.cmt_id = commit_comment_ref.cmt_id ) AND ( commit_comment_ref.msg_id = message.msg_id ) ) 
                  GROUP BY
                     message.cntrb_id,
                     commits.repo_id,
                     commit_comment_ref.created_at,
                     contributors.cntrb_full_name,
                     contributors.cntrb_login UNION ALL
                  SELECT
                     issue_events.cntrb_id AS ID,
                     issue_events.created_at,
                     issues.repo_id,
                     'issue_closed' :: TEXT AS ACTION,
                     contributors.cntrb_full_name AS full_name,
                     contributors.cntrb_login AS LOGIN 
                  FROM
                     augur_data.issues,
                     (
                        ( augur_data.issue_events LEFT JOIN augur_data.contributors ON ( ( contributors.cntrb_id = issue_events.cntrb_id ) ) )
                        LEFT JOIN (
                        SELECT DISTINCT ON
                           ( contributors_1.cntrb_canonical ) contributors_1.cntrb_full_name,
                           contributors_1.cntrb_canonical AS canonical_email,
                           contributors_1.data_collection_date,
                           contributors_1.cntrb_id AS canonical_id 
                        FROM
                           augur_data.contributors contributors_1 
                        WHERE
                           ( ( contributors_1.cntrb_canonical ) :: TEXT = ( contributors_1.cntrb_email ) :: TEXT ) 
                        ORDER BY
                           contributors_1.cntrb_canonical 
                        ) canonical_full_names ON ( ( ( canonical_full_names.canonical_email ) :: TEXT = ( contributors.cntrb_canonical ) :: TEXT ) ) 
                     ) 
                  WHERE
                     (
                        ( issues.issue_id = issue_events.issue_id ) 
                        AND ( issues.pull_request IS NULL ) 
                        AND ( issue_events.cntrb_id IS NOT NULL ) 
                        AND ( ( issue_events.ACTION ) :: TEXT = 'closed' :: TEXT ) 
                     ) 
                  GROUP BY
                     issue_events.cntrb_id,
                     issues.repo_id,
                     issue_events.created_at,
                     contributors.cntrb_full_name,
                     contributors.cntrb_login UNION ALL
                  SELECT
                     pull_requests.pr_augur_contributor_id AS ID,
                     pull_requests.pr_created_at AS created_at,
                     pull_requests.repo_id,
                     'open_pull_request' :: TEXT AS ACTION,
                     contributors.cntrb_full_name AS full_name,
                     contributors.cntrb_login AS LOGIN 
                  FROM
                     (
                        ( augur_data.pull_requests LEFT JOIN augur_data.contributors ON ( ( pull_requests.pr_augur_contributor_id = contributors.cntrb_id ) ) )
                        LEFT JOIN (
                        SELECT DISTINCT ON
                           ( contributors_1.cntrb_canonical ) contributors_1.cntrb_full_name,
                           contributors_1.cntrb_canonical AS canonical_email,
                           contributors_1.data_collection_date,
                           contributors_1.cntrb_id AS canonical_id 
                        FROM
                           augur_data.contributors contributors_1 
                        WHERE
                           ( ( contributors_1.cntrb_canonical ) :: TEXT = ( contributors_1.cntrb_email ) :: TEXT ) 
                        ORDER BY
                           contributors_1.cntrb_canonical 
                        ) canonical_full_names ON ( ( ( canonical_full_names.canonical_email ) :: TEXT = ( contributors.cntrb_canonical ) :: TEXT ) ) 
                     ) 
                  GROUP BY
                     pull_requests.pr_augur_contributor_id,
                     pull_requests.repo_id,
                     pull_requests.pr_created_at,
                     contributors.cntrb_full_name,
                     contributors.cntrb_login UNION ALL
                  SELECT
                     message.cntrb_id AS ID,
                     message.msg_timestamp AS created_at,
                     pull_requests.repo_id,
                     'pull_request_comment' :: TEXT AS ACTION,
                     contributors.cntrb_full_name AS full_name,
                     contributors.cntrb_login AS LOGIN 
                  FROM
                     augur_data.pull_requests,
                     augur_data.pull_request_message_ref,
                     (
                        ( augur_data.message LEFT JOIN augur_data.contributors ON ( ( contributors.cntrb_id = message.cntrb_id ) ) )
                        LEFT JOIN (
                        SELECT DISTINCT ON
                           ( contributors_1.cntrb_canonical ) contributors_1.cntrb_full_name,
                           contributors_1.cntrb_canonical AS canonical_email,
                           contributors_1.data_collection_date,
                           contributors_1.cntrb_id AS canonical_id 
                        FROM
                           augur_data.contributors contributors_1 
                        WHERE
                           ( ( contributors_1.cntrb_canonical ) :: TEXT = ( contributors_1.cntrb_email ) :: TEXT ) 
                        ORDER BY
                           contributors_1.cntrb_canonical 
                        ) canonical_full_names ON ( ( ( canonical_full_names.canonical_email ) :: TEXT = ( contributors.cntrb_canonical ) :: TEXT ) ) 
                     ) 
                  WHERE
                     ( ( pull_request_message_ref.pull_request_id = pull_requests.pull_request_id ) AND ( pull_request_message_ref.msg_id = message.msg_id ) ) 
                  GROUP BY
                     message.cntrb_id,
                     pull_requests.repo_id,
                     message.msg_timestamp,
                     contributors.cntrb_full_name,
                     contributors.cntrb_login UNION ALL
                  SELECT
                     issues.reporter_id AS ID,
                     message.msg_timestamp AS created_at,
                     issues.repo_id,
                     'issue_comment' :: TEXT AS ACTION,
                     contributors.cntrb_full_name AS full_name,
                     contributors.cntrb_login AS LOGIN 
                  FROM
                     augur_data.issues,
                     augur_data.issue_message_ref,
                     (
                        ( augur_data.message LEFT JOIN augur_data.contributors ON ( ( contributors.cntrb_id = message.cntrb_id ) ) )
                        LEFT JOIN (
                        SELECT DISTINCT ON
                           ( contributors_1.cntrb_canonical ) contributors_1.cntrb_full_name,
                           contributors_1.cntrb_canonical AS canonical_email,
                           contributors_1.data_collection_date,
                           contributors_1.cntrb_id AS canonical_id 
                        FROM
                           augur_data.contributors contributors_1 
                        WHERE
                           ( ( contributors_1.cntrb_canonical ) :: TEXT = ( contributors_1.cntrb_email ) :: TEXT ) 
                        ORDER BY
                           contributors_1.cntrb_canonical 
                        ) canonical_full_names ON ( ( ( canonical_full_names.canonical_email ) :: TEXT = ( contributors.cntrb_canonical ) :: TEXT ) ) 
                     ) 
                  WHERE
                     ( ( issue_message_ref.msg_id = message.msg_id ) AND ( issues.issue_id = issue_message_ref.issue_id ) AND ( issues.pull_request_id = NULL :: BIGINT ) ) 
                  GROUP BY
                     issues.reporter_id,
                     issues.repo_id,
                     message.msg_timestamp,
                     contributors.cntrb_full_name,
                     contributors.cntrb_login 
                  ) A,
                  augur_data.repo 
               WHERE
                  ( ( A.ID IS NOT NULL ) AND ( A.repo_id = repo.repo_id ) ) 
               GROUP BY
                  A.ID,
                  A.repo_id,
                  A.ACTION,
                  A.created_at,
                  repo.repo_name,
                  A.full_name,
                  A.LOGIN 
               ORDER BY
                  A.created_at DESC 
               ) b 
            ) x 
         ORDER BY
            x.created_at DESC;"""))
    else:
        
        conn = op.get_bind()

        conn.execute(text("""drop materialized view if exists augur_data.explorer_contributor_actions;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_entry_list;"""))
        conn.execute(text("""drop materialized view if exists augur_data.api_get_all_repo_prs;"""))
