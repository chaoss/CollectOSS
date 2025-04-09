"""Update pr events unique

Revision ID: 31
Revises: 30
Create Date: 2025-03-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from augur.application.db import create_database_engine, get_database_string


# revision identifiers, used by Alembic.
revision = '31'
down_revision = '30'
branch_labels = None
depends_on = None


    # conn = op.get_bind() 
    # conn.execute(text("""
    #     UPDATE pull_request_events
    #     SET issue_event_src_id = substring(node_url FROM '.*/([0-9]+)$')::BIGINT;
    # """))


def upgrade():

    connection_string = get_database_string()
    engine = create_database_engine(connection_string)

    with engine.connect() as conn:

        result = conn.execute(text("SELECT COUNT(*) FROM pull_request_events WHERE issue_event_src_id=pr_platform_event_id"))
        total_rows = result.scalar()
        if total_rows != 0:
            print(f"Rows needing updated: {total_rows}")
            print(f"0.0% complete")
            total_updated = 0

            while True:
                result = conn.execute(text("""
                    WITH cte AS (
                        SELECT pr_event_id 
                        FROM pull_request_events 
                        WHERE issue_event_src_id=pr_platform_event_id 
                        LIMIT 250000
                    )
                    UPDATE pull_request_events
                    SET issue_event_src_id = substring(node_url FROM '.*/([0-9]+)$')::BIGINT
                    FROM cte
                    WHERE pull_request_events.pr_event_id = cte.pr_event_id
                    RETURNING 1;
                """))

                conn.commit()

                rows_updated = result.rowcount
                total_updated += rows_updated

                if rows_updated == 0:
                    print(f"Update complete")
                    break

                percentage_updated = (total_updated / total_rows) * 100

                print(f"{percentage_updated:.1f}% complete ({total_rows-total_updated} rows left)")

            print("Creating (repo_id, issue_event_src_id) index")
    op.create_unique_constraint('pr_events_repo_id_event_src_id_unique', 'pull_request_events', ['repo_id', 'issue_event_src_id'], schema='augur_data')


def downgrade():
    op.drop_constraint('pr_events_repo_id_event_src_id_unique', 'pull_request_events', schema='augur_data', type_='unique')

    print("Please run in background. This downgrade will take a very *very* long time")
    conn = op.get_bind() 
    conn.execute(text("""
        UPDATE pull_request_events
        SET issue_event_src_id = pr_platform_event_id
        WHERE issue_event_src_id <> pr_platform_event_id;
    """))