""" Update messages unique

Revision ID: 27
Revises: 26
Create Date: 2024-03-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '27'
down_revision = '26'
branch_labels = None
depends_on = None


schema_name = 'augur_data'
table_name = "message"
constraint_name = "message-insert-unique"

def upgrade():
        
    op.drop_constraint(constraint_name, table_name, schema=schema_name,     type_='unique')

    op.create_unique_constraint(constraint_name, table_name, ['platform_msg_id', 'pltfrm_id'], schema=schema_name)

def downgrade():

    op.drop_constraint(constraint_name, table_name, schema=schema_name,     type_='unique')

    op.create_unique_constraint(constraint_name, table_name, ['platform_msg_id'], schema=schema_name)
