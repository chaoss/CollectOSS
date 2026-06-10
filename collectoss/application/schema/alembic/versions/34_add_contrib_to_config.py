"""Add Facade contributor full recollect to config, default to off (0) 

Revision ID: 34
Revises: 33
Create Date: 2025-10-09 12:03:57.171011

"""
from alembic import op
from collectoss.application.db.session import DatabaseSession
from collectoss.application.config import *
from sqlalchemy.sql import text
import logging

# revision identifiers, used by Alembic.
revision = '34'
down_revision = '33'
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)

def upgrade():
    pass


def downgrade():
    pass