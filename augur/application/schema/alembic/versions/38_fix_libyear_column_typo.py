"""Fix typo in repo_deps_libyear column: current_verion -> current_version

Revision ID: 38
Revises: 37
Create Date: 2025-01-15

This migration fixes a typo in the repo_deps_libyear table where the column
'current_verion' was misspelled (missing 's'). The correct name should be
'current_version'.

Since PostgreSQL supports simple column renames via ALTER TABLE, no data
copying or temp tables are needed. However, we must drop and recreate the
materialized view 'explorer_libyear_detail' which references this column.
"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '38'
down_revision = '37'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Step 1: Drop the materialized view that references the column
    conn.execute(text("""
        DROP MATERIALIZED VIEW IF EXISTS augur_data.explorer_libyear_detail;
    """))

    # Step 2: Rename the column (simple metadata operation in PostgreSQL)
    conn.execute(text("""
        ALTER TABLE augur_data.repo_deps_libyear
        RENAME COLUMN current_verion TO current_version;
    """))

    # Step 3: Recreate the materialized view with the corrected column name
    conn.execute(text("""
        CREATE MATERIALIZED VIEW augur_data.explorer_libyear_detail AS
        SELECT a.repo_id,
            a.repo_name,
            b.name,
            b.requirement,
            b.current_version,
            b.latest_version,
            b.current_release_date,
            b.libyear,
            max(b.data_collection_date) AS max
        FROM augur_data.repo a,
            augur_data.repo_deps_libyear b
        WHERE a.repo_id = b.repo_id
        GROUP BY a.repo_id, a.repo_name, b.name, b.requirement, b.current_version,
                 b.latest_version, b.current_release_date, b.libyear
        ORDER BY a.repo_id, b.requirement;
    """))


def downgrade():
    conn = op.get_bind()

    # Step 1: Drop the materialized view
    conn.execute(text("""
        DROP MATERIALIZED VIEW IF EXISTS augur_data.explorer_libyear_detail;
    """))

    # Step 2: Rename the column back to the typo version
    conn.execute(text("""
        ALTER TABLE augur_data.repo_deps_libyear
        RENAME COLUMN current_version TO current_verion;
    """))

    # Step 3: Recreate the materialized view with the original (typo) column name
    conn.execute(text("""
        CREATE MATERIALIZED VIEW augur_data.explorer_libyear_detail AS
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
        WHERE a.repo_id = b.repo_id
        GROUP BY a.repo_id, a.repo_name, b.name, b.requirement, b.current_verion,
                 b.latest_version, b.current_release_date, b.libyear
        ORDER BY a.repo_id, b.requirement;
    """))
