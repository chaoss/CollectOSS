"""Fix Keys and materialized view

Revision ID: 22
Revises: 21
Create Date: 2023-08-23 18:17:22.651191

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '22'
down_revision = '21'
branch_labels = None
depends_on = None


def upgrade():

    add_fix_keys_22()

def downgrade():

    upgrade=False

    add_fix_keys_22(upgrade)

def add_fix_keys_22(upgrade=True):

   if upgrade:

      conn = op.get_bind() 
      conn.execute(text(""" 
         alter TABLE
         augur_data.commits DROP CONSTRAINT if exists fk_commits_contributors_3, 
         DROP CONSTRAINT if exists fk_commits_contributors_4; 
         alter TABLE augur_data.contributors 
            DROP CONSTRAINT if exists "GH-UNIQUE-C", 
            DROP CONSTRAINT if exists
            "GL-cntrb-LOGIN-UNIQUE";"""))

      conn = op.get_bind()
      conn.execute(text("""
        drop materialized view if exists augur_data.explorer_contributor_actions; """)) 

      conn = op.get_bind()
      conn.execute(text("""
        create materialized view augur_data.explorer_contributor_actions as 
        SELECT a.created_at,
                a.repo_id,
                a.action,
                repo.repo_name,
                a.login,
                dense_rank() OVER (PARTITION BY a.id, a.repo_id ORDER BY a.created_at) AS rank
               FROM ( SELECT commits.cmt_ght_author_id AS id,
                        commits.cmt_author_timestamp AS created_at,
                        commits.repo_id,
                        'commit'::text AS action,
                        contributors.cntrb_login AS login
                       FROM (augur_data.commits
                         LEFT JOIN augur_data.contributors ON (((contributors.cntrb_id)::text = (commits.cmt_ght_author_id)::text)))
                      GROUP BY commits.cmt_commit_hash, commits.cmt_ght_author_id, commits.repo_id, commits.cmt_author_timestamp, 'commit'::text, contributors.cntrb_login
                    UNION ALL
                     SELECT issues.reporter_id AS id,
                        issues.created_at,
                        issues.repo_id,
                        'issue_opened'::text AS action,
                        contributors.cntrb_login AS login
                       FROM (augur_data.issues
                         LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issues.reporter_id)))
                      WHERE (issues.pull_request IS NULL)
                    UNION ALL
                     SELECT pull_request_events.cntrb_id AS id,
                        pull_request_events.created_at,
                        pull_requests.repo_id,
                        'pull_request_closed'::text AS action,
                        contributors.cntrb_login AS login
                       FROM augur_data.pull_requests,
                        (augur_data.pull_request_events
                         LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = pull_request_events.cntrb_id)))
                      WHERE ((pull_requests.pull_request_id = pull_request_events.pull_request_id) AND (pull_requests.pr_merged_at IS NULL) AND ((pull_request_events.action)::text = 'closed'::text))
                    UNION ALL
                     SELECT pull_request_events.cntrb_id AS id,
                        pull_request_events.created_at,
                        pull_requests.repo_id,
                        'pull_request_merged'::text AS action,
                        contributors.cntrb_login AS login
                       FROM augur_data.pull_requests,
                        (augur_data.pull_request_events
                         LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = pull_request_events.cntrb_id)))
                      WHERE ((pull_requests.pull_request_id = pull_request_events.pull_request_id) AND ((pull_request_events.action)::text = 'merged'::text))
                    UNION ALL
                     SELECT issue_events.cntrb_id AS id,
                        issue_events.created_at,
                        issues.repo_id,
                        'issue_closed'::text AS action,
                        contributors.cntrb_login AS login
                       FROM augur_data.issues,
                        (augur_data.issue_events
                         LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issue_events.cntrb_id)))
                      WHERE ((issues.issue_id = issue_events.issue_id) AND (issues.pull_request IS NULL) AND ((issue_events.action)::text = 'closed'::text))
                    UNION ALL
                     SELECT pull_request_reviews.cntrb_id AS id,
                        pull_request_reviews.pr_review_submitted_at AS created_at,
                        pull_requests.repo_id,
                        ('pull_request_review_'::text || (pull_request_reviews.pr_review_state)::text) AS action,
                        contributors.cntrb_login AS login
                       FROM augur_data.pull_requests,
                        (augur_data.pull_request_reviews
                         LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = pull_request_reviews.cntrb_id)))
                      WHERE (pull_requests.pull_request_id = pull_request_reviews.pull_request_id)
                    UNION ALL
                     SELECT pull_requests.pr_augur_contributor_id AS id,
                        pull_requests.pr_created_at AS created_at,
                        pull_requests.repo_id,
                        'pull_request_open'::text AS action,
                        contributors.cntrb_login AS login
                       FROM (augur_data.pull_requests
                         LEFT JOIN augur_data.contributors ON ((pull_requests.pr_augur_contributor_id = contributors.cntrb_id)))
                    UNION ALL
                     SELECT message.cntrb_id AS id,
                        message.msg_timestamp AS created_at,
                        pull_requests.repo_id,
                        'pull_request_comment'::text AS action,
                        contributors.cntrb_login AS login
                       FROM augur_data.pull_requests,
                        augur_data.pull_request_message_ref,
                        (augur_data.message
                         LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                      WHERE ((pull_request_message_ref.pull_request_id = pull_requests.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
                    UNION ALL
                     SELECT issues.reporter_id AS id,
                        message.msg_timestamp AS created_at,
                        issues.repo_id,
                        'issue_comment'::text AS action,
                        contributors.cntrb_login AS login
                       FROM augur_data.issues,
                        augur_data.issue_message_ref,
                        (augur_data.message
                         LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                      WHERE ((issue_message_ref.msg_id = message.msg_id) AND (issues.issue_id = issue_message_ref.issue_id) AND (issues.closed_at <> message.msg_timestamp))) a,
                augur_data.repo
              WHERE (a.repo_id = repo.repo_id)
              ORDER BY a.created_at DESC"""))

