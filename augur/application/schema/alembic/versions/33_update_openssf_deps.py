"""Fix OpenSSF Scorecard Unique Constraint

Revision ID: 33
Revises: 32
Create Date: 2025-06-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from augur.application.db import create_database_engine, get_database_string


# revision identifiers, used by Alembic.
revision = '33'
down_revision = '32'
branch_labels = None
depends_on = None
def upgrade():
    op.drop_constraint(
        'deps_scorecard_new_unique',
        'repo_deps_scorecard',
        schema='augur_data',
        type_='unique'
    )
    op.create_unique_constraint(
        'deps_scorecard_new_unique',
        'repo_deps_scorecard',
        ['repo_id', 'name', 'data_collection_date'],
        schema='augur_data'
    )

def downgrade():
    op.drop_constraint(
        'deps_scorecard_new_unique',
        'repo_deps_scorecard',
        schema='augur_data',
        type_='unique'
    )
    op.create_unique_constraint(
        'deps-scorecard-insert-unique',
        'repo_deps_scorecard',
        ['repo_id', 'name'],
        schema='augur_data'
    )