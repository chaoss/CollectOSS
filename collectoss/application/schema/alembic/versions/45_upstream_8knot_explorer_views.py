"""upstream 8Knot explorer materialized views

Revision ID: 45
Revises: 44
Create Date: 2026-08-04 00:00:00.000000

Adds the three file-level materialized views 8Knot depends on that were never
upstreamed -- explorer_repo_files, explorer_cntrb_per_file and explorer_pr_files,
which back 8Knot's codebase heatmaps -- and replaces explorer_contributor_actions
with the definition 8Knot deploys as of oss-aspen/8Knot#1116.

All four are dropped first if present. Deployments that created these views out
of band -- 8Knot's infra repo does -- would otherwise fail on "relation already
exists", and a hand-made copy is not guaranteed to match the definition here.

explorer_contributor_actions loses the `rank` window column and the `commit`
action branch. Consequences:
  * `rank` was the view's only candidate key, so its unique index is not
    recreated and refreshes can no longer run CONCURRENTLY -- they take an
    ACCESS EXCLUSIVE lock on the view for the duration of the rebuild.
  * A net-new btree on repo_id is added. The dropped unique index led with
    cntrb_id and never served repo_id lookups, which are the hot path for both
    8Knot and nadia_project_labeling_badge in collectoss/api/metrics/repo_meta.py.
  * That badge endpoint counts rows in this view, so repos whose contributors
    only ever committed (no issues, no PRs) now count as fewer contributors and
    may be bucketed lower.
  * created_at changes from `timestamp with time zone` to `timestamp without
    time zone`: commits.cmt_author_timestamp was the only timestamptz input to
    the UNION ALL and it set the resolved type. The remaining inputs are all
    naive UTC, so the instants are unchanged.

The three new views are created WITH NO DATA. Creating them WITH DATA would
materialize the pull_requests x pull_request_files x pull_request_reviews join
inside this migration's transaction, which is hours of held locks on a
production-sized database.

OPERATORS: an unpopulated materialized view raises "has not been populated" on
every read -- it does not return zero rows. Nothing can query these three views
until they are refreshed at least once. refresh_materialized_views is scheduled
via add_periodic_task, so its first run is one full
refresh_materialized_views_interval_in_days after worker startup (default 1;
instances that predate migration 25 sit at 7), and setting that interval to 0
disables the task entirely, leaving these views permanently unreadable. Unless
you are content to wait out an interval, refresh them once by hand right after
migrating:

    REFRESH MATERIALIZED VIEW data.explorer_repo_files WITH DATA;
    REFRESH MATERIALIZED VIEW data.explorer_cntrb_per_file WITH DATA;
    REFRESH MATERIALIZED VIEW data.explorer_pr_files WITH DATA;

explorer_contributor_actions is recreated WITH DATA instead, because it replaces
a populated view that repo_meta.py and 8Knot already read; leaving it empty
would break them for the same window. That does mean this migration holds a
transaction open for as long as that view takes to build -- plan a window.
"""
from alembic import op
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = '45'
down_revision = '44'
branch_labels = None
depends_on = None


EXPLORER_CONTRIBUTOR_ACTIONS = """\
SELECT
    a.cntrb_id,
    a.created_at,
    a.repo_id,
    a.action,
    a.repo_name,
    co.cntrb_login AS login
FROM (
    -- issues opened
    SELECT
        i.reporter_id                  AS cntrb_id,
        i.created_at,
        i.repo_id,
        'issue_opened'::text           AS action,
        r.repo_name
    FROM data.issues i
    JOIN data.repo r ON r.repo_id = i.repo_id
    WHERE i.pull_request IS NULL

    UNION ALL

    -- pull requests closed (not merged)
    SELECT
        pre.cntrb_id,
        pre.created_at,
        pr.repo_id,
        'pull_request_closed'::text    AS action,
        r.repo_name
    FROM data.pull_request_events pre
    JOIN data.pull_requests pr
        ON pr.pull_request_id = pre.pull_request_id
        AND pr.pr_merged_at IS NULL
    JOIN data.repo r ON r.repo_id = pr.repo_id
    WHERE pre.action = 'closed'

    UNION ALL

    -- pull requests merged
    SELECT
        pre.cntrb_id,
        pre.created_at,
        pr.repo_id,
        'pull_request_merged'::text    AS action,
        r.repo_name
    FROM data.pull_request_events pre
    JOIN data.pull_requests pr
        ON pr.pull_request_id = pre.pull_request_id
    JOIN data.repo r ON r.repo_id = pr.repo_id
    WHERE pre.action = 'merged'

    UNION ALL

    -- issues closed
    SELECT
        ie.cntrb_id,
        ie.created_at,
        i.repo_id,
        'issue_closed'::text           AS action,
        r.repo_name
    FROM data.issue_events ie
    JOIN data.issues i
        ON i.issue_id = ie.issue_id
        AND i.pull_request IS NULL
    JOIN data.repo r ON r.repo_id = i.repo_id
    WHERE ie.action = 'closed'

    UNION ALL

    -- pull request reviews
    SELECT
        prr.cntrb_id,
        prr.pr_review_submitted_at     AS created_at,
        pr.repo_id,
        ('pull_request_review_' || prr.pr_review_state::text) AS action,
        r.repo_name
    FROM data.pull_request_reviews prr
    JOIN data.pull_requests pr
        ON pr.pull_request_id = prr.pull_request_id
    JOIN data.repo r ON r.repo_id = pr.repo_id

    UNION ALL

    -- pull requests opened
    SELECT
        pr.pr_augur_contributor_id     AS cntrb_id,
        pr.pr_created_at               AS created_at,
        pr.repo_id,
        'pull_request_open'::text      AS action,
        r.repo_name
    FROM data.pull_requests pr
    JOIN data.repo r ON r.repo_id = pr.repo_id

    UNION ALL

    -- pull request comments
    SELECT
        m.cntrb_id,
        m.msg_timestamp                AS created_at,
        pr.repo_id,
        'pull_request_comment'::text   AS action,
        r.repo_name
    FROM data.pull_request_message_ref prmr
    JOIN data.pull_requests pr
        ON pr.pull_request_id = prmr.pull_request_id
    JOIN data.repo r ON r.repo_id = pr.repo_id
    JOIN data.message m ON m.msg_id = prmr.msg_id

    UNION ALL

    -- issue comments
    SELECT
        m.cntrb_id,
        m.msg_timestamp                AS created_at,
        i.repo_id,
        'issue_comment'::text          AS action,
        r.repo_name
    FROM data.issue_message_ref imr
    JOIN data.message m ON m.msg_id = imr.msg_id
    JOIN data.issues i
        ON i.issue_id = imr.issue_id
        AND i.pull_request IS NULL
        AND i.closed_at <> m.msg_timestamp
    JOIN data.repo r ON r.repo_id = i.repo_id
) a
LEFT JOIN data.contributors co ON co.cntrb_id = a.cntrb_id
ORDER BY a.created_at DESC"""

# The definition this migration replaces, restored verbatim by downgrade().
EXPLORER_CONTRIBUTOR_ACTIONS_PRE_45 = """\
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
           FROM (data.commits
             LEFT JOIN data.contributors ON (((contributors.cntrb_id)::text = (commits.cmt_ght_author_id)::text)))
          GROUP BY commits.cmt_commit_hash, commits.cmt_ght_author_id, commits.repo_id, commits.cmt_author_timestamp, 'commit'::text, contributors.cntrb_login
        UNION ALL
         SELECT issues.reporter_id AS id,
            issues.created_at,
            issues.repo_id,
            'issue_opened'::text AS action,
            contributors.cntrb_login AS login
           FROM (data.issues
             LEFT JOIN data.contributors ON ((contributors.cntrb_id = issues.reporter_id)))
          WHERE (issues.pull_request IS NULL)
        UNION ALL
         SELECT pull_request_events.cntrb_id AS id,
            pull_request_events.created_at,
            pull_requests.repo_id,
            'pull_request_closed'::text AS action,
            contributors.cntrb_login AS login
           FROM data.pull_requests,
            (data.pull_request_events
             LEFT JOIN data.contributors ON ((contributors.cntrb_id = pull_request_events.cntrb_id)))
          WHERE ((pull_requests.pull_request_id = pull_request_events.pull_request_id) AND (pull_requests.pr_merged_at IS NULL) AND ((pull_request_events.action)::text = 'closed'::text))
        UNION ALL
         SELECT pull_request_events.cntrb_id AS id,
            pull_request_events.created_at,
            pull_requests.repo_id,
            'pull_request_merged'::text AS action,
            contributors.cntrb_login AS login
           FROM data.pull_requests,
            (data.pull_request_events
             LEFT JOIN data.contributors ON ((contributors.cntrb_id = pull_request_events.cntrb_id)))
          WHERE ((pull_requests.pull_request_id = pull_request_events.pull_request_id) AND ((pull_request_events.action)::text = 'merged'::text))
        UNION ALL
         SELECT issue_events.cntrb_id AS id,
            issue_events.created_at,
            issues.repo_id,
            'issue_closed'::text AS action,
            contributors.cntrb_login AS login
           FROM data.issues,
            (data.issue_events
             LEFT JOIN data.contributors ON ((contributors.cntrb_id = issue_events.cntrb_id)))
          WHERE ((issues.issue_id = issue_events.issue_id) AND (issues.pull_request IS NULL) AND ((issue_events.action)::text = 'closed'::text))
        UNION ALL
         SELECT pull_request_reviews.cntrb_id AS id,
            pull_request_reviews.pr_review_submitted_at AS created_at,
            pull_requests.repo_id,
            ('pull_request_review_'::text || (pull_request_reviews.pr_review_state)::text) AS action,
            contributors.cntrb_login AS login
           FROM data.pull_requests,
            (data.pull_request_reviews
             LEFT JOIN data.contributors ON ((contributors.cntrb_id = pull_request_reviews.cntrb_id)))
          WHERE (pull_requests.pull_request_id = pull_request_reviews.pull_request_id)
        UNION ALL
         SELECT pull_requests.pr_augur_contributor_id AS id,
            pull_requests.pr_created_at AS created_at,
            pull_requests.repo_id,
            'pull_request_open'::text AS action,
            contributors.cntrb_login AS login
           FROM (data.pull_requests
             LEFT JOIN data.contributors ON ((pull_requests.pr_augur_contributor_id = contributors.cntrb_id)))
        UNION ALL
         SELECT message.cntrb_id AS id,
            message.msg_timestamp AS created_at,
            pull_requests.repo_id,
            'pull_request_comment'::text AS action,
            contributors.cntrb_login AS login
           FROM data.pull_requests,
            data.pull_request_message_ref,
            (data.message
             LEFT JOIN data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
          WHERE ((pull_request_message_ref.pull_request_id = pull_requests.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
        UNION ALL
         SELECT issues.reporter_id AS id,
            message.msg_timestamp AS created_at,
            issues.repo_id,
            'issue_comment'::text AS action,
            contributors.cntrb_login AS login
           FROM data.issues,
            data.issue_message_ref,
            (data.message
             LEFT JOIN data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
          WHERE ((issue_message_ref.msg_id = message.msg_id) AND (issues.issue_id = issue_message_ref.issue_id) AND (issues.closed_at <> message.msg_timestamp))) a,
    data.repo
  WHERE (a.repo_id = repo.repo_id)
  ORDER BY a.created_at DESC"""

EXPLORER_REPO_FILES = """\
SELECT
    rl.repo_id,
    r.repo_name,
    r.repo_path,
    rl.rl_analysis_date,
    rl.file_path,
    rl.file_name
FROM data.repo_labor rl
INNER JOIN data.repo r ON rl.repo_id = r.repo_id
WHERE (rl.repo_id, rl.rl_analysis_date) IN (
    SELECT DISTINCT ON (repo_id) repo_id, rl_analysis_date
    FROM data.repo_labor
    ORDER BY repo_id, rl_analysis_date DESC
)"""

EXPLORER_CNTRB_PER_FILE = """\
SELECT
    pr.repo_id,
    prf.pr_file_path AS file_path,
    string_agg(DISTINCT CAST(pr.pr_augur_contributor_id AS varchar(15)), ',') AS cntrb_ids,
    string_agg(DISTINCT CAST(prr.cntrb_id AS varchar(15)), ',') AS reviewer_ids
FROM data.pull_requests pr
INNER JOIN data.pull_request_files prf
    ON pr.pull_request_id = prf.pull_request_id
LEFT OUTER JOIN data.pull_request_reviews prr
    ON pr.pull_request_id = prr.pull_request_id
GROUP BY prf.pr_file_path, pr.repo_id"""

EXPLORER_PR_FILES = """\
SELECT
    prf.pr_file_path AS file_path,
    pr.pull_request_id,
    pr.repo_id
FROM data.pull_requests pr
INNER JOIN data.pull_request_files prf
    ON pr.pull_request_id = prf.pull_request_id"""


def upgrade():
    conn = op.get_bind()

    # --- explorer_contributor_actions: redefined ---------------------------
    # Dropping the view drops its indexes, including the unique index created
    # in migration 25 over the now-removed `rank` column.
    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_contributor_actions;"))
    conn.execute(sql_text(
        f"CREATE MATERIALIZED VIEW data.explorer_contributor_actions AS {EXPLORER_CONTRIBUTOR_ACTIONS};"
    ))
    conn.execute(sql_text(
        "CREATE INDEX explorer_contributor_actions_repo_id_idx "
        "ON data.explorer_contributor_actions (repo_id);"
    ))

    # --- explorer_repo_files ------------------------------------------------
    # Unique on (repo_id, file_path, file_name): repo_labor is unique on
    # (repo_id, rl_analysis_date, file_path, file_name) and the view pins one
    # rl_analysis_date per repo_id.
    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_repo_files;"))
    conn.execute(sql_text(
        f"CREATE MATERIALIZED VIEW data.explorer_repo_files AS {EXPLORER_REPO_FILES} WITH NO DATA;"
    ))
    conn.execute(sql_text(
        "CREATE UNIQUE INDEX explorer_repo_files_unique_idx "
        "ON data.explorer_repo_files (repo_id, file_path, file_name);"
    ))

    # --- explorer_cntrb_per_file --------------------------------------------
    # Unique on (repo_id, file_path) by construction: that is the GROUP BY.
    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_cntrb_per_file;"))
    conn.execute(sql_text(
        f"CREATE MATERIALIZED VIEW data.explorer_cntrb_per_file AS {EXPLORER_CNTRB_PER_FILE} WITH NO DATA;"
    ))
    conn.execute(sql_text(
        "CREATE UNIQUE INDEX explorer_cntrb_per_file_unique_idx "
        "ON data.explorer_cntrb_per_file (repo_id, file_path);"
    ))

    # --- explorer_pr_files --------------------------------------------------
    # Composite index on (repo_id, file_path), not a unique one. This view is
    # one row per pull_request_files row, so (repo_id, file_path) is not unique:
    # one file touched by two PRs in the same repo yields two rows. Adding
    # pull_request_id does not rescue it either -- repo_id here comes from
    # pull_requests, so the prfiles_unique constraint on
    # data.pull_request_files, which covers that table's own nullable repo_id,
    # does not carry over: two source rows differing only by repo_id (1 vs NULL)
    # are legal and collapse to duplicate view rows. Without a candidate key
    # this view cannot be refreshed CONCURRENTLY. The index still leads with
    # repo_id, so it serves the repo_id-only lookups 8Knot issues.
    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_pr_files;"))
    conn.execute(sql_text(
        f"CREATE MATERIALIZED VIEW data.explorer_pr_files AS {EXPLORER_PR_FILES} WITH NO DATA;"
    ))
    conn.execute(sql_text(
        "CREATE INDEX explorer_pr_files_repo_id_file_path_idx "
        "ON data.explorer_pr_files (repo_id, file_path);"
    ))


def downgrade():
    conn = op.get_bind()

    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_pr_files;"))
    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_cntrb_per_file;"))
    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_repo_files;"))

    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_contributor_actions;"))
    conn.execute(sql_text(
        f"CREATE MATERIALIZED VIEW data.explorer_contributor_actions AS "
        f"{EXPLORER_CONTRIBUTOR_ACTIONS_PRE_45};"
    ))
    conn.execute(sql_text(
        "CREATE UNIQUE INDEX ON data.explorer_contributor_actions "
        "(cntrb_id, created_at, repo_id, action, repo_name, login, rank);"
    ))
