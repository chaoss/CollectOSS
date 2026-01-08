"""Augur New Changes

Revision ID: 4
Revises: 3
Create Date: 2023-01-24 09:17:31.706564

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text
from augur.tasks.util.AugurUUID import AugurUUID, GithubUUID, UnresolvableUUID


# revision identifiers, used by Alembic.
revision = '4'
down_revision = '3'
branch_labels = None
depends_on = None


def upgrade():

    add_materialized_views_15()

def downgrade():

    upgrade=False

    add_materialized_views_15(upgrade)

def add_materialized_views_15(upgrade=True):

    if upgrade:
        conn = op.get_bind()
        conn.execute(text("""
        drop materialized view if exists augur_data.explorer_commits_and_committers_daily_count; 
        drop materialized view if exists augur_data.api_get_all_repos_commits; 
        drop materialized view if exists augur_data.api_get_all_repos_issues; 
        drop materialized view if exists augur_data.augur_new_contributors; 
        drop materialized view if exists augur_data.explorer_contributor_actions; 
        drop materialized view if exists augur_data.explorer_entry_list; 
        drop materialized view if exists augur_data.explorer_libyear_all; 
        drop materialized view if exists augur_data.explorer_libyear_detail; 
        drop materialized view if exists augur_data.explorer_new_contributors;
        drop materialized view if exists augur_data.api_get_all_repo_prs;
        drop materialized view if exists augur_data.explorer_libyear_summary;"""))

        conn.execute(text("""
        create materialized view augur_data.api_get_all_repo_prs as 
        SELECT pull_requests.repo_id,
        count(*) AS pull_requests_all_time
        FROM augur_data.pull_requests
        GROUP BY pull_requests.repo_id;"""))

        conn.execute(text("""
        create materialized view augur_data.explorer_entry_list as

        SELECT DISTINCT r.repo_git,
            r.repo_id,
            r.repo_name,
            rg.rg_name
           FROM (augur_data.repo r
             JOIN augur_data.repo_groups rg ON ((rg.repo_group_id = r.repo_group_id)))
          ORDER BY rg.rg_name;"""))

        conn.execute(text("""
        create materialized view augur_data.explorer_commits_and_committers_daily_count as
        SELECT repo.repo_id,
            repo.repo_name,
            commits.cmt_committer_date,
            count(commits.cmt_id) AS num_of_commits,
            count(DISTINCT commits.cmt_committer_raw_email) AS num_of_unique_committers
        FROM (augur_data.commits
            LEFT JOIN augur_data.repo ON ((repo.repo_id = commits.repo_id)))
        GROUP BY repo.repo_id, repo.repo_name, commits.cmt_committer_date
        ORDER BY repo.repo_id, commits.cmt_committer_date;"""))

        conn.execute(text("""

        create materialized view augur_data.api_get_all_repos_commits as
        SELECT commits.repo_id,
            count(DISTINCT commits.cmt_commit_hash) AS commits_all_time
        FROM augur_data.commits
        GROUP BY commits.repo_id;"""))


        conn.execute(text("""

        create materialized view augur_data.api_get_all_repos_issues as
        SELECT issues.repo_id,
            count(*) AS issues_all_time
        FROM augur_data.issues
        WHERE (issues.pull_request IS NULL)
        GROUP BY issues.repo_id; """))

        conn.execute(text("""

        create materialized view augur_data.explorer_libyear_all as 
        SELECT a.repo_id,
            a.repo_name,
            avg(b.libyear) AS avg_libyear,
            date_part('month'::text, (a.data_collection_date)::date) AS month,
            date_part('year'::text, (a.data_collection_date)::date) AS year
        FROM augur_data.repo a,
            augur_data.repo_deps_libyear b
        GROUP BY a.repo_id, a.repo_name, (date_part('month'::text, (a.data_collection_date)::date)), (date_part('year'::text, (a.data_collection_date)::date))
        ORDER BY (date_part('year'::text, (a.data_collection_date)::date)) DESC, (date_part('month'::text, (a.data_collection_date)::date)) DESC, (avg(b.libyear)) DESC; """))

        conn.execute(text("""

        create materialized view augur_data.explorer_libyear_summary as
        SELECT a.repo_id,
            a.repo_name,
            avg(b.libyear) AS avg_libyear,
            date_part('month'::text, (a.data_collection_date)::date) AS month,
            date_part('year'::text, (a.data_collection_date)::date) AS year
        FROM augur_data.repo a,
            augur_data.repo_deps_libyear b
        GROUP BY a.repo_id, a.repo_name, (date_part('month'::text, (a.data_collection_date)::date)), (date_part('year'::text, (a.data_collection_date)::date))
        ORDER BY (date_part('year'::text, (a.data_collection_date)::date)) DESC, (date_part('month'::text, (a.data_collection_date)::date)) DESC, (avg(b.libyear)) DESC;"""))

        conn.execute(text("""

        create materialized view augur_data.explorer_libyear_detail as 
        SELECT a.repo_id,
            a.repo_name,
            b.name,
            b.requirement,
            b.current_verion,
            b.latest_version,
            b.current_release_date,
            b.libyear,
            max(b.data_collection_date) AS max
        FROM augur_data.repo a,
            augur_data.repo_deps_libyear b
        GROUP BY a.repo_id, a.repo_name, b.name, b.requirement, b.current_verion, b.latest_version, b.current_release_date, b.libyear
        ORDER BY a.repo_id, b.requirement; """))

        conn.execute(text("""

        create materialized view augur_data.explorer_new_contributors as
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
                        rank() OVER (PARTITION BY a.id ORDER BY a.created_at) AS rank
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
            WHERE (b.rank = ANY (ARRAY[(1)::bigint, (2)::bigint, (3)::bigint, (4)::bigint, (5)::bigint, (6)::bigint, (7)::bigint]))) x;"""))

        conn.execute(text("""

    create  materialized view augur_data.augur_new_contributors as 
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
                        rank() OVER (PARTITION BY a.id ORDER BY a.created_at) AS rank
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
                                LEFT JOIN augur_data.contributors ON (((contributors.cntrb_email)::text = (commits.cmt_author_email)::text)))
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
            WHERE (b.rank = ANY (ARRAY[(1)::bigint, (2)::bigint, (3)::bigint, (4)::bigint, (5)::bigint, (6)::bigint, (7)::bigint]))) x; """))

        conn.execute(text("""
        create materialized view augur_data.explorer_contributor_actions as 
        SELECT x.cntrb_id,
            x.created_at,
            x.repo_id,
            x.login,
            x.action,
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
                            rank() OVER (PARTITION BY a.id, a.repo_id ORDER BY a.created_at) AS rank
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
                                        WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_canonical)::text)
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
                        ORDER BY a.created_at DESC) b) x
            ORDER BY x.created_at DESC; """))
    else:
        
        conn = op.get_bind()
        conn.execute(text("""drop materialized view if exists augur_data.explorer_commits_and_committers_daily_count;""")) 
        conn.execute(text("""drop materialized view if exists augur_data.api_get_all_repos_commits;"""))
        conn.execute(text("""drop materialized view if exists augur_data.api_get_all_repos_issues;"""))
        conn.execute(text("""drop materialized view if exists augur_data.augur_new_contributors;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_contributor_actions;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_entry_list;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_libyear_all;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_libyear_detail;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_libyear_summary;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_new_contributors;"""))
        conn.execute(text("""drop materialized view if exists augur_data.api_get_all_repo_prs;"""))
