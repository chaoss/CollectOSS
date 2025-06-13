"""Fix OpenSSF Scorecard Unique Constraint

Revision ID: 34
Revises: 33
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
        'pr_files_repo_unq',
        'pull_request_files',
        schema='augur_data',
        type_='unique'
    )
    op.create_unique_constraint(
        'pr_files_repo_unq',
        'pull_request_files',
        ['repo_id', 'pull_request_id', 'pr_file_path'],
        schema='augur_data'
    )

def downgrade():
    op.drop_constraint(
        'pr_files_repo_unq',
        'pull_request_files',
        schema='augur_data',
        type_='unique'
    )
    