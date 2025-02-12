"""Add extra celery options to the config if they do not exist

Revision ID: 19
Revises: 18
Create Date: 2023-05-15 12:03:57.171011

"""
from alembic import op
from augur.application.db.session import DatabaseSession
from augur.application.config import *
from sqlalchemy.sql import text
import logging

# revision identifiers, used by Alembic.
revision = '19'
down_revision = '18'
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)

def upgrade():

    with DatabaseSession(logger) as session:
        config = AugurConfig(logger,session)
        config_dict = config.load_config()
        
        #Update the missing fields of the celery section in the config
        section = config_dict.get("Celery")

        #Just copy the default if section doesn't exist.
        if section:
            if 'worker_process_vmem_cap' not in section.keys():
                section['worker_process_vmem_cap'] = 0.25
            
            if 'refresh_materialized_views_interval_in_days' not in section.keys():
                section['refresh_materialized_views_interval_in_days'] = 7
        else:
            section = config.default_config["Celery"]
        
        config.add_section_from_json("Celery", section)

        #delete old setting
        session.execute_sql(text(f"""
            DELETE FROM augur_operations.config
            WHERE section_name='Celery' AND setting_name='concurrency';
        """))



def downgrade():

    conn = op.get_bind()

    conn.execute(text(f"""
        DELETE FROM augur_operations.config
        WHERE section_name='Celery' AND (setting_name='worker_process_vmem_cap' OR setting_name='refresh_materialized_views_interval_in_days');
    """))

    try:
        conn.execute(text(f"""
            INSERT INTO augur_operations.config (section_name,setting_name,value,type) VALUES ('Celery','concurrency',12,'int');
        """))
    except:
        pass