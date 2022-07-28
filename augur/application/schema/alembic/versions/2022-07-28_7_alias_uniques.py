"""alias uniques

Revision ID: 7
Revises: 6
Create Date: 2022-07-28 14:26:15.346751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7'
down_revision = '6'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(None, 'contributors_aliases', schema='augur_data', type_='unique')
    op.create_unique_constraint('contributor-alias-unique', 'contributors_aliases', ['alias_email'], schema='augur_data')


def downgrade():
    op.drop_constraint('contributor-alias-unique', 'contributors_aliases', schema='augur_data', type_='unique')
    op.create_unique_constraint(None, 'contributors_aliases', ['alias_email', 'canonical_email'], schema='augur_data', initially="DEFERRED", deferrable=True)
