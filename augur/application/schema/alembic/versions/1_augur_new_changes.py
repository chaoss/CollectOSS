"""Augur New Changes

Revision ID: 1
Revises: 0
Create Date: 2022-07-11 11:17:31.706564

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text
from augur.tasks.util.AugurUUID import AugurUUID, GithubUUID, UnresolvableUUID


# revision identifiers, used by Alembic.
revision = '1'
down_revision = '0'
branch_labels = None
depends_on = None


def upgrade():

   change_tables_to_mimic_current_db_1()
   change_natural_keys_for_bulk_upsert_2()
   add_config_table_3()
   add_user_table_4()
   change_cntrb_id_to_uuid_5()
   small_data_type_change_6()
   alias_uniques_7()
   platform_id_stuff_8()
   change_type_of_cmt_ght_author_id_9()
   add_admin_column_to_user_table_10()
   made_events_cntrb_id_nullable_11()
   add_user_repo_table_12()
   add_materialized_views_13()
   set_repo_name_path_null_14()


def downgrade():

    upgrade=False

    set_repo_name_path_null_14(upgrade)
    add_materialized_views_13(upgrade)
    add_user_repo_table_12(upgrade)
    made_events_cntrb_id_nullable_11(upgrade)
    add_admin_column_to_user_table_10(upgrade)
    change_type_of_cmt_ght_author_id_9(upgrade)
    platform_id_stuff_8(upgrade)
    alias_uniques_7(upgrade)
    small_data_type_change_6(upgrade)
    change_cntrb_id_to_uuid_5(upgrade)
    add_user_table_4(upgrade)
    add_config_table_3(upgrade)
    change_natural_keys_for_bulk_upsert_2(upgrade)
    change_tables_to_mimic_current_db_1(upgrade)



def change_tables_to_mimic_current_db_1(upgrade=True):

    if upgrade:
        
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

    else:
        
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


def change_natural_keys_for_bulk_upsert_2(upgrade=True):

    if upgrade:
            # create issue assignee unique for inserts
        op.create_unique_constraint('issue-assignee-insert-unique', 'issue_assignees', ['issue_assignee_src_id', 'issue_id'], schema='augur_data')

        # update issue message ref unique for inserts
        op.drop_constraint('repo-issue', 'issue_message_ref', schema='augur_data', type_='unique')
        op.create_unique_constraint('issue-message-ref-insert-unique', 'issue_message_ref', ['issue_msg_ref_src_comment_id', 'issue_id'], schema='augur_data')

        # create issue unique for inserts
        op.create_unique_constraint('issue-insert-unique', 'issues', ['issue_url'], schema='augur_data')

        # update message unique for inserts
        op.drop_constraint('gh-message', 'message', schema='augur_data', type_='unique')
        op.create_unique_constraint('message-insert-unique', 'message', ['platform_msg_id'], schema='augur_data')

        # update pull request message ref unique for inserts
        op.drop_constraint('pr-comment-nk', 'pull_request_message_ref', schema='augur_data', type_='unique')
        op.create_unique_constraint('pull-request-message-ref-insert-unique', 'pull_request_message_ref', ['pr_message_ref_src_comment_id', 'pull_request_id'], schema='augur_data')

        # create pull request meta unique for inserts
        op.create_unique_constraint('pull-request-meta-insert-unique', 'pull_request_meta', ['pull_request_id', 'pr_head_or_base', 'pr_sha'], schema='augur_data')

        # update pull request review message ref unique for inserts
        op.drop_constraint('pr-review-nk', 'pull_request_review_message_ref', schema='augur_data', type_='unique')
        op.create_unique_constraint('pull-request-review-message-ref-insert-unique', 'pull_request_review_message_ref', ['pr_review_msg_src_id'], schema='augur_data')

        # create pull request unique for inserts
        op.create_unique_constraint('pull-request-insert-unique', 'pull_requests', ['pr_url'], schema='augur_data')

    else:

        op.drop_constraint('pull-request-insert-unique', 'pull_requests', schema='augur_data', type_='unique')
        op.drop_constraint('pull-request-review-message-ref-insert-unique', 'pull_request_review_message_ref', schema='augur_data', type_='unique')
        op.create_unique_constraint('pr-review-nk', 'pull_request_review_message_ref', ['pr_review_msg_src_id', 'tool_source'], schema='augur_data')
        op.drop_constraint('pull-request-meta-insert-unique', 'pull_request_meta', schema='augur_data', type_='unique')
        op.drop_constraint('pull-request-message-ref-insert-unique', 'pull_request_message_ref', schema='augur_data', type_='unique')
        op.create_unique_constraint('pr-comment-nk', 'pull_request_message_ref', ['pr_message_ref_src_comment_id', 'tool_source'], schema='augur_data')
        op.drop_constraint('message-insert-unique', 'message', schema='augur_data', type_='unique')
        op.create_unique_constraint('gh-message', 'message', ['platform_msg_id', 'tool_source'], schema='augur_data')
        op.drop_constraint('issue-insert-unique', 'issues', schema='augur_data', type_='unique')
        op.drop_constraint('issue-message-ref-insert-unique', 'issue_message_ref', schema='augur_data', type_='unique')
        op.create_unique_constraint('repo-issue', 'issue_message_ref', ['issue_msg_ref_src_comment_id', 'tool_source'], schema='augur_data')
        op.drop_constraint('issue-assignee-insert-unique', 'issue_assignees', schema='augur_data', type_='unique')

def add_config_table_3(upgrade=True):

    if upgrade:

        op.create_table('config',
        sa.Column('id', sa.SmallInteger(), nullable=False),
        sa.Column('section_name', sa.String(), nullable=False),
        sa.Column('setting_name', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('section_name', 'setting_name', name='unique-config-setting'),
        schema='augur_operations'
        )

    else:
        op.drop_table('config', schema='augur_operations')

def add_user_table_4(upgrade=True):

    if upgrade:

        op.create_table('users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('login_name', sa.String(), nullable=False),
        sa.Column('login_hashword', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('text_phone', sa.String(), nullable=True),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('tool_source', sa.String(), nullable=True),
        sa.Column('tool_version', sa.String(), nullable=True),
        sa.Column('data_source', sa.String(), nullable=True),
        sa.Column('data_collection_date', postgresql.TIMESTAMP(precision=0), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email', name='user-unique-email'),
        sa.UniqueConstraint('login_name', name='user-unique-name'),
        sa.UniqueConstraint('text_phone', name='user-unique-phone'),
        schema='augur_operations'
        )

    else:
        op.drop_table('users', schema='augur_operations')

def change_cntrb_id_to_uuid_5(upgrade=True):

    if upgrade:
        conn = op.get_bind()

        op.drop_column('contributor_repo', 'cntrb_id')              
        op.drop_column('contributors_aliases', 'cntrb_id')              
        op.drop_column('issue_assignees', 'cntrb_id')               
        op.drop_column('issue_events', 'cntrb_id')
        conn.execute(text("""ALTER TABLE issues DROP COLUMN reporter_id CASCADE"""))              
        op.drop_column('issues', 'cntrb_id')             
        op.drop_column('message', 'cntrb_id')              
        op.drop_column('pull_request_assignees', 'contrib_id')               
        op.drop_column('pull_request_commits', 'pr_cmt_author_cntrb_id')              
        op.drop_column('pull_request_events', 'cntrb_id')              
        op.drop_column('pull_request_meta', 'cntrb_id')              
        op.drop_column('pull_request_repo', 'pr_cntrb_id')              
        op.drop_column('pull_request_reviewers', 'cntrb_id')              
        op.drop_column('pull_request_reviews', 'cntrb_id')              
        op.drop_column('pull_requests', 'pr_augur_contributor_id')              


        conn.execute(text("""DELETE FROM contributors"""))

        op.drop_column("contributors", "cntrb_id")
        op.add_column("contributors", 
            sa.Column("cntrb_id", postgresql.UUID(as_uuid=True))
        )
        op.create_primary_key("contributors-pk", "contributors", ["cntrb_id"])



        op.add_column('contributor_repo', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=False, comment='This is not null because what is the point without the contributor in this table? '), schema='augur_data')
        op.create_foreign_key(None, 'contributor_repo', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='RESTRICT')
        
        op.add_column('contributors_aliases', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=False), schema='augur_data')
        op.create_foreign_key(None, 'contributors_aliases', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE', initially='DEFERRED', deferrable=True)

        op.add_column('issue_assignees', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=True), schema='augur_data')
        op.create_index('issue-cntrb-assign-idx-1', 'issue_assignees', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'issue_assignees', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('issue_events', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=False), schema='augur_data')
        op.create_index('issue_events_ibfk_2', 'issue_events', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'issue_events', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='RESTRICT')

        op.add_column('issues', sa.Column('reporter_id', postgresql.UUID(as_uuid=True), nullable=True, comment='The ID of the person who opened the issue. '), schema='augur_data')
        op.add_column('issues', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=True, comment='The ID of the person who closed the issue. '), schema='augur_data')
        op.create_index('issue-cntrb-dix2', 'issues', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_index('issues_ibfk_2', 'issues', ['reporter_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'issues', 'contributors', ['reporter_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')
        op.create_foreign_key(None, 'issues', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('message', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Not populated for mailing lists. Populated for GitHub issues. '), schema='augur_data')
        op.create_index('msg-cntrb-id-idx', 'message', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'message', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE')

        op.add_column('pull_request_assignees', sa.Column('contrib_id', postgresql.UUID(as_uuid=True), nullable=True), schema='augur_data')
        op.create_index('pr_meta_cntrb-idx', 'pull_request_assignees', ['contrib_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_assignees', 'contributors', ['contrib_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('pull_request_commits', sa.Column('pr_cmt_author_cntrb_id', postgresql.UUID(as_uuid=True), nullable=True), schema='augur_data')
        op.create_foreign_key(None, 'pull_request_commits', 'contributors', ['pr_cmt_author_cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE')

        op.add_column('pull_request_events', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=False), schema='augur_data')
        op.create_index('pr_events_ibfk_2', 'pull_request_events', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_events', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('pull_request_meta', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=True), schema='augur_data')
        op.create_index('pr_meta-cntrbid-idx', 'pull_request_meta', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_meta', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('pull_request_repo', sa.Column('pr_cntrb_id', postgresql.UUID(as_uuid=True), nullable=True), schema='augur_data')
        op.create_index('pr-cntrb-idx-repo', 'pull_request_repo', ['pr_cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_repo', 'contributors', ['pr_cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('pull_request_reviewers', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=True), schema='augur_data')
        op.create_index('pr-reviewers-cntrb-idx1', 'pull_request_reviewers', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_reviewers', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE')

        op.add_column('pull_request_reviews', sa.Column('cntrb_id', postgresql.UUID(as_uuid=True), nullable=False), schema='augur_data')
        op.create_foreign_key(None, 'pull_request_reviews', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='RESTRICT')

        op.add_column('pull_requests', sa.Column('pr_augur_contributor_id', postgresql.UUID(as_uuid=True), nullable=True, comment='This is to link to the augur contributor record. '), schema='augur_data')
        op.create_foreign_key(None, 'pull_requests', 'contributors', ['pr_augur_contributor_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='RESTRICT')

        conn.execute(
            text(
                """
                    INSERT INTO "augur_data"."contributors"("cntrb_id", "cntrb_login", "cntrb_email", "cntrb_company", "cntrb_created_at", "cntrb_type", "cntrb_fake", "cntrb_deleted", "cntrb_long", "cntrb_lat", "cntrb_country_code", "cntrb_state", "cntrb_city", "cntrb_location", "cntrb_canonical", "gh_user_id", "gh_login", "gh_url", "gh_html_url", "gh_node_id", "gh_avatar_url", "gh_gravatar_id", "gh_followers_url", "gh_following_url", "gh_gists_url", "gh_starred_url", "gh_subscriptions_url", "gh_organizations_url", "gh_repos_url", "gh_events_url", "gh_received_events_url", "gh_type", "gh_site_admin", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (:cntrb_uuid, 'not-provided', NULL, NULL, '2019-06-13 11:33:39', NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, 'nobody', 'http://fake.me', 'http://fake.me', 'x', 'http://fake.me', NULL, 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', NULL, NULL, NULL, NULL, NULL, NULL, '2019-06-13 16:35:25');
                """
            ),
            cntrb_uuid=UnresolvableUUID().to_UUID()
        )

        conn.execute(
            text(
                """
                    INSERT INTO "augur_data"."contributors" ("cntrb_id", "cntrb_login", "cntrb_email", "cntrb_full_name", "cntrb_company", "cntrb_created_at", "cntrb_type", "cntrb_fake", "cntrb_deleted", "cntrb_long", "cntrb_lat", "cntrb_country_code", "cntrb_state", "cntrb_city", "cntrb_location", "cntrb_canonical", "cntrb_last_used", "gh_user_id", "gh_login", "gh_url", "gh_html_url", "gh_node_id", "gh_avatar_url", "gh_gravatar_id", "gh_followers_url", "gh_following_url", "gh_gists_url", "gh_starred_url", "gh_subscriptions_url", "gh_organizations_url", "gh_repos_url", "gh_events_url", "gh_received_events_url", "gh_type", "gh_site_admin", "gl_web_url", "gl_avatar_url", "gl_state", "gl_username", "gl_full_name", "gl_id", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (:cntrb_uuid, 'nan', 'kannayoshihiro@gmail.com', 'KANNA Yoshihiro', 'UTMC', '2009-04-17 12:43:58', NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, 'kannayoshihiro@gmail.com', '2021-01-28 21:56:10-06', 74832, 'nan', 'https://api.github.com/users/nan', 'https://github.com/nan', 'MDQ6VXNlcjc0ODMy', 'https://avatars.githubusercontent.com/u/74832?v=4', '', 'https://api.github.com/users/nan/followers', 'https://api.github.com/users/nan/following{/other_user}', 'https://api.github.com/users/nan/gists{/gist_id}', 'https://api.github.com/users/nan/starred{/owner}{/repo}', 'https://api.github.com/users/nan/subscriptions', 'https://api.github.com/users/nan/orgs', 'https://api.github.com/users/nan/repos', 'https://api.github.com/users/nan/events{/privacy}', 'https://api.github.com/users/nan/received_events', 'User', 'false', NULL, NULL, NULL, NULL, NULL, NULL, 'GitHub API Worker', '1.0.0', 'GitHub API', '2021-10-28 15:23:46');
                """
            ),
            cntrb_uuid=GithubUUID().to_UUID()
        )

    else:
        
        conn = op.get_bind()

        op.drop_column('contributor_repo', 'cntrb_id')              
        op.drop_column('contributors_aliases', 'cntrb_id')              
        op.drop_column('issue_assignees', 'cntrb_id')               
        op.drop_column('issue_events', 'cntrb_id')              
        conn.execute(text("""ALTER TABLE issues DROP COLUMN reporter_id CASCADE"""))                 
        op.drop_column('issues', 'cntrb_id')             
        op.drop_column('message', 'cntrb_id')              
        op.drop_column('pull_request_assignees', 'contrib_id')               
        op.drop_column('pull_request_commits', 'pr_cmt_author_cntrb_id')              
        op.drop_column('pull_request_events', 'cntrb_id')              
        op.drop_column('pull_request_meta', 'cntrb_id')              
        op.drop_column('pull_request_repo', 'pr_cntrb_id')              
        op.drop_column('pull_request_reviewers', 'cntrb_id')              
        op.drop_column('pull_request_reviews', 'cntrb_id')              
        op.drop_column('pull_requests', 'pr_augur_contributor_id')              

        conn.execute(text("""DELETE FROM contributors"""))

        op.drop_column("contributors", "cntrb_id")
        op.add_column("contributors", 
            sa.Column("cntrb_id", sa.BigInteger)
        )
        op.create_primary_key("contributors-pk", "contributors", ["cntrb_id"])


        op.add_column('contributor_repo', sa.Column('cntrb_id', sa.BigInteger, nullable=False, comment='This is not null because what is the point without the contributor in this table? '), schema='augur_data')
        op.create_foreign_key(None, 'contributor_repo', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='RESTRICT')
        
        op.add_column('contributors_aliases', sa.Column('cntrb_id', sa.BigInteger, nullable=False), schema='augur_data')
        op.create_foreign_key(None, 'contributors_aliases', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE', initially='DEFERRED', deferrable=True)

        op.add_column('issue_assignees', sa.Column('cntrb_id', sa.BigInteger, nullable=True), schema='augur_data')
        op.create_index('issue-cntrb-assign-idx-1', 'issue_assignees', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'issue_assignees', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('issue_events', sa.Column('cntrb_id', sa.BigInteger, nullable=False), schema='augur_data')
        op.create_index('issue_events_ibfk_2', 'issue_events', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'issue_events', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='RESTRICT')

        op.add_column('issues', sa.Column('reporter_id', sa.BigInteger, nullable=True, comment='The ID of the person who opened the issue. '), schema='augur_data')
        op.add_column('issues', sa.Column('cntrb_id', sa.BigInteger, nullable=True, comment='The ID of the person who closed the issue. '), schema='augur_data')
        op.create_index('issue-cntrb-dix2', 'issues', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_index('issues_ibfk_2', 'issues', ['reporter_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'issues', 'contributors', ['reporter_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')
        op.create_foreign_key(None, 'issues', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('message', sa.Column('cntrb_id', sa.BigInteger, nullable=True, comment='Not populated for mailing lists. Populated for GitHub issues. '), schema='augur_data')
        op.create_index('msg-cntrb-id-idx', 'message', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'message', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE')

        op.add_column('pull_request_assignees', sa.Column('contrib_id', sa.BigInteger, nullable=True), schema='augur_data')
        op.create_index('pr_meta_cntrb-idx', 'pull_request_assignees', ['contrib_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_assignees', 'contributors', ['contrib_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('pull_request_commits', sa.Column('pr_cmt_author_cntrb_id', sa.BigInteger, nullable=True), schema='augur_data')
        op.create_foreign_key(None, 'pull_request_commits', 'contributors', ['pr_cmt_author_cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE')

        op.add_column('pull_request_events', sa.Column('cntrb_id', sa.BigInteger, nullable=False), schema='augur_data')
        op.create_index('pr_events_ibfk_2', 'pull_request_events', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_events', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('pull_request_meta', sa.Column('cntrb_id', sa.BigInteger, nullable=True), schema='augur_data')
        op.create_index('pr_meta-cntrbid-idx', 'pull_request_meta', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_meta', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('pull_request_repo', sa.Column('pr_cntrb_id', sa.BigInteger, nullable=True), schema='augur_data')
        op.create_index('pr-cntrb-idx-repo', 'pull_request_repo', ['pr_cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_repo', 'contributors', ['pr_cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')

        op.add_column('pull_request_reviewers', sa.Column('cntrb_id', sa.BigInteger, nullable=True), schema='augur_data')
        op.create_index('pr-reviewers-cntrb-idx1', 'pull_request_reviewers', ['cntrb_id'], unique=False, schema='augur_data')
        op.create_foreign_key(None, 'pull_request_reviewers', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='CASCADE')

        op.add_column('pull_request_reviews', sa.Column('cntrb_id', sa.BigInteger, nullable=False), schema='augur_data')
        op.create_foreign_key(None, 'pull_request_reviews', 'contributors', ['cntrb_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='RESTRICT')

        op.add_column('pull_requests', sa.Column('pr_augur_contributor_id', sa.BigInteger, nullable=True, comment='This is to link to the augur contributor record. '), schema='augur_data')
        op.create_foreign_key(None, 'pull_requests', 'contributors', ['pr_augur_contributor_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data', onupdate='CASCADE', ondelete='RESTRICT')



        conn.execute(
            text(
                """
                    INSERT INTO "augur_data"."contributors"("cntrb_id", "cntrb_login", "cntrb_email", "cntrb_company", "cntrb_created_at", "cntrb_type", "cntrb_fake", "cntrb_deleted", "cntrb_long", "cntrb_lat", "cntrb_country_code", "cntrb_state", "cntrb_city", "cntrb_location", "cntrb_canonical", "gh_user_id", "gh_login", "gh_url", "gh_html_url", "gh_node_id", "gh_avatar_url", "gh_gravatar_id", "gh_followers_url", "gh_following_url", "gh_gists_url", "gh_starred_url", "gh_subscriptions_url", "gh_organizations_url", "gh_repos_url", "gh_events_url", "gh_received_events_url", "gh_type", "gh_site_admin", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (1, 'not-provided', NULL, NULL, '2019-06-13 11:33:39', NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, 'nobody', 'http://fake.me', 'http://fake.me', 'x', 'http://fake.me', NULL, 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', 'http://fake.me', NULL, NULL, NULL, NULL, NULL, NULL, '2019-06-13 16:35:25');
                """
            ),
        )

        conn.execute(
            text(
                """
                    INSERT INTO "augur_data"."contributors" ("cntrb_id", "cntrb_login", "cntrb_email", "cntrb_full_name", "cntrb_company", "cntrb_created_at", "cntrb_type", "cntrb_fake", "cntrb_deleted", "cntrb_long", "cntrb_lat", "cntrb_country_code", "cntrb_state", "cntrb_city", "cntrb_location", "cntrb_canonical", "cntrb_last_used", "gh_user_id", "gh_login", "gh_url", "gh_html_url", "gh_node_id", "gh_avatar_url", "gh_gravatar_id", "gh_followers_url", "gh_following_url", "gh_gists_url", "gh_starred_url", "gh_subscriptions_url", "gh_organizations_url", "gh_repos_url", "gh_events_url", "gh_received_events_url", "gh_type", "gh_site_admin", "gl_web_url", "gl_avatar_url", "gl_state", "gl_username", "gl_full_name", "gl_id", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (11, 'nan', 'kannayoshihiro@gmail.com', 'KANNA Yoshihiro', 'UTMC', '2009-04-17 12:43:58', NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, 'kannayoshihiro@gmail.com', '2021-01-28 21:56:10-06', 74832, 'nan', 'https://api.github.com/users/nan', 'https://github.com/nan', 'MDQ6VXNlcjc0ODMy', 'https://avatars.githubusercontent.com/u/74832?v=4', '', 'https://api.github.com/users/nan/followers', 'https://api.github.com/users/nan/following{/other_user}', 'https://api.github.com/users/nan/gists{/gist_id}', 'https://api.github.com/users/nan/starred{/owner}{/repo}', 'https://api.github.com/users/nan/subscriptions', 'https://api.github.com/users/nan/orgs', 'https://api.github.com/users/nan/repos', 'https://api.github.com/users/nan/events{/privacy}', 'https://api.github.com/users/nan/received_events', 'User', 'false', NULL, NULL, NULL, NULL, NULL, NULL, 'GitHub API Worker', '1.0.0', 'GitHub API', '2021-10-28 15:23:46');
                """
            ),
        )

def small_data_type_change_6(upgrade=True):
    
    if upgrade:
        op.alter_column('repo_sbom_scans', 'repo_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True,
               schema='augur_data')
        op.alter_column('repo_topic', 'repo_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True,
               schema='augur_data')

    else:
        op.alter_column('repo_topic', 'repo_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True,
               schema='augur_data')
        op.alter_column('repo_sbom_scans', 'repo_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True,
               schema='augur_data')

def alias_uniques_7(upgrade=True):

    if upgrade:
        op.drop_constraint("only-email-once", 'contributors_aliases', schema='augur_data', type_='unique')
        op.create_unique_constraint('contributor-alias-unique', 'contributors_aliases', ['alias_email'], schema='augur_data')
    else:
        op.drop_constraint('contributor-alias-unique', 'contributors_aliases', schema='augur_data', type_='unique')
        op.create_unique_constraint("only-email-once", 'contributors_aliases', ['alias_email', 'canonical_email'], schema='augur_data', initially="DEFERRED", deferrable=True)

def platform_id_stuff_8(upgrade=True):

    if upgrade:
        
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

    else:
        conn = op.get_bind()

        conn.execute(text("""
                        UPDATE platform
                        SET pltfrm_id= 25150
                        WHERE pltfrm_id = 1;
                """))

        conn.execute(text("""
                    DELETE FROM platform WHERE pltfrm_id=0 OR pltfrm_id=2;
        """))

def change_type_of_cmt_ght_author_id_9(upgrade=True):

    if upgrade:
        conn = op.get_bind()
        conn.execute(text("""DELETE FROM commits"""))
        op.drop_column('commits', 'cmt_ght_author_id')

        op.add_column('commits', sa.Column('cmt_ght_author_id', postgresql.UUID(as_uuid=True), nullable=True), schema='augur_data')
        op.create_index('author_cntrb_id', 'commits', ['cmt_ght_author_id'], unique=False, schema='augur_data')

    else:
        
        conn = op.get_bind()
        conn.execute(text("""DELETE FROM commits"""))

        op.drop_column('commits', 'cmt_ght_author_id')
        op.add_column('commits', sa.Column('cmt_ght_author_id', sa.INTEGER, nullable=True), schema='augur_data') 

def add_admin_column_to_user_table_10(upgrade=True):

    if upgrade:
        op.add_column('users', sa.Column('admin', sa.Boolean(), nullable=False), schema='augur_operations')
    else:
        op.drop_column('users', 'admin', schema='augur_operations')

def made_events_cntrb_id_nullable_11(upgrade=True):

    if upgrade:
        
        op.alter_column('issue_events', 'cntrb_id',
               existing_type=postgresql.UUID(),
               nullable=True,
               schema='augur_data')
        op.alter_column('pull_request_events', 'cntrb_id',
               existing_type=postgresql.UUID(),
               nullable=True,
               schema='augur_data')
    else:
        op.alter_column('pull_request_events', 'cntrb_id',
                existing_type=postgresql.UUID(),
                nullable=False,
                schema='augur_data')
        op.alter_column('issue_events', 'cntrb_id',
                existing_type=postgresql.UUID(),
                nullable=False,
                schema='augur_data')

def add_user_repo_table_12(upgrade=True):

    if upgrade:
        op.create_table('user_repos',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('repo_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['repo_id'], ['augur_data.repo.repo_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['augur_operations.users.user_id'], ),
        sa.PrimaryKeyConstraint('user_id', 'repo_id'),
        schema='augur_operations'
        )

        conn = op.get_bind()
        cli_user_id = 1
        conn.execute(text(f"""INSERT INTO "augur_operations"."users" ("user_id", "login_name", "login_hashword", "email", "text_phone", "first_name", "last_name", "tool_source", "tool_version", "data_source", "data_collection_date", "admin") VALUES({cli_user_id}, 'cli_user', 'pbkdf2:sha256:260000$oDmAfipU8Ef8TAau$835fce1fc3290b57b5e02ec83aef4613cc06664e6e7535bb6d267dc44563d5d5', 'cli_user', NULL, 'cli_user', 'cli_user', 'Schema Generaation', NULL, 'Schema Generation', '2022-10-02 21:49:13', 'f');
        
        ALTER SEQUENCE users_user_id_seq RESTART WITH  2;
        ALTER SEQUENCE repo_repo_id_seq RESTART WITH 25480;
        """))
        

        default_repos_ids = [1]
        for repo_id in default_repos_ids:
            conn.execute(text(
                f"""INSERT INTO "augur_operations"."user_repos" ("user_id", "repo_id") VALUES ({cli_user_id}, {repo_id});"""))
    else:
        op.drop_table('user_repos', schema='augur_operations')

        conn = op.get_bind()
        conn.execute(text("""DELETE FROM "augur_operations"."users" WHERE user_id=1"""))

def add_materialized_views_13(upgrade=True):

    if upgrade:
        conn = op.get_bind()
        conn.execute(text("""
        drop materialized view if exists augur_data.explorer_commits_and_committers_daily_count; 
        drop materialized view if exists augur_data.api_get_all_repos_commits; 
        drop materialized view if exists augur_data.api_get_all_repos_issues; 
        drop materialized view if exists augur_data.augur_new_contributors; 
        drop materialized view if exists augur_data.explorer_contributor_actions; 
        drop materialized view if exists augur_data.explorer_entry_list; 
        drop materialized view if exists augur_data.explorer_libyear_all; 
        drop materialized view if exists augur_data.explorer_libyear_detail; 
        drop materialized view if exists augur_data.explorer_new_contributors;""")) 


        conn = op.get_bind()
        conn.execute(text("""

        create materialized view augur_data.explorer_commits_and_committers_daily_count as
        SELECT repo.repo_id,
            repo.repo_name,
            commits.cmt_committer_date,
            count(commits.cmt_id) AS num_of_commits,
            count(DISTINCT commits.cmt_committer_raw_email) AS num_of_unique_committers
        FROM (augur_data.commits
            LEFT JOIN augur_data.repo ON ((repo.repo_id = commits.repo_id)))
        GROUP BY repo.repo_id, repo.repo_name, commits.cmt_committer_date
        ORDER BY repo.repo_id, commits.cmt_committer_date;"""))


        conn.execute(text("""

        create materialized view augur_data.api_get_all_repos_commits as
        SELECT commits.repo_id,
            count(DISTINCT commits.cmt_commit_hash) AS commits_all_time
        FROM augur_data.commits
        GROUP BY commits.repo_id;"""))


        conn.execute(text("""

        create materialized view augur_data.api_get_all_repos_issues as
        SELECT issues.repo_id,
            count(*) AS issues_all_time
        FROM augur_data.issues
        WHERE (issues.pull_request IS NULL)
        GROUP BY issues.repo_id; """))

        conn.execute(text("""

        create materialized view augur_data.explorer_libyear_all as 
        SELECT a.repo_id,
            a.repo_name,
            avg(b.libyear) AS avg_libyear,
            date_part('month'::text, (a.data_collection_date)::date) AS month,
            date_part('year'::text, (a.data_collection_date)::date) AS year
        FROM augur_data.repo a,
            augur_data.repo_deps_libyear b
        GROUP BY a.repo_id, a.repo_name, (date_part('month'::text, (a.data_collection_date)::date)), (date_part('year'::text, (a.data_collection_date)::date))
        ORDER BY (date_part('year'::text, (a.data_collection_date)::date)) DESC, (date_part('month'::text, (a.data_collection_date)::date)) DESC, (avg(b.libyear)) DESC; """))

        conn.execute(text("""

        create materialized view augur_data.explorer_libyear_summary as
        SELECT a.repo_id,
            a.repo_name,
            avg(b.libyear) AS avg_libyear,
            date_part('month'::text, (a.data_collection_date)::date) AS month,
            date_part('year'::text, (a.data_collection_date)::date) AS year
        FROM augur_data.repo a,
            augur_data.repo_deps_libyear b
        GROUP BY a.repo_id, a.repo_name, (date_part('month'::text, (a.data_collection_date)::date)), (date_part('year'::text, (a.data_collection_date)::date))
        ORDER BY (date_part('year'::text, (a.data_collection_date)::date)) DESC, (date_part('month'::text, (a.data_collection_date)::date)) DESC, (avg(b.libyear)) DESC;"""))

        conn.execute(text("""

        create materialized view augur_data.explorer_libyear_detail as 
        SELECT a.repo_id,
            a.repo_name,
            b.name,
            b.requirement,
            b.current_verion,
            b.latest_version,
            b.current_release_date,
            b.libyear,
            max(b.data_collection_date) AS max
        FROM augur_data.repo a,
            augur_data.repo_deps_libyear b
        GROUP BY a.repo_id, a.repo_name, b.name, b.requirement, b.current_verion, b.latest_version, b.current_release_date, b.libyear
        ORDER BY a.repo_id, b.requirement; """))

        conn.execute(text("""

    create materialized view augur_data.explorer_new_contributors as
    SELECT x.cntrb_id,
        x.created_at,
        x.month,
        x.year,
        x.repo_id,
        x.repo_name,
        x.full_name,
        x.login,
        x.rank
    FROM ( SELECT b.cntrb_id,
                b.created_at,
                b.month,
                b.year,
                b.repo_id,
                b.repo_name,
                b.full_name,
                b.login,
                b.action,
                b.rank
            FROM ( SELECT a.id AS cntrb_id,
                        a.created_at,
                        date_part('month'::text, (a.created_at)::date) AS month,
                        date_part('year'::text, (a.created_at)::date) AS year,
                        a.repo_id,
                        repo.repo_name,
                        a.full_name,
                        a.login,
                        a.action,
                        rank() OVER (PARTITION BY a.id ORDER BY a.created_at) AS rank
                    FROM ( SELECT canonical_full_names.canonical_id AS id,
                                issues.created_at,
                                issues.repo_id,
                                'issue_opened'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM ((augur_data.issues
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issues.reporter_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE (issues.pull_request IS NULL)
                            GROUP BY canonical_full_names.canonical_id, issues.repo_id, issues.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT canonical_full_names.canonical_id AS id,
                                to_timestamp((commits.cmt_author_date)::text, 'YYYY-MM-DD'::text) AS created_at,
                                commits.repo_id,
                                'commit'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM ((augur_data.commits
                                LEFT JOIN augur_data.contributors ON (((contributors.cntrb_canonical)::text = (commits.cmt_author_email)::text)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            GROUP BY commits.repo_id, canonical_full_names.canonical_email, canonical_full_names.canonical_id, commits.cmt_author_date, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT message.cntrb_id AS id,
                                commit_comment_ref.created_at,
                                commits.repo_id,
                                'commit_comment'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM augur_data.commit_comment_ref,
                                augur_data.commits,
                                ((augur_data.message
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE ((commits.cmt_id = commit_comment_ref.cmt_id) AND (commit_comment_ref.msg_id = message.msg_id))
                            GROUP BY message.cntrb_id, commits.repo_id, commit_comment_ref.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT issue_events.cntrb_id AS id,
                                issue_events.created_at,
                                issues.repo_id,
                                'issue_closed'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM augur_data.issues,
                                ((augur_data.issue_events
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issue_events.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE ((issues.issue_id = issue_events.issue_id) AND (issues.pull_request IS NULL) AND (issue_events.cntrb_id IS NOT NULL) AND ((issue_events.action)::text = 'closed'::text))
                            GROUP BY issue_events.cntrb_id, issues.repo_id, issue_events.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT pull_requests.pr_augur_contributor_id AS id,
                                pull_requests.pr_created_at AS created_at,
                                pull_requests.repo_id,
                                'open_pull_request'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM ((augur_data.pull_requests
                                LEFT JOIN augur_data.contributors ON ((pull_requests.pr_augur_contributor_id = contributors.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            GROUP BY pull_requests.pr_augur_contributor_id, pull_requests.repo_id, pull_requests.pr_created_at, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT message.cntrb_id AS id,
                                message.msg_timestamp AS created_at,
                                pull_requests.repo_id,
                                'pull_request_comment'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM augur_data.pull_requests,
                                augur_data.pull_request_message_ref,
                                ((augur_data.message
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE ((pull_request_message_ref.pull_request_id = pull_requests.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
                            GROUP BY message.cntrb_id, pull_requests.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT issues.reporter_id AS id,
                                message.msg_timestamp AS created_at,
                                issues.repo_id,
                                'issue_comment'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM augur_data.issues,
                                augur_data.issue_message_ref,
                                ((augur_data.message
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE ((issue_message_ref.msg_id = message.msg_id) AND (issues.issue_id = issue_message_ref.issue_id) AND (issues.pull_request_id = NULL::bigint))
                            GROUP BY issues.reporter_id, issues.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login) a,
                        augur_data.repo
                    WHERE ((a.id IS NOT NULL) AND (a.repo_id = repo.repo_id))
                    GROUP BY a.id, a.repo_id, a.action, a.created_at, repo.repo_name, a.full_name, a.login
                    ORDER BY a.id) b
            WHERE (b.rank = ANY (ARRAY[(1)::bigint, (2)::bigint, (3)::bigint, (4)::bigint, (5)::bigint, (6)::bigint, (7)::bigint]))) x;"""))

        conn.execute(text("""

    create  materialized view augur_data.augur_new_contributors as 
    SELECT x.cntrb_id,
        x.created_at,
        x.month,
        x.year,
        x.repo_id,
        x.repo_name,
        x.full_name,
        x.login,
        x.rank
    FROM ( SELECT b.cntrb_id,
                b.created_at,
                b.month,
                b.year,
                b.repo_id,
                b.repo_name,
                b.full_name,
                b.login,
                b.action,
                b.rank
            FROM ( SELECT a.id AS cntrb_id,
                        a.created_at,
                        date_part('month'::text, (a.created_at)::date) AS month,
                        date_part('year'::text, (a.created_at)::date) AS year,
                        a.repo_id,
                        repo.repo_name,
                        a.full_name,
                        a.login,
                        a.action,
                        rank() OVER (PARTITION BY a.id ORDER BY a.created_at) AS rank
                    FROM ( SELECT canonical_full_names.canonical_id AS id,
                                issues.created_at,
                                issues.repo_id,
                                'issue_opened'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM ((augur_data.issues
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issues.reporter_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE (issues.pull_request IS NULL)
                            GROUP BY canonical_full_names.canonical_id, issues.repo_id, issues.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT canonical_full_names.canonical_id AS id,
                                to_timestamp((commits.cmt_author_date)::text, 'YYYY-MM-DD'::text) AS created_at,
                                commits.repo_id,
                                'commit'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM ((augur_data.commits
                                LEFT JOIN augur_data.contributors ON (((contributors.cntrb_email)::text = (commits.cmt_author_email)::text)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            GROUP BY commits.repo_id, canonical_full_names.canonical_email, canonical_full_names.canonical_id, commits.cmt_author_date, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT message.cntrb_id AS id,
                                commit_comment_ref.created_at,
                                commits.repo_id,
                                'commit_comment'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM augur_data.commit_comment_ref,
                                augur_data.commits,
                                ((augur_data.message
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE ((commits.cmt_id = commit_comment_ref.cmt_id) AND (commit_comment_ref.msg_id = message.msg_id))
                            GROUP BY message.cntrb_id, commits.repo_id, commit_comment_ref.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT issue_events.cntrb_id AS id,
                                issue_events.created_at,
                                issues.repo_id,
                                'issue_closed'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM augur_data.issues,
                                ((augur_data.issue_events
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issue_events.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE ((issues.issue_id = issue_events.issue_id) AND (issues.pull_request IS NULL) AND (issue_events.cntrb_id IS NOT NULL) AND ((issue_events.action)::text = 'closed'::text))
                            GROUP BY issue_events.cntrb_id, issues.repo_id, issue_events.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT pull_requests.pr_augur_contributor_id AS id,
                                pull_requests.pr_created_at AS created_at,
                                pull_requests.repo_id,
                                'open_pull_request'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM ((augur_data.pull_requests
                                LEFT JOIN augur_data.contributors ON ((pull_requests.pr_augur_contributor_id = contributors.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            GROUP BY pull_requests.pr_augur_contributor_id, pull_requests.repo_id, pull_requests.pr_created_at, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT message.cntrb_id AS id,
                                message.msg_timestamp AS created_at,
                                pull_requests.repo_id,
                                'pull_request_comment'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM augur_data.pull_requests,
                                augur_data.pull_request_message_ref,
                                ((augur_data.message
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE ((pull_request_message_ref.pull_request_id = pull_requests.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
                            GROUP BY message.cntrb_id, pull_requests.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login
                            UNION ALL
                            SELECT issues.reporter_id AS id,
                                message.msg_timestamp AS created_at,
                                issues.repo_id,
                                'issue_comment'::text AS action,
                                contributors.cntrb_full_name AS full_name,
                                contributors.cntrb_login AS login
                            FROM augur_data.issues,
                                augur_data.issue_message_ref,
                                ((augur_data.message
                                LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                        contributors_1.cntrb_canonical AS canonical_email,
                                        contributors_1.data_collection_date,
                                        contributors_1.cntrb_id AS canonical_id
                                    FROM augur_data.contributors contributors_1
                                    WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                    ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                            WHERE ((issue_message_ref.msg_id = message.msg_id) AND (issues.issue_id = issue_message_ref.issue_id) AND (issues.pull_request_id = NULL::bigint))
                            GROUP BY issues.reporter_id, issues.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login) a,
                        augur_data.repo
                    WHERE ((a.id IS NOT NULL) AND (a.repo_id = repo.repo_id))
                    GROUP BY a.id, a.repo_id, a.action, a.created_at, repo.repo_name, a.full_name, a.login
                    ORDER BY a.id) b
            WHERE (b.rank = ANY (ARRAY[(1)::bigint, (2)::bigint, (3)::bigint, (4)::bigint, (5)::bigint, (6)::bigint, (7)::bigint]))) x; """))

        conn.execute(text("""
        create materialized view augur_data.explorer_contributor_actions as 
        SELECT x.cntrb_id,
            x.created_at,
            x.repo_id,
            x.login,
            x.action,
            x.rank
        FROM ( SELECT b.cntrb_id,
                    b.created_at,
                    b.month,
                    b.year,
                    b.repo_id,
                    b.repo_name,
                    b.full_name,
                    b.login,
                    b.action,
                    b.rank
                FROM ( SELECT a.id AS cntrb_id,
                            a.created_at,
                            date_part('month'::text, (a.created_at)::date) AS month,
                            date_part('year'::text, (a.created_at)::date) AS year,
                            a.repo_id,
                            repo.repo_name,
                            a.full_name,
                            a.login,
                            a.action,
                            rank() OVER (PARTITION BY a.id, a.repo_id ORDER BY a.created_at) AS rank
                        FROM ( SELECT canonical_full_names.canonical_id AS id,
                                    issues.created_at,
                                    issues.repo_id,
                                    'issue_opened'::text AS action,
                                    contributors.cntrb_full_name AS full_name,
                                    contributors.cntrb_login AS login
                                FROM ((augur_data.issues
                                    LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issues.reporter_id)))
                                    LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                            contributors_1.cntrb_canonical AS canonical_email,
                                            contributors_1.data_collection_date,
                                            contributors_1.cntrb_id AS canonical_id
                                        FROM augur_data.contributors contributors_1
                                        WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                        ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                WHERE (issues.pull_request IS NULL)
                                GROUP BY canonical_full_names.canonical_id, issues.repo_id, issues.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                                UNION ALL
                                SELECT canonical_full_names.canonical_id AS id,
                                    to_timestamp((commits.cmt_author_date)::text, 'YYYY-MM-DD'::text) AS created_at,
                                    commits.repo_id,
                                    'commit'::text AS action,
                                    contributors.cntrb_full_name AS full_name,
                                    contributors.cntrb_login AS login
                                FROM ((augur_data.commits
                                    LEFT JOIN augur_data.contributors ON (((contributors.cntrb_canonical)::text = (commits.cmt_author_email)::text)))
                                    LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                            contributors_1.cntrb_canonical AS canonical_email,
                                            contributors_1.data_collection_date,
                                            contributors_1.cntrb_id AS canonical_id
                                        FROM augur_data.contributors contributors_1
                                        WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_canonical)::text)
                                        ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                GROUP BY commits.repo_id, canonical_full_names.canonical_email, canonical_full_names.canonical_id, commits.cmt_author_date, contributors.cntrb_full_name, contributors.cntrb_login
                                UNION ALL
                                SELECT message.cntrb_id AS id,
                                    commit_comment_ref.created_at,
                                    commits.repo_id,
                                    'commit_comment'::text AS action,
                                    contributors.cntrb_full_name AS full_name,
                                    contributors.cntrb_login AS login
                                FROM augur_data.commit_comment_ref,
                                    augur_data.commits,
                                    ((augur_data.message
                                    LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                    LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                            contributors_1.cntrb_canonical AS canonical_email,
                                            contributors_1.data_collection_date,
                                            contributors_1.cntrb_id AS canonical_id
                                        FROM augur_data.contributors contributors_1
                                        WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                        ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                WHERE ((commits.cmt_id = commit_comment_ref.cmt_id) AND (commit_comment_ref.msg_id = message.msg_id))
                                GROUP BY message.cntrb_id, commits.repo_id, commit_comment_ref.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                                UNION ALL
                                SELECT issue_events.cntrb_id AS id,
                                    issue_events.created_at,
                                    issues.repo_id,
                                    'issue_closed'::text AS action,
                                    contributors.cntrb_full_name AS full_name,
                                    contributors.cntrb_login AS login
                                FROM augur_data.issues,
                                    ((augur_data.issue_events
                                    LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = issue_events.cntrb_id)))
                                    LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                            contributors_1.cntrb_canonical AS canonical_email,
                                            contributors_1.data_collection_date,
                                            contributors_1.cntrb_id AS canonical_id
                                        FROM augur_data.contributors contributors_1
                                        WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                        ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                WHERE ((issues.issue_id = issue_events.issue_id) AND (issues.pull_request IS NULL) AND (issue_events.cntrb_id IS NOT NULL) AND ((issue_events.action)::text = 'closed'::text))
                                GROUP BY issue_events.cntrb_id, issues.repo_id, issue_events.created_at, contributors.cntrb_full_name, contributors.cntrb_login
                                UNION ALL
                                SELECT pull_requests.pr_augur_contributor_id AS id,
                                    pull_requests.pr_created_at AS created_at,
                                    pull_requests.repo_id,
                                    'open_pull_request'::text AS action,
                                    contributors.cntrb_full_name AS full_name,
                                    contributors.cntrb_login AS login
                                FROM ((augur_data.pull_requests
                                    LEFT JOIN augur_data.contributors ON ((pull_requests.pr_augur_contributor_id = contributors.cntrb_id)))
                                    LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                            contributors_1.cntrb_canonical AS canonical_email,
                                            contributors_1.data_collection_date,
                                            contributors_1.cntrb_id AS canonical_id
                                        FROM augur_data.contributors contributors_1
                                        WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                        ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                GROUP BY pull_requests.pr_augur_contributor_id, pull_requests.repo_id, pull_requests.pr_created_at, contributors.cntrb_full_name, contributors.cntrb_login
                                UNION ALL
                                SELECT message.cntrb_id AS id,
                                    message.msg_timestamp AS created_at,
                                    pull_requests.repo_id,
                                    'pull_request_comment'::text AS action,
                                    contributors.cntrb_full_name AS full_name,
                                    contributors.cntrb_login AS login
                                FROM augur_data.pull_requests,
                                    augur_data.pull_request_message_ref,
                                    ((augur_data.message
                                    LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                    LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                            contributors_1.cntrb_canonical AS canonical_email,
                                            contributors_1.data_collection_date,
                                            contributors_1.cntrb_id AS canonical_id
                                        FROM augur_data.contributors contributors_1
                                        WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                        ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                WHERE ((pull_request_message_ref.pull_request_id = pull_requests.pull_request_id) AND (pull_request_message_ref.msg_id = message.msg_id))
                                GROUP BY message.cntrb_id, pull_requests.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login
                                UNION ALL
                                SELECT issues.reporter_id AS id,
                                    message.msg_timestamp AS created_at,
                                    issues.repo_id,
                                    'issue_comment'::text AS action,
                                    contributors.cntrb_full_name AS full_name,
                                    contributors.cntrb_login AS login
                                FROM augur_data.issues,
                                    augur_data.issue_message_ref,
                                    ((augur_data.message
                                    LEFT JOIN augur_data.contributors ON ((contributors.cntrb_id = message.cntrb_id)))
                                    LEFT JOIN ( SELECT DISTINCT ON (contributors_1.cntrb_canonical) contributors_1.cntrb_full_name,
                                            contributors_1.cntrb_canonical AS canonical_email,
                                            contributors_1.data_collection_date,
                                            contributors_1.cntrb_id AS canonical_id
                                        FROM augur_data.contributors contributors_1
                                        WHERE ((contributors_1.cntrb_canonical)::text = (contributors_1.cntrb_email)::text)
                                        ORDER BY contributors_1.cntrb_canonical) canonical_full_names ON (((canonical_full_names.canonical_email)::text = (contributors.cntrb_canonical)::text)))
                                WHERE ((issue_message_ref.msg_id = message.msg_id) AND (issues.issue_id = issue_message_ref.issue_id) AND (issues.pull_request_id = NULL::bigint))
                                GROUP BY issues.reporter_id, issues.repo_id, message.msg_timestamp, contributors.cntrb_full_name, contributors.cntrb_login) a,
                            augur_data.repo
                        WHERE ((a.id IS NOT NULL) AND (a.repo_id = repo.repo_id))
                        GROUP BY a.id, a.repo_id, a.action, a.created_at, repo.repo_name, a.full_name, a.login
                        ORDER BY a.created_at DESC) b) x
            ORDER BY x.created_at DESC; """))
    else:
        
        conn = op.get_bind()
        conn.execute(text("""drop materialized view if exists augur_data.explorer_commits_and_committers_daily_count;""")) 
        conn.execute(text("""drop materialized view if exists augur_data.api_get_all_repos_commits;"""))
        conn.execute(text("""drop materialized view if exists augur_data.api_get_all_repos_issues;"""))
        conn.execute(text("""drop materialized view if exists augur_data.augur_new_contributors;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_contributor_actions;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_entry_list;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_libyear_all;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_libyear_detail;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_libyear_summary;"""))
        conn.execute(text("""drop materialized view if exists augur_data.explorer_new_contributors;"""))

def set_repo_name_path_null_14(upgrade=True):
    
    if upgrade:
        op.create_foreign_key("cmt_ght_author_cntrb_id_fk", 'commits', 'contributors', ['cmt_ght_author_id'], ['cntrb_id'], source_schema='augur_data', referent_schema='augur_data')
        op.alter_column('releases', 'release_id',
                existing_type=sa.CHAR(length=64),
                type_=sa.CHAR(length=256),
                existing_nullable=False,
                existing_server_default=sa.text('nextval(\'"augur_data".releases_release_id_seq\'::regclass)'),
                schema='augur_data')

    else:
        op.alter_column('releases', 'release_id',
               existing_type=sa.CHAR(length=256),
               type_=sa.CHAR(length=128),
               existing_nullable=False,
               existing_server_default=sa.text('nextval(\'"augur_data".releases_release_id_seq\'::regclass)'),
               schema='augur_data')
        op.drop_constraint("cmt_ght_author_cntrb_id_fk", 'commits', schema='augur_data', type_='foreignkey')