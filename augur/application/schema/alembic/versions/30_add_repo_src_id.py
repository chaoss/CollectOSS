"""Add repo src id

Revision ID: 30
Revises: 29
Create Date: 2024-08-30

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '30'
down_revision = '29'
branch_labels = None
depends_on = None


def upgrade():
    # Check if repo_src_id column already exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('repo', schema='augur_data')]
    
    if 'repo_src_id' not in columns:
        op.add_column('repo', sa.Column('repo_src_id', sa.BigInteger(), nullable=True), schema='augur_data')
    
    # Check if constraint already exists
    constraints = [con['name'] for con in inspector.get_unique_constraints('repo', schema='augur_data')]
    if 'repo_src_id_unique' not in constraints:
        op.create_unique_constraint('repo_src_id_unique', 'repo', ['repo_src_id'], schema='augur_data')
    

def downgrade():
    op.drop_constraint('repo_src_id_unique', 'repo', schema='augur_data', type_='unique')
    op.drop_column('repo', 'repo_src_id', schema='augur_data')
