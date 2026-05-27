"""rename schema

Revision ID: 43
Revises: 42
Create Date: 2026-05-27 15:28:12.439500

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '43'
down_revision = '42'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind() 
    conn.execute(text("ALTER SCHEMA augur_data RENAME TO collection_data;"))
    conn.execute(text("ALTER SCHEMA augur_operations RENAME TO collection_operations;"))

    op.create_table_comment(
        'repos_fetch_log',
        'For future use when we move all working tables to the collection_operations schema. ',
        existing_comment='For future use when we move all working tables to the augur_operations schema. ',
        schema='collection_operations'
    )
    op.create_table_comment(
        'worker_settings_facade',
        'For future use when we move all working tables to the collection_operations schema. ',
        existing_comment='For future use when we move all working tables to the augur_operations schema. ',
        schema='collection_operations'
    )
    op.create_table_comment(
        'working_commits',
        'For future use when we move all working tables to the collection_operations schema. ',
        existing_comment='For future use when we move all working tables to the augur_operations schema. ',
        schema='collection_operations'
    )



def downgrade() -> None:

    op.create_table_comment(
        'working_commits',
        'For future use when we move all working tables to the augur_operations schema. ',
        existing_comment='For future use when we move all working tables to the collection_operations schema. ',
        schema='collection_operations'
    )
    op.create_table_comment(
        'worker_settings_facade',
        'For future use when we move all working tables to the augur_operations schema. ',
        existing_comment='For future use when we move all working tables to the collection_operations schema. ',
        schema='collection_operations'
    )
    op.create_table_comment(
        'repos_fetch_log',
        'For future use when we move all working tables to the augur_operations schema. ',
        existing_comment='For future use when we move all working tables to the collection_operations schema. ',
        schema='collection_operations'
    )

    conn = op.get_bind() 
    conn.execute(text("ALTER SCHEMA collection_data RENAME TO augur_data;"))
    conn.execute(text("ALTER SCHEMA collection_operations RENAME TO augur_operations;"))