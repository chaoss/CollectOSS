"""Add collection status constraints

Revision ID: 17
Revises: 16
Create Date: 2023-04-19 14:30:14.709349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17'
down_revision = '16'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        constraint_name="core_data_last_collected_check",
        table_name="collection_status",
        condition="(core_status = 'Error') OR "
        "(core_status = 'Collecting') OR "
        "(core_data_last_collected IS NOT NULL AND core_status = 'Success') OR "
        "(core_data_last_collected IS NULL AND core_status = 'Pending')"
    )
    op.create_check_constraint(
        constraint_name="core_task_id_check",
        table_name="collection_status",
        condition="(core_task_id IS NULL AND core_status IN ('Pending', 'Success', 'Error')) OR "
        "(core_task_id IS NOT NULL AND core_status = 'Collecting')"
    )
    op.create_check_constraint(
        constraint_name="secondary_data_last_collected_check",
        table_name="collection_status",
        condition="(secondary_status = 'Error') OR "
        "(secondary_status = 'Collecting') OR "
        "(secondary_data_last_collected IS NOT NULL AND secondary_status = 'Success') OR "
        "(secondary_data_last_collected IS NULL AND secondary_status = 'Pending')"
    )
    op.create_check_constraint(
        constraint_name="secondary_task_id_check",
        table_name="collection_status",
        condition="(secondary_task_id IS NULL AND secondary_status IN ('Pending', 'Success', 'Error')) OR "
        "(secondary_task_id IS NOT NULL AND secondary_status = 'Collecting')"
    )
    op.create_check_constraint(
        constraint_name="facade_data_last_collected_check",
        table_name="collection_status",
        condition="(facade_status = 'Error') OR "
        "(facade_data_last_collected IS NOT NULL AND facade_status IN ('Success', 'Update')) OR "
        "(facade_data_last_collected IS NULL AND facade_status = 'Pending')"
    )
    op.create_check_constraint(
        constraint_name="facade_task_id_check",
        table_name="collection_status",
        condition="(facade_task_id IS NULL AND facade_status IN ('Pending', 'Success', 'Error', 'Failed Clone')) OR "
        "(facade_task_id IS NOT NULL AND facade_status = 'Collecting')"
    )
    op.create_check_constraint(
        constraint_name="core_secondary_dependency_check",
        table_name="collection_status",
        condition="(core_status = 'Success') OR "
        "(core_status IN ('Pending', 'Collecting', 'Error') AND secondary_status = 'Pending')"
    )


def downgrade():
    op.drop_constraint("core_data_last_collected_check", "collection_status")
    op.drop_constraint("core_task_id_check", "collection_status")
    op.drop_constraint("secondary_data_last_collected_check", "collection_status")
    op.drop_constraint("secondary_task_id_check", "collection_status")
    op.drop_constraint("facade_data_last_collected_check", "collection_status")
    op.drop_constraint("facade_task_id_check", "collection_status")
    op.drop_constraint("core_secondary_dependency_check", "collection_status")

