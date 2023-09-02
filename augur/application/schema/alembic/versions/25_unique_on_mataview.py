""" THIS WILL TAKE LONGER ON A LARGE SET OF REPOSITORIES : a unique index on a materialized view allows it to be refreshed concurrently, preventing blocking behavior

Revision ID: 25
Revises: 24
Create Date: 2023-08-23 18:17:22.651191

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '25'
down_revision = '24'
branch_labels = None
depends_on = None


def upgrade():

    add_fix_keys_25()

def downgrade():

    upgrade=False

    add_fix_keys_25(upgrade)

def add_fix_keys_25(upgrade=True):

   if upgrade:

      conn = op.get_bind() 
      conn.execute(text("""CREATE UNIQUE INDEX ON augur_data.api_get_all_repo_prs(repo_id);"""))
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.api_get_all_repos_commits(repo_id); """)) 
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.api_get_all_repos_issues(repo_id); """)) 
      conn.execute(text("""COMMIT;"""))


      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.explorer_commits_and_committers_daily_count( repo_id, cmt_committer_date); """)) 
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.explorer_entry_list(repo_id); """)) 
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind()
      conn.execute(text("""
          drop MATERIALIZED VIEW if exists augur_data.explorer_libyear_all;
          drop MATERIALIZED VIEW if exists augur_data.explorer_libyear_detail;
          drop MATERIALIZED VIEW if exists augur_data.explorer_libyear_summary; 
          drop MATERIALIZED VIEW if exists augur_data.explorer_contributor_actions; 


            ----
            DROP MATERIALIZED VIEW if exists "augur_data"."augur_new_contributors";"""))

      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind()
      conn.execute(text(""" 
                create MATERIALIZED VIEW "augur_data"."augur_new_contributors"
                AS
                SELECT a.id AS cntrb_id,
                    a.created_at,
                    a.repo_id,
                    a.action,
                    repo.repo_name,
                    a.login,
                    row_number() OVER (PARTITION BY a.id, a.repo_id ORDER BY a.created_at DESC) AS rank
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
                  ORDER BY a.created_at DESC;

                ALTER MATERIALIZED VIEW "augur_data"."augur_new_contributors" OWNER TO "augur";

            ----
              create materialized view augur_data.explorer_contributor_actions as 
              SELECT a.id AS cntrb_id,
                  a.created_at,
                  a.repo_id,
                  a.action,
                  repo.repo_name,
                  a.login,
                  row_number() OVER (PARTITION BY a.id, a.repo_id ORDER BY a.created_at desc) AS rank
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
                ORDER BY a.created_at DESC;
                
                 update augur_operations.config set value='1' where setting_name = 'refresh_materialized_views_interval_in_days';"""))

      conn.execute(text("""COMMIT;"""))

      conn.execute(text(""" drop materialized view if exists augur_data.explorer_new_contributors;
                    create materialized view augur_data.explorer_new_contributors
                    AS
                    SELECT x.cntrb_id,
                        x.created_at,
                        x.month,
                        x.year,
                        x.repo_id,
                        x.repo_name,
                        x.full_name,
                        x.login,
                        x.rank
                       FROM ( SELECT b.cntrb_id,
                                b.created_at,
                                b.month,
                                b.year,
                                b.repo_id,
                                b.repo_name,
                                b.full_name,
                                b.login,
                                b.action,
                                b.rank
                               FROM ( SELECT a.id AS cntrb_id,
                                        a.created_at,
                                        date_part('month'::text, (a.created_at)::date) AS month,
                                        date_part('year'::text, (a.created_at)::date) AS year,
                                        a.repo_id,
                                        repo.repo_name,
                                        a.full_name,
                                        a.login,
                                        a.action,
                                        row_number() OVER (PARTITION BY a.id, a.repo_id ORDER BY a.created_at desc) AS rank
                                       FROM ( SELECT canonical_full_names.canonical_id AS id,
                                                issues.created_at,
                                                issues.repo_id,
                                                'issue_opened'::text AS action,
                                                contributors.cntrb_full_name AS full_name,
                                                contributors.cntrb_login AS login
                                               FROM ((augur_data.issues
                                                 LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issues.reporter_id)))
                                                 LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                                        contributors_1.cntrb_canonical AS canonical_email,
                                                        contributors_1.data_collection_date,
                                                        contributors_1.cntrb_id AS canonical_id
                                                       FROM augur_data.contributors contributors_1
                                                      WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                                      ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                              WHERE (issues.pull_request IS NULL)
                                              GROUP BY canonical_full_names.canonical_id, issues.repo_id, issues.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                                            UNION ALL
                                             SELECT canonical_full_names.canonical_id AS id,
                                                to_timestamp((commits.cmt_author_date)::text, 'YYYY-MM-DD'::text) AS created_at,
                                                commits.repo_id,
                                                'commit'::text AS action,
                                                contributors.cntrb_full_name AS full_name,
                                                contributors.cntrb_login AS login
                                               FROM ((augur_data.commits
                                                 LEFT JOIN augur_data.contributors ON (((contributors.cntrb_canonical)::text = (commits.cmt_author_email)::text)))
                                                 LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                                        contributors_1.cntrb_canonical AS canonical_email,
                                                        contributors_1.data_collection_date,
                                                        contributors_1.cntrb_id AS canonical_id
                                                       FROM augur_data.contributors contributors_1
                                                      WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                                      ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                              GROUP BY commits.repo_id, canonical_full_names.canonical_email, canonical_full_names.canonical_id, commits.cmt_author_date, contributors.cntrb_full_name, contributors.cntrb_login
                                            UNION ALL
                                             SELECT message.cntrb_id AS id,
                                                commit_comment_ref.created_at,
                                                commits.repo_id,
                                                'commit_comment'::text AS action,
                                                contributors.cntrb_full_name AS full_name,
                                                contributors.cntrb_login AS login
                                               FROM augur_data.commit_comment_ref,
                                                augur_data.commits,
                                                ((augur_data.message
                                                 LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                                 LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                                        contributors_1.cntrb_canonical AS canonical_email,
                                                        contributors_1.data_collection_date,
                                                        contributors_1.cntrb_id AS canonical_id
                                                       FROM augur_data.contributors contributors_1
                                                      WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                                      ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                              WHERE ((commits.cmt_id = commit_comment_ref.cmt_id) AND (commit_comment_ref.msg_id = message.msg_id))
                                              GROUP BY message.cntrb_id, commits.repo_id, commit_comment_ref.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                                            UNION ALL
                                             SELECT issue_events.cntrb_id AS id,
                                                issue_events.created_at,
                                                issues.repo_id,
                                                'issue_closed'::text AS action,
                                                contributors.cntrb_full_name AS full_name,
                                                contributors.cntrb_login AS login
                                               FROM augur_data.issues,
                                                ((augur_data.issue_events
                                                 LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issue_events.cntrb_id)))
                                                 LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                                        contributors_1.cntrb_canonical AS canonical_email,
                                                        contributors_1.data_collection_date,
                                                        contributors_1.cntrb_id AS canonical_id
                                                       FROM augur_data.contributors contributors_1
                                                      WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                                      ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                              WHERE ((issues.issue_id = issue_events.issue_id) AND (issues.pull_request IS NULL) AND (issue_events.cntrb_id IS NOT NULL) AND ((issue_events.action)::text = 'closed'::text))
                                              GROUP BY issue_events.cntrb_id, issues.repo_id, issue_events.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                                            UNION ALL
                                             SELECT pull_requests.pr_augur_contributor_id AS id,
                                                pull_requests.pr_created_at AS created_at,
                                                pull_requests.repo_id,
                                                'open_pull_request'::text AS action,
                                                contributors.cntrb_full_name AS full_name,
                                                contributors.cntrb_login AS login
                                               FROM ((augur_data.pull_requests
                                                 LEFT JOIN augur_data.contributors ON ((pull_requests.pr_augur_contributor_id = contributors.cntrb_id)))
                                                 LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                                        contributors_1.cntrb_canonical AS canonical_email,
                                                        contributors_1.data_collection_date,
                                                        contributors_1.cntrb_id AS canonical_id
                                                       FROM augur_data.contributors contributors_1
                                                      WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                                      ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                              GROUP BY pull_requests.pr_augur_contributor_id, pull_requests.repo_id, pull_requests.pr_created_at, contributors.cntrb_full_name, contributors.cntrb_login
                                            UNION ALL
                                             SELECT message.cntrb_id AS id,
                                                message.msg_timestamp AS created_at,
                                                pull_requests.repo_id,
                                                'pull_request_comment'::text AS action,
                                                contributors.cntrb_full_name AS full_name,
                                                contributors.cntrb_login AS login
                                               FROM augur_data.pull_requests,
                                                augur_data.pull_request_message_ref,
                                                ((augur_data.message
                                                 LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                                 LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                                        contributors_1.cntrb_canonical AS canonical_email,
                                                        contributors_1.data_collection_date,
                                                        contributors_1.cntrb_id AS canonical_id
                                                       FROM augur_data.contributors contributors_1
                                                      WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                                      ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                              WHERE ((pull_request_message_ref.pull_request_id = pull_requests.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
                                              GROUP BY message.cntrb_id, pull_requests.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login
                                            UNION ALL
                                             SELECT issues.reporter_id AS id,
                                                message.msg_timestamp AS created_at,
                                                issues.repo_id,
                                                'issue_comment'::text AS action,
                                                contributors.cntrb_full_name AS full_name,
                                                contributors.cntrb_login AS login
                                               FROM augur_data.issues,
                                                augur_data.issue_message_ref,
                                                ((augur_data.message
                                                 LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                                 LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                                        contributors_1.cntrb_canonical AS canonical_email,
                                                        contributors_1.data_collection_date,
                                                        contributors_1.cntrb_id AS canonical_id
                                                       FROM augur_data.contributors contributors_1
                                                      WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                                      ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                              WHERE ((issue_message_ref.msg_id = message.msg_id) AND (issues.issue_id = issue_message_ref.issue_id) AND (issues.pull_request_id = NULL::bigint))
                                              GROUP BY issues.reporter_id, issues.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login) a,
                                        augur_data.repo
                                      WHERE ((a.id IS NOT NULL) AND (a.repo_id = repo.repo_id))
                                      GROUP BY a.id, a.repo_id, a.action, a.created_at, repo.repo_name, a.full_name, a.login
                                      ORDER BY a.id) b
                              WHERE (b.rank = ANY (ARRAY[(1)::bigint, (2)::bigint, (3)::bigint, (4)::bigint, (5)::bigint, (6)::bigint, (7)::bigint]))) x;

                    ALTER MATERIALIZED VIEW augur_data.explorer_new_contributors OWNER TO augur;"""))
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.augur_new_contributors( cntrb_id, created_at, repo_id, repo_name, login, rank); """)) 
      conn.execute(text("""COMMIT;"""))


      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.explorer_contributor_actions(cntrb_id,created_at,repo_id, action, repo_name,login, rank); """)) 
      conn.execute(text("""COMMIT;"""))

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.explorer_new_contributors(cntrb_id, created_at, month, year, repo_id, full_name, repo_name, login, rank); """)) 
      conn.execute(text("""COMMIT;"""))

