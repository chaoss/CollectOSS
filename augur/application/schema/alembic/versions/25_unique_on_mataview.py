"""a unique index on a materialized view allows it to be refreshed concurrently, preventing blocking behavior

Revision ID: 25
Revises: 24
Create Date: 2023-08-23 18:17:22.651191

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '25'
down_revision = '24'
branch_labels = None
depends_on = None


def upgrade():

    add_uniques_onMV()

def downgrade():

    upgrade=False

    add_uniques_onMV(upgrade)

def add_fix_keys_22(upgrade=True):

   if upgrade:

      conn = op.get_bind() 
      conn.execute(text("""CREATE UNIQUE INDEX ON augur_data.api_get_all_repo_prs(repo_id);"""))

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.api_get_all_repos_commits(repo_id); """)) 

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.api_get_all_repos_issues(repo_id); """)) 

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.augur_new_contributors( cntrb_id, repo_id, month, login, year, rank); """)) 

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.explorer_commits_and_committers_daily_count( repo_id, cmt_committer_date); """)) 

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.explorer_new_contributors(cntrb_id, created_at, month, year, repo_id, login, rank); """)) 

      conn = op.get_bind()
      conn.execute(text("""
        CREATE  UNIQUE INDEX ON augur_data.explorer_entry_list(repo_id); """)) 

      # conn = op.get_bind()
      # conn.execute(text("""
      #   CREATE  UNIQUE INDEX ON augur_data.explorer_contributor_actions(); """)) 

      conn = op.get_bind()
      conn.execute(text("""
         drop MATERIALIZED VIEW if exists augur_data.explorer_libyear_all;
         drop MATERIALIZED VIEW if exists augur_data.explorer_libyear_detail;
         drop MATERIALIZED VIEW if exists augur_data.explorer_libyear_summary; """))
