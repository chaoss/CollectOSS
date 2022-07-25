"""Change tables to mimic current db

Revision ID: 1
Revises: 0
Create Date: 2022-07-11 11:17:31.706564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1'
down_revision = '0'
branch_labels = None
depends_on = None


def upgrade():

    op.drop_constraint('fk_commits_contributors_4', 'commits', schema='augur_data', type_='foreignkey')
    op.create_foreign_key('fk_commits_contributors_4', 'commits', 'contributors', ['cmt_author_platform_username'], ['cntrb_login'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE', initially='DEFERRED', deferrable=True)

    op.drop_constraint('fk_commits_contributors_3', 'commits', schema='augur_data', type_='foreignkey')
    op.create_foreign_key('fk_commits_contributors_3', 'commits', 'contributors', ['cmt_author_platform_username'], ['cntrb_login'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE', initially='DEFERRED', deferrable=True)

    op.drop_index('therepo', table_name='repo', schema='augur_data')
    op.create_index('therepo', 'repo', ['repo_id'], unique=True, schema='augur_data')

    # add unique to pull_request assignees
    op.create_unique_constraint('assigniees-unique', 'pull_request_assignees', ['pull_request_id', 'pr_assignee_src_id'], schema='augur_data')

    # modify unique-pr-event-id
    op.drop_constraint('unique-pr-event-id', 'pull_request_events', schema='augur_data', type_='unique')
    op.create_unique_constraint('unique-pr-event-id', 'pull_request_events', ['platform_id', 'node_id'], schema='augur_data')

    # add pr-unqiue-event
    op.create_unique_constraint('pr-unqiue-event', 'pull_request_events', ['node_id'], schema='augur_data')

    # modify pr reviewers unique
    op.drop_constraint('unique_pr_src_reviewer_key', 'pull_request_reviewers', schema='augur_data', type_='unique')
    op.create_unique_constraint('unique_pr_src_reviewer_key', 'pull_request_reviewers', ['pull_request_id', 'pr_reviewer_src_id'], schema='augur_data')

    op.create_unique_constraint('unique-pr', 'pull_requests', ['repo_id', 'pr_src_id'], schema='augur_data')

    op.create_unique_constraint('repo_git-unique', 'repo', ['repo_git'], schema='augur_data')
   


def downgrade():

    op.drop_constraint('repo_git-unique', 'repo', schema='augur_data', type_='unique')

    op.drop_constraint('unique-pr', 'pull_requests', schema='augur_data', type_='unique')

    # modify pr reviewers unique
    op.drop_constraint('unique_pr_src_reviewer_key', 'pull_request_reviewers', schema='augur_data', type_='unique')
    op.create_unique_constraint('unique_pr_src_reviewer_key', 'pull_request_reviewers', ['pr_source_id', 'pr_reviewer_src_id'], schema='augur_data', initially='DEFERRED', deferrable=True)

    # remove pr-unqiue-event
    op.drop_constraint('pr-unqiue-event', 'pull_request_events', schema='augur_data', type_='unique')

    # modify unique-pr-event-id
    op.drop_constraint('unique-pr-event-id', 'pull_request_events', schema='augur_data', type_='unique')
    op.create_unique_constraint('unique-pr-event-id', 'pull_request_events', ['pr_platform_event_id', 'platform_id'], schema='augur_data')

    # remove pr assignees unique
    op.drop_constraint('assigniees-unique', 'pull_request_assignees', schema='augur_data', type_='unique')

    op.drop_index('therepo', table_name='repo', schema='augur_data')
    op.create_index('therepo', 'repo', ['repo_id'], unique=False, schema='augur_data')

    op.drop_constraint('fk_commits_contributors_3', 'commits', schema='augur_data', type_='foreignkey')
    op.create_foreign_key('fk_commits_contributors_3', 'commits', 'contributors', ['cmt_author_platform_username'], ['cntrb_login'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE')

    op.drop_constraint('fk_commits_contributors_4', 'commits', schema='augur_data', type_='foreignkey')
    op.create_foreign_key('fk_commits_contributors_4', 'commits', 'contributors', ['cmt_author_platform_username'], ['cntrb_login'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE')

