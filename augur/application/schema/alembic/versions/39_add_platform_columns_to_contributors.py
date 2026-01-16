"""add platform data to contributors

Revision ID: 39
Revises: 38
Create Date: 2026-01-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '39'
down_revision = '38'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to augur_data.contributors
    op.add_column('contributors', sa.Column('platform', sa.String(), nullable=False, server_default='github'), schema='augur_data')
    op.add_column('contributors', sa.Column('platform_username', sa.String(), nullable=True), schema='augur_data')
    
    # Backfill platform_username from gh_login for the default 'github' platform entries
    # We use execute with text() for safe SQL execution
    connection = op.get_bind()
    connection.execute(text("UPDATE augur_data.contributors SET platform_username = gh_login WHERE platform = 'github'"))


def downgrade():
    op.drop_column('contributors', 'platform_username', schema='augur_data')
    op.drop_column('contributors', 'platform', schema='augur_data')
