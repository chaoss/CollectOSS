"""upstream 8Knot explorer file materialized views

Revision ID: 45
Revises: 44
Create Date: 2026-08-04 00:00:00.000000

Adds the three file-level materialized views 8Knot depends on that were never
upstreamed: explorer_repo_files, explorer_cntrb_per_file and explorer_pr_files.
They back 8Knot's codebase heatmaps. Nothing in CollectOSS reads them today, so
this migration is purely additive.

All three are dropped first if present. Deployments that created these views out
of band -- 8Knot's infra repo does -- would otherwise fail on "relation already
exists", and a hand-made copy is not guaranteed to match the definition here.

The views are created WITH NO DATA. Creating them WITH DATA would materialize
the pull_requests x pull_request_files x pull_request_reviews join inside this
migration's transaction, which is hours of held locks on a production-sized
database.

OPERATORS: an unpopulated materialized view raises "has not been populated" on
every read -- it does not return zero rows. Nothing can query these views until
they are refreshed at least once. refresh_materialized_views is scheduled via
add_periodic_task, so its first run is one full
refresh_materialized_views_interval_in_days after worker startup (default 1;
instances that predate migration 25 sit at 7), and setting that interval to 0
disables the task entirely, leaving these views permanently unreadable. Unless
you are content to wait out an interval, refresh them once by hand right after
migrating:

    REFRESH MATERIALIZED VIEW data.explorer_repo_files WITH DATA;
    REFRESH MATERIALIZED VIEW data.explorer_cntrb_per_file WITH DATA;
    REFRESH MATERIALIZED VIEW data.explorer_pr_files WITH DATA;
"""
from alembic import op
from sqlalchemy import text as sql_text

# revision identifiers, used by Alembic.
revision = '45'
down_revision = '44'
branch_labels = None
depends_on = None


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
    # No unique index: repo_id here comes from pull_requests, so the
    # prfiles_unique constraint on data.pull_request_files does not carry over
    # and duplicate rows are possible on databases with legacy PR-file data.
    # Without a candidate key this view cannot be refreshed CONCURRENTLY.
    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_pr_files;"))
    conn.execute(sql_text(
        f"CREATE MATERIALIZED VIEW data.explorer_pr_files AS {EXPLORER_PR_FILES} WITH NO DATA;"
    ))
    conn.execute(sql_text(
        "CREATE INDEX explorer_pr_files_repo_id_idx ON data.explorer_pr_files (repo_id);"
    ))


def downgrade():
    conn = op.get_bind()

    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_pr_files;"))
    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_cntrb_per_file;"))
    conn.execute(sql_text("DROP MATERIALIZED VIEW IF EXISTS data.explorer_repo_files;"))
