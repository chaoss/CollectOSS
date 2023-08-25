"""add index

Revision ID: 23
Revises: 22
Create Date: 2023-08-23 18:17:22.651191

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '23'
down_revision = '22'
branch_labels = None
depends_on = None


def upgrade():

    gh_loginindex()

def downgrade():

    upgrade=False

    gh_loginindex(upgrade)

def gh_loginindex(upgrade=True):

   if upgrade:

      conn = op.get_bind() 
      conn.execute(text(""" 
         CREATE INDEX if not exists "gh_login" ON "augur_data"."contributors" USING btree (
            "gh_login" ASC NULLS FIRST);"""))

   else: 


      conn = op.get_bind() 
      conn.execute(text(""" 
         DROP INDEX if exists "gh_login" ON "augur_data"."contributors" USING btree (
            "gh_login" ASC NULLS FIRST);"""))
