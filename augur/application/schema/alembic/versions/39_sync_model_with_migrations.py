"""sync model with migrations

Revision ID: 39
Revises: 38
Create Date: 2026-02-04 15:57:55.645448

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '39'
down_revision = '38'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    # the db init script added in #3351 includes this table in the public schema for some reason
    # databases created after that pr was merged will have this extraneous table, so we should drop it.
    if "test" in tables: 
        op.drop_table('test')
    op.create_foreign_key('fk_commits_contributors_3', 'commits', 'contributors', ['cmt_author_platform_username'], ['cntrb_login'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE', initially='DEFERRED', deferrable=True)


def downgrade():
    # we intentionally dont drop the foreign key here because doing so will cause augur not to work (im fairly sure).
    # This foreign key is actively used in many queries and im not sure how the prior migrations managed to not break stuff
    pass
