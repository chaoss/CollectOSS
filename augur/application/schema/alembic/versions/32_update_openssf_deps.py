"""Update pr events unique

Revision ID: 31
Revises: 30
Create Date: 2025-03-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from augur.application.db import create_database_engine, get_database_string


# revision identifiers, used by Alembic.
revision = '32'
down_revision = '31'
branch_labels = None
depends_on = None
def upgrade():
    op.drop_constraint(
        'deps-scorecard-insert-unique',
        'repo_deps_scorecard',
        schema='augur_data',
        type_='unique'
    )

def downgrade():
    # You would need to know the columns involved in the original unique constraint to recreate it.
    # Example below assumes the columns were ('repo_id', 'scorecard_id')
    op.create_unique_constraint(
        'deps-scorecard-insert-unique',
        'repo_deps_scorecard',
        ['repo_id', 'scorecard_id'],
        schema='augur_data'
    )