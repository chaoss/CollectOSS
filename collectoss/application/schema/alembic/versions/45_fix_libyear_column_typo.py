"""Fix typo in repo_deps_libyear column: current_verion -> current_version

Revision ID: 45
Revises: 44
Create Date: 2025-12-15
"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '45'
down_revision = '44'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text("""
        ALTER TABLE data.repo_deps_libyear
        RENAME COLUMN current_verion TO current_version;
    """))


def downgrade():
    conn = op.get_bind()
    conn.execute(text("""
        ALTER TABLE data.repo_deps_libyear
        RENAME COLUMN current_version TO current_verion;
    """))
