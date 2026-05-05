""" Updating materialized views and associated indices

Revision ID: 26
Revises: 25
Create Date: 2023-08-23 18:17:22.651191

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '26'
down_revision = '25'
branch_labels = None
depends_on = None


def upgrade():

    mview_keys_26()

def downgrade():

    upgrade=False

    mview_keys_26(upgrade)

def mview_keys_26(upgrade=True):

   if upgrade:
      conn = op.get_bind() 
      conn.execute(text("""
      drop materialized view if exists augur_data.explorer_pr_assignments; 
      drop materialized view if exists augur_data.explorer_user_repos; 
      drop materialized view if exists augur_data.explorer_pr_response_times;
      drop materialized view if exists augur_data.explorer_pr_response;  
      drop materialized view if exists augur_data.explorer_issue_assignments;"""))

      conn.execute(text("""
      create materialized view augur_data.explorer_pr_assignments as 
      SELECT
        pr.pull_request_id,
        pr.repo_id AS ID,
        pr.pr_created_at AS created,
        pr.pr_closed_at AS closed,
        pre.created_at AS assign_date,
        pre.ACTION AS assignment_action,
        pre.cntrb_id AS assignee,
        pre.node_id AS node_id 
      FROM
        (
          augur_data.pull_requests pr
          LEFT JOIN augur_data.pull_request_events pre ON (
            (
              ( pr.pull_request_id = pre.pull_request_id ) 
              AND (
                ( pre.ACTION ) :: TEXT = ANY ( ARRAY [ ( 'unassigned' :: CHARACTER VARYING ) :: TEXT, ( 'assigned' :: CHARACTER VARYING ) :: TEXT ] ) 
              ) 
            ) 
          ) 
        );"""))
      conn.execute(text("""
      create materialized view augur_data.explorer_pr_response as 
      SELECT pr.pull_request_id,
          pr.repo_id AS id,
          pr.pr_augur_contributor_id AS cntrb_id,
          m.msg_timestamp,
          m.msg_cntrb_id,
          pr.pr_created_at,
          pr.pr_closed_at
        FROM (augur_data.pull_requests pr
          LEFT JOIN ( SELECT prr.pull_request_id,
                  m_1.msg_timestamp,
                  m_1.cntrb_id AS msg_cntrb_id
                FROM augur_data.pull_request_review_message_ref prrmr,
                  augur_data.pull_requests pr_1,
                  augur_data.message m_1,
                  augur_data.pull_request_reviews prr
                WHERE ((prrmr.pr_review_id = prr.pr_review_id) AND (prrmr.msg_id = m_1.msg_id) AND (prr.pull_request_id = pr_1.pull_request_id))
              UNION
              SELECT prmr.pull_request_id,
                  m_1.msg_timestamp,
                  m_1.cntrb_id AS msg_cntrb_id
                FROM augur_data.pull_request_message_ref prmr,
                  augur_data.pull_requests pr_1,
                  augur_data.message m_1
                WHERE ((prmr.pull_request_id = pr_1.pull_request_id) AND (prmr.msg_id = m_1.msg_id))) m ON ((m.pull_request_id = pr.pull_request_id)));"""))
      


      conn.execute(text("""
      create materialized view augur_data.explorer_user_repos as 
      SELECT a.login_name,
          a.user_id,
          b.group_id,
          c.repo_id
        FROM augur_operations.users a,
          augur_operations.user_groups b,
          augur_operations.user_repos c
        WHERE ((a.user_id = b.user_id) AND (b.group_id = c.group_id))
        ORDER BY a.user_id;"""))

      conn.execute(text("""
      create materialized view augur_data.explorer_pr_response_times as 
      SELECT repo.repo_id,
          pull_requests.pr_src_id,
          repo.repo_name,
          pull_requests.pr_src_author_association,
          repo_groups.rg_name AS repo_group,
          pull_requests.pr_src_state,
          pull_requests.pr_merged_at,
          pull_requests.pr_created_at,
          pull_requests.pr_closed_at,
          date_part('year'::text, (pull_requests.pr_created_at)::date) AS created_year,
          date_part('month'::text, (pull_requests.pr_created_at)::date) AS created_month,
          date_part('year'::text, (pull_requests.pr_closed_at)::date) AS closed_year,
          date_part('month'::text, (pull_requests.pr_closed_at)::date) AS closed_month,
          base_labels.pr_src_meta_label,
          base_labels.pr_head_or_base,
          ((EXTRACT(epoch FROM pull_requests.pr_closed_at) - EXTRACT(epoch FROM pull_requests.pr_created_at)) / (3600)::numeric) AS hours_to_close,
          ((EXTRACT(epoch FROM pull_requests.pr_closed_at) - EXTRACT(epoch FROM pull_requests.pr_created_at)) / (86400)::numeric) AS days_to_close,
          ((EXTRACT(epoch FROM response_times.first_response_time) - EXTRACT(epoch FROM pull_requests.pr_created_at)) / (3600)::numeric) AS hours_to_first_response,
          ((EXTRACT(epoch FROM response_times.first_response_time) - EXTRACT(epoch FROM pull_requests.pr_created_at)) / (86400)::numeric) AS days_to_first_response,
          ((EXTRACT(epoch FROM response_times.last_response_time) - EXTRACT(epoch FROM pull_requests.pr_created_at)) / (3600)::numeric) AS hours_to_last_response,
          ((EXTRACT(epoch FROM response_times.last_response_time) - EXTRACT(epoch FROM pull_requests.pr_created_at)) / (86400)::numeric) AS days_to_last_response,
          response_times.first_response_time,
          response_times.last_response_time,
          response_times.average_time_between_responses,
          response_times.assigned_count,
          response_times.review_requested_count,
          response_times.labeled_count,
          response_times.subscribed_count,
          response_times.mentioned_count,
          response_times.referenced_count,
          response_times.closed_count,
          response_times.head_ref_force_pushed_count,
          response_times.merged_count,
          response_times.milestoned_count,
          response_times.unlabeled_count,
          response_times.head_ref_deleted_count,
          response_times.comment_count,
          master_merged_counts.lines_added,
          master_merged_counts.lines_removed,
          all_commit_counts.commit_count,
          master_merged_counts.file_count
        FROM augur_data.repo,
          augur_data.repo_groups,
          ((((augur_data.pull_requests
          LEFT JOIN ( SELECT pull_requests_1.pull_request_id,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'assigned'::text)) AS assigned_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'review_requested'::text)) AS review_requested_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'labeled'::text)) AS labeled_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'unlabeled'::text)) AS unlabeled_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'subscribed'::text)) AS subscribed_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'mentioned'::text)) AS mentioned_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'referenced'::text)) AS referenced_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'closed'::text)) AS closed_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'head_ref_force_pushed'::text)) AS head_ref_force_pushed_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'head_ref_deleted'::text)) AS head_ref_deleted_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'milestoned'::text)) AS milestoned_count,
                  count(*) FILTER (WHERE ((pull_request_events.action)::text = 'merged'::text)) AS merged_count,
                  min(message.msg_timestamp) AS first_response_time,
                  count(DISTINCT message.msg_timestamp) AS comment_count,
                  max(message.msg_timestamp) AS last_response_time,
                  ((max(message.msg_timestamp) - min(message.msg_timestamp)) / (count(DISTINCT message.msg_timestamp))::double precision) AS average_time_between_responses
                FROM augur_data.pull_request_events,
                  augur_data.pull_requests pull_requests_1,
                  augur_data.repo repo_1,
                  augur_data.pull_request_message_ref,
                  augur_data.message
                WHERE ((repo_1.repo_id = pull_requests_1.repo_id) AND (pull_requests_1.pull_request_id = pull_request_events.pull_request_id) AND (pull_requests_1.pull_request_id = pull_request_message_ref.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
                GROUP BY pull_requests_1.pull_request_id) response_times ON ((pull_requests.pull_request_id = response_times.pull_request_id)))
          LEFT JOIN ( SELECT pull_request_commits.pull_request_id,
                  count(DISTINCT pull_request_commits.pr_cmt_sha) AS commit_count
                FROM augur_data.pull_request_commits,
                  augur_data.pull_requests pull_requests_1,
                  augur_data.pull_request_meta
                WHERE ((pull_requests_1.pull_request_id = pull_request_commits.pull_request_id) AND (pull_requests_1.pull_request_id = pull_request_meta.pull_request_id) AND ((pull_request_commits.pr_cmt_sha)::text <> (pull_requests_1.pr_merge_commit_sha)::text) AND ((pull_request_commits.pr_cmt_sha)::text <> (pull_request_meta.pr_sha)::text))
                GROUP BY pull_request_commits.pull_request_id) all_commit_counts ON ((pull_requests.pull_request_id = all_commit_counts.pull_request_id)))
          LEFT JOIN ( SELECT max(pull_request_meta.pr_repo_meta_id) AS max,
                  pull_request_meta.pull_request_id,
                  pull_request_meta.pr_head_or_base,
                  pull_request_meta.pr_src_meta_label
                FROM augur_data.pull_requests pull_requests_1,
                  augur_data.pull_request_meta
                WHERE ((pull_requests_1.pull_request_id = pull_request_meta.pull_request_id) AND ((pull_request_meta.pr_head_or_base)::text = 'base'::text))
                GROUP BY pull_request_meta.pull_request_id, pull_request_meta.pr_head_or_base, pull_request_meta.pr_src_meta_label) base_labels ON ((base_labels.pull_request_id = all_commit_counts.pull_request_id)))
          LEFT JOIN ( SELECT sum(commits.cmt_added) AS lines_added,
                  sum(commits.cmt_removed) AS lines_removed,
                  pull_request_commits.pull_request_id,
                  count(DISTINCT commits.cmt_filename) AS file_count
                FROM augur_data.pull_request_commits,
                  augur_data.commits,
                  augur_data.pull_requests pull_requests_1,
                  augur_data.pull_request_meta
                WHERE (((commits.cmt_commit_hash)::text = (pull_request_commits.pr_cmt_sha)::text) AND (pull_requests_1.pull_request_id = pull_request_commits.pull_request_id) AND (pull_requests_1.pull_request_id = pull_request_meta.pull_request_id) AND (commits.repo_id = pull_requests_1.repo_id) AND ((commits.cmt_commit_hash)::text <> (pull_requests_1.pr_merge_commit_sha)::text) AND ((commits.cmt_commit_hash)::text <> (pull_request_meta.pr_sha)::text))
                GROUP BY pull_request_commits.pull_request_id) master_merged_counts ON ((base_labels.pull_request_id = master_merged_counts.pull_request_id)))
        WHERE ((repo.repo_group_id = repo_groups.repo_group_id) AND (repo.repo_id = pull_requests.repo_id))
        ORDER BY response_times.merged_count DESC;"""))

      conn.execute(text("""
      create materialized view augur_data.explorer_issue_assignments as 
      SELECT
      i.issue_id,
      i.repo_id AS ID,
      i.created_at AS created,
      i.closed_at AS closed,
      ie.created_at AS assign_date,
      ie.ACTION AS assignment_action,
      ie.cntrb_id AS assignee, 
      ie.node_id as node_id  
      FROM
        (
          augur_data.issues i
          LEFT JOIN augur_data.issue_events ie ON (
            (
              ( i.issue_id = ie.issue_id ) 
              AND (
                ( ie.ACTION ) :: TEXT = ANY ( ARRAY [ ( 'unassigned' :: CHARACTER VARYING ) :: TEXT, ( 'assigned' :: CHARACTER VARYING ) :: TEXT ] ) 
              ) 
            ) 
          ) 
        );"""))

      conn = op.get_bind() 
      conn.execute(text("""CREATE UNIQUE INDEX ON augur_data.explorer_user_repos(login_name,user_id,group_id,repo_id);"""))
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind() 
      conn.execute(text("""CREATE UNIQUE INDEX ON augur_data.explorer_pr_response_times(repo_id, pr_src_id, pr_src_meta_label);"""))
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind() 
      conn.execute(text("""CREATE UNIQUE INDEX ON augur_data.explorer_pr_assignments(pull_request_id, id, node_id);"""))
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind() 
      conn.execute(text("""CREATE UNIQUE INDEX ON augur_data.explorer_issue_assignments(issue_id, id, node_id);"""))
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind() 
      conn.execute(text("""CREATE UNIQUE INDEX ON augur_data.explorer_pr_response(pull_request_id, id, cntrb_id, msg_cntrb_id, msg_timestamp);"""))
      conn.execute(text("""COMMIT;"""))