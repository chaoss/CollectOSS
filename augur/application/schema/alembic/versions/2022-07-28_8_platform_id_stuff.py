"""Platform ID stuff

Revision ID: 8
Revises: 7
Create Date: 2022-07-28 20:10:56.912849

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '8'
down_revision = '7'
branch_labels = None
depends_on = None


def upgrade():

    conn = op.get_bind()

    conn.execute(text("""
                        UPDATE platform
                        SET pltfrm_id= 1
                        WHERE pltfrm_id = 25150;
                """))

    conn.execute(text("""
                     INSERT INTO "augur_data"."platform" ("pltfrm_id", "pltfrm_name", "pltfrm_version", "pltfrm_release_date", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (0, 'Unresolved', '0', '2019-06-05', 'Manual Entry', 'Sean Goggins', 'GitHub', '2022-07-28 20:43:00');
            """))

    conn.execute(text("""
                    INSERT INTO "augur_data"."platform" ("pltfrm_id", "pltfrm_name", "pltfrm_version", "pltfrm_release_date", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (2, 'GitLab', '2', '2019-06-05', 'Manual Entry', 'Sean Goggins', 'GitHub', '2022-07-28 20:43:00');
        """))

               
    
    # ### end Alembic commands ###


def downgrade():

    conn = op.get_bind()

    conn.execute(text("""
                    UPDATE platform
                    SET pltfrm_id= 25150
                    WHERE pltfrm_id = 1;
            """))

    conn.execute(text("""
                DELETE FROM platform WHERE pltfrm_id=0 OR pltfrm_id=2;
    """))
