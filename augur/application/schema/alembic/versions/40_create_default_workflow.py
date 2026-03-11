"""create default workflow

Revision ID: 40
Revises: 39
Create Date: 2026-02-06 19:54:00.000000

"""
from alembic import op
import sqlalchemy as sa
import logging
from augur.improved_collection.create_workflow import insert_workflow_dag
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '40'
down_revision = '39'
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)

def upgrade():
    """
    Create a default workflow DAG with common collection tasks.
    
    This creates a workflow with the following structure:
    - repo_info (core) - foundational task that collects basic repo information
    - issues (secondary) - depends on repo_info
    - pull_requests (secondary) - depends on repo_info
    - commits (facade) - depends on repo_info and pull_requests
    """

    default_dag = {
        "tasks": [
            {
                "task_name": "task_1",
                "task_type": "core",
                "depends_on": []
            },
            {
                "task_name": "task_2",
                "task_type": "secondary",
                "depends_on": []
            },
            {
                "task_name": "task_3",
                "task_type": "secondary",
                "depends_on": ["task_1", "task_2"]
            }
        ]
    }
    
    conn = op.get_bind()
    insert_workflow_dag(default_dag, conn)


def downgrade():
    """
    Remove the default workflow.
    
    Note: This removes the first workflow (id=1) which should be the default workflow
    created by this migration. If other workflows exist, they will not be affected
    due to the WHERE clause.
    """
    connection = op.get_bind()
    
    # TODO: Remove cascades from schema?
    # Delete the first workflow (cascade will handle dependencies and tasks)
    connection.execute(
        text("DELETE FROM augur_operations.workflows WHERE id = 1")
    )
