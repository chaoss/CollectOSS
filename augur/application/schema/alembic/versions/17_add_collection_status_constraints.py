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
        condition="NOT (core_data_last_collected IS NULL AND core_status = 'Success') AND "
        "NOT (core_data_last_collected IS NOT NULL AND core_status = 'Pending')"
    )
    op.create_check_constraint(
        constraint_name="core_task_id_check",
        table_name="collection_status",
        condition="NOT (core_task_id IS NOT NULL AND core_status IN ('Pending', 'Success', 'Error')) AND "
        "NOT (core_task_id IS NULL AND core_status = 'Collecting')"
    )
    op.create_check_constraint(
        constraint_name="secondary_data_last_collected_check",
        table_name="collection_status",
        condition="NOT (secondary_data_last_collected IS NULL AND secondary_status = 'Success') AND "
        "NOT (secondary_data_last_collected IS NOT NULL AND secondary_status = 'Pending')"
    )
    op.create_check_constraint(
        constraint_name="secondary_task_id_check",
        table_name="collection_status",
        condition="NOT (secondary_task_id IS NOT NULL AND secondary_status IN ('Pending', 'Success', 'Error')) AND "
        "NOT (secondary_task_id IS NULL AND secondary_status = 'Collecting')"
    )
    op.create_check_constraint(
        constraint_name="facade_data_last_collected_check",
        table_name="collection_status",
        condition="NOT (facade_data_last_collected IS NULL AND facade_status  = 'Success' ) AND "
        "NOT (facade_data_last_collected IS NOT NULL AND facade_status IN ('Pending','Initializing', 'Update'))"
    )
    op.create_check_constraint(
        constraint_name="facade_task_id_check",
        table_name="collection_status",
        condition="NOT (facade_task_id IS NOT NULL AND facade_status IN ('Pending', 'Success', 'Error', 'Failed Clone', 'Initializing')) AND "
        "NOT (facade_task_id IS NULL AND facade_status IN ('Collecting'))"
    )
    op.create_check_constraint(
        constraint_name="core_secondary_dependency_check",
        table_name="collection_status",
        condition="NOT (core_status = 'Pending' AND secondary_status = 'Collecting')"
    )


def downgrade():
    op.drop_constraint("core_data_last_collected_check", "collection_status")
    op.drop_constraint("core_task_id_check", "collection_status")
    op.drop_constraint("secondary_data_last_collected_check", "collection_status")
    op.drop_constraint("secondary_task_id_check", "collection_status")
    op.drop_constraint("facade_data_last_collected_check", "collection_status")
    op.drop_constraint("facade_task_id_check", "collection_status")
    op.drop_constraint("core_secondary_dependency_check", "collection_status")

