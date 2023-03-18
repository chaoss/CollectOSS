"""traffic additions

Revision ID: 12
Revises: 11
Create Date: 2022-12-30 19:23:17.997570

"""
from alembic.autogenerate import renderers

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import Sequence

# revision identifiers, used by Alembic.
revision = '12'
down_revision = '11'
branch_labels = None
depends_on = None


def upgrade():

    add_repo_clone_data_table_1()

def downgrade():

    upgrade = False

    add_repo_clone_data_table_1(upgrade)
    

def add_repo_clone_data_table_1(upgrade = True):

    clone_sequence = Sequence("augur_data.repo_clones_data_id_seq")
    add_sequence_to_model(clone_sequence, **{'schema': None})

    @renderers.dispatch_for(CreateSequenceOp)
    def render_create_sequence(autogen_context, op):
        return "op.create_sequence(%r, **%r)" % (
            op.sequence_name,
            {"schema": op.schema}
        )


    @renderers.dispatch_for(DropSequenceOp)
    def render_drop_sequence(autogen_context, op):
        return "op.drop_sequence(%r, **%r)" % (
            op.sequence_name,
            {"schema": op.schema}
        ) 

    if upgrade:

        op.create_sequence('repo_clones_data_id_seq', **{'schema': 'augur_data'})
        op.create_table('repo_clones_data',
        sa.Column('repo_clone_data_id', sa.BigInteger(), server_default=sa.text("nextval('augur_data.repo_clones_data_id_seq'::regclass)"), nullable=False),
        sa.Column('repo_id', sa.BigInteger(), nullable=False),
        sa.Column('unique_clones', sa.BigInteger(), nullable=True),
        sa.Column('count_clones', sa.BigInteger(), nullable=True),
        sa.Column('clone_data_timestamp', postgresql.TIMESTAMP(precision=6), nullable=True),
        sa.ForeignKeyConstraint(['repo_id'], ['augur_data.repo.repo_id'], onupdate='CASCADE', ondelete='RESTRICT', initially='DEFERRED', deferrable=True),
        sa.PrimaryKeyConstraint('repo_clone_data_id'),
        schema='augur_data'
        )
        op.create_unique_constraint('repo_clone_unique', 'repo_clones_data', ['repo_id'])
        op.drop_constraint('user_repos_repo_id_fkey', 'user_repos', schema='augur_operations', type_='foreignkey')
        op.create_foreign_key(None, 'user_repos', 'repo', ['repo_id'], ['repo_id'], source_schema='augur_operations', referent_schema='augur_data')
    
    else:
        
        op.drop_constraint(None, 'user_repos', schema='augur_operations', type_='foreignkey')
        op.create_foreign_key('user_repos_repo_id_fkey', 'user_repos', 'repo', ['repo_id'], ['repo_id'], source_schema='augur_operations')
        op.drop_table('repo_clones_data', schema='augur_data')
        op.execute(DropSequence(Sequence('augur_data.repo_clones_data_id_seq')))
        add_sequence_to_model(clone_sequence, 'augur_data')
        op.drop_sequence('repo_clones_data_id_seq', **{'schema': 'augur_data'})

