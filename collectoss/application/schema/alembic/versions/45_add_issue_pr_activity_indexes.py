"""add issue and pull request activity indexes

Revision ID: 45
Revises: 44

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '45'
down_revision = '44'
branch_labels = None
depends_on = None


def upgrade():
    # Concurrent builds keep these tables writable during collection.
    with op.get_context().autocommit_block():
        op.create_index(
            'issues_idx_repo_id_updated_at', 'issues', ['repo_id', 'updated_at'],
            schema='data', postgresql_concurrently=True,
        )
        op.create_index(
            'issues_idx_repo_id_created_at', 'issues', ['repo_id', 'created_at'],
            schema='data', postgresql_concurrently=True,
        )
        op.create_index(
            'pull_requests_idx_repo_id_pr_updated_at', 'pull_requests',
            ['repo_id', 'pr_updated_at'],
            schema='data', postgresql_concurrently=True,
        )
        op.create_index(
            'pull_requests_idx_repo_id_pr_created_at', 'pull_requests',
            ['repo_id', 'pr_created_at'],
            schema='data', postgresql_concurrently=True,
        )


def downgrade():
    with op.get_context().autocommit_block():
        op.drop_index(
            'pull_requests_idx_repo_id_pr_created_at', table_name='pull_requests',
            schema='data', postgresql_concurrently=True,
        )
        op.drop_index(
            'pull_requests_idx_repo_id_pr_updated_at', table_name='pull_requests',
            schema='data', postgresql_concurrently=True,
        )
        op.drop_index(
            'issues_idx_repo_id_created_at', table_name='issues',
            schema='data', postgresql_concurrently=True,
        )
        op.drop_index(
            'issues_idx_repo_id_updated_at', table_name='issues',
            schema='data', postgresql_concurrently=True,
        )
