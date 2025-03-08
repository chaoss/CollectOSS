"""Update pr events unique

Revision ID: 31
Revises: 30
Create Date: 2025-03-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '30'
down_revision = '29'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind() 
    conn.execute(text("""
        UPDATE pull_request_events
        SET issue_event_src_id = substring(node_url FROM '.*/([0-9]+)$')::BIGINT;
    """))

    op.create_unique_constraint('pr_events_repo_id_event_src_id_unique', 'pull_request_events', ['repo_id', 'issue_event_src_id'], schema='augur_data')
    

def downgrade():
    op.drop_constraint('pr_events_repo_id_event_src_id_unique', 'pull_request_events', schema='augur_data', type_='unique')

    conn = op.get_bind() 
    conn.execute(text("""
        UPDATE pull_request_events
        SET issue_event_src_id = pr_platform_event_id;
    """))

