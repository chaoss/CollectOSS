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



def downgrade() -> None:
    conn = op.get_bind() 
    conn.execute(text("ALTER SCHEMA collection_data RENAME TO augur_data;"))
    conn.execute(text("ALTER SCHEMA collection_operations RENAME TO augur_operations;"))