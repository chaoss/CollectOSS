"""add task management schema

Revision ID: 39
Revises: 38
Create Date: 2026-02-04 07:49:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '39'
down_revision = '38'
branch_labels = None
depends_on = None


def upgrade():
    # Create ENUM types
    op.execute("CREATE TYPE augur_operations.task_type AS ENUM ('core', 'secondary', 'facade')")
    op.execute("CREATE TYPE augur_operations.origin_type AS ENUM ('automation', 'manual')")
    op.execute("CREATE TYPE augur_operations.collection_type AS ENUM ('full', 'incremental')")
    op.execute("CREATE TYPE augur_operations.collection_state AS ENUM ('Collecting', 'Failed', 'Complete')")
    op.execute("CREATE TYPE augur_operations.task_run_state AS ENUM ('Pending', 'Queued', 'Collecting', 'Failed', 'Complete')")
    
    # 1. Workflows table
    op.create_table('workflows',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('created_on', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        schema='augur_operations'
    )
    
    # 2. Workflow Tasks table
    op.create_table('workflow_tasks',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.Text(), nullable=False),
        sa.Column('task_type', postgresql.ENUM('core', 'secondary', 'facade', name='task_type', schema='augur_operations', create_type=False), nullable=False),
        sa.ForeignKeyConstraint(['workflow_id'], ['augur_operations.workflows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workflow_id', 'task_name'),
        schema='augur_operations'
    )
    
    # 3. Workflow Dependencies table
    op.create_table('workflow_dependencies',
        sa.Column('workflow_task_id', sa.Integer(), nullable=False),
        sa.Column('depends_on_workflow_task_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['workflow_task_id'], ['augur_operations.workflow_tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['depends_on_workflow_task_id'], ['augur_operations.workflow_tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('workflow_task_id', 'depends_on_workflow_task_id'),
        sa.CheckConstraint('workflow_task_id <> depends_on_workflow_task_id'),
        schema='augur_operations'
    )
    
    # 4. Repo Collections table
    op.create_table('repo_collections',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('repo_id', sa.BigInteger(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('origin', postgresql.ENUM('automation', 'manual', name='origin_type', schema='augur_operations', create_type=False), nullable=False),
        sa.Column('collection_type', postgresql.ENUM('full', 'incremental', name='collection_type', schema='augur_operations', create_type=False), nullable=False, server_default='full'),
        sa.Column('is_new_repo', sa.Boolean(), nullable=False, server_default='FALSE'),
        sa.Column('started_on', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('completed_on', sa.TIMESTAMP(), nullable=True),
        sa.Column('state', postgresql.ENUM('Collecting', 'Failed', 'Complete', name='collection_state', schema='augur_operations', create_type=False), nullable=False, server_default='Collecting'),
        sa.ForeignKeyConstraint(['repo_id'], ['augur_data.repo.repo_id']),
        sa.ForeignKeyConstraint(['workflow_id'], ['augur_operations.workflows.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='augur_operations'
    )
    
    # 5. Task Runs table
    op.create_table('task_runs',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('collection_record_id', sa.Integer(), nullable=False),
        sa.Column('workflow_task_id', sa.Integer(), nullable=False),
        sa.Column('restarted', sa.Boolean(), nullable=False, server_default='FALSE'),
        sa.Column('start_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('state', postgresql.ENUM('Pending', 'Queued', 'Collecting', 'Failed', 'Complete', name='task_run_state', schema='augur_operations', create_type=False), nullable=False, server_default='Pending'),
        sa.Column('stacktrace', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['collection_record_id'], ['augur_operations.repo_collections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workflow_task_id'], ['augur_operations.workflow_tasks.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('collection_record_id', 'workflow_task_id'),
        schema='augur_operations'
    )
    
    # 6. Repo Collection Settings table
    op.create_table('repo_collection_settings',
        sa.Column('repo_id', sa.BigInteger(), nullable=False),
        sa.Column('force_full_collection', sa.Boolean(), nullable=False, server_default='FALSE'),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('repo_id'),
        schema='augur_operations'
    )
    
    # Create indexes
    op.create_index('idx_workflow_tasks_workflow', 'workflow_tasks', ['workflow_id'], schema='augur_operations')
    op.create_index('idx_dependencies_task', 'workflow_dependencies', ['workflow_task_id'], schema='augur_operations')
    op.create_index('idx_dependencies_depends_on', 'workflow_dependencies', ['depends_on_workflow_task_id'], schema='augur_operations')
    op.create_index('idx_repo_collections_repo', 'repo_collections', ['repo_id'], schema='augur_operations')
    op.create_index('idx_repo_collection_settings_force_full', 'repo_collection_settings', ['force_full_collection'], 
                    schema='augur_operations', postgresql_where=sa.text('force_full_collection = TRUE'))
    op.create_index('idx_task_runs_collection', 'task_runs', ['collection_record_id'], schema='augur_operations')
    op.create_index('idx_task_runs_state', 'task_runs', ['state'], schema='augur_operations')


def downgrade():
    # Drop indexes
    op.drop_index('idx_task_runs_state', table_name='task_runs', schema='augur_operations')
    op.drop_index('idx_task_runs_collection', table_name='task_runs', schema='augur_operations')
    op.drop_index('idx_repo_collection_settings_force_full', table_name='repo_collection_settings', schema='augur_operations')
    op.drop_index('idx_repo_collections_repo', table_name='repo_collections', schema='augur_operations')
    op.drop_index('idx_dependencies_depends_on', table_name='workflow_dependencies', schema='augur_operations')
    op.drop_index('idx_dependencies_task', table_name='workflow_dependencies', schema='augur_operations')
    op.drop_index('idx_workflow_tasks_workflow', table_name='workflow_tasks', schema='augur_operations')
    
    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_table('repo_collection_settings', schema='augur_operations')
    op.drop_table('task_runs', schema='augur_operations')
    op.drop_table('repo_collections', schema='augur_operations')
    op.drop_table('workflow_dependencies', schema='augur_operations')
    op.drop_table('workflow_tasks', schema='augur_operations')
    op.drop_table('workflows', schema='augur_operations')
    
    # Drop ENUM types
    op.execute('DROP TYPE augur_operations.task_run_state')
    op.execute('DROP TYPE augur_operations.collection_state')
    op.execute('DROP TYPE augur_operations.collection_type')
    op.execute('DROP TYPE augur_operations.origin_type')
    op.execute('DROP TYPE augur_operations.task_type')
