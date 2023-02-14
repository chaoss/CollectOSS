"""Implemented oauth and user groups

Revision ID: 3
Revises: 2
Create Date: 2022-12-19 11:00:37.509132

"""
import logging

from alembic import op
import sqlalchemy as sa
from augur.application.db.session import DatabaseSession
from augur.application.db.models.augur_operations import UserGroup, UserRepo

CLI_USER_ID = 1


# revision identifiers, used by Alembic.
revision = '3'
down_revision = '2'
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)

def upgrade():

    with DatabaseSession(logger) as session:

        create_user_groups_table = """    
            CREATE TABLE "augur_operations"."user_groups" (
                "group_id" BIGSERIAL NOT NULL,
                "user_id" int4 NOT NULL,
                "name" varchar COLLATE "pg_catalog"."default" NOT NULL,
                PRIMARY KEY ("group_id"),
                FOREIGN KEY ("user_id") REFERENCES "augur_operations"."users" ("user_id") ON DELETE NO ACTION ON UPDATE NO ACTION,
                UNIQUE ("user_id", "name")
            );


            ALTER TABLE "augur_operations"."user_groups" 
            OWNER TO "augur";

            INSERT INTO "augur_operations"."user_groups" ("group_id", "user_id", "name") VALUES (1, {}, 'default') ON CONFLICT ("user_id", "name") DO NOTHING;
            ALTER SEQUENCE user_groups_group_id_seq RESTART WITH 2;
            """.format(CLI_USER_ID)

        session.execute_sql(sa.sql.text(create_user_groups_table))


        user_repos = []

        # create user group for all the users that have repos
        user_id_query = sa.sql.text("""SELECT DISTINCT(user_id) FROM user_repos;""")
        user_groups = session.fetchall_data_from_sql_text(user_id_query)
        if user_groups:

            result = []
            for group in user_groups:
                
                user_id = group["user_id"]

                if user_id == CLI_USER_ID:
                    continue

                user_group_insert = sa.sql.text(f"""INSERT INTO "augur_operations"."user_groups" ("user_id", "name") VALUES ({user_id}, 'default') RETURNING group_id, user_id;""")
                result.append(session.fetchall_data_from_sql_text(user_group_insert)[0])
            
            # cli user mapping by default
            user_group_id_mapping = {CLI_USER_ID: "1"}
            for row in result:
                user_group_id_mapping[row["user_id"]] = row["group_id"]
            

            user_repo_query = sa.sql.text("""SELECT * FROM user_repos;""")
            user_repo_data = session.fetchall_data_from_sql_text(user_repo_query)
            for row in user_repo_data:
                row.update({"group_id": user_group_id_mapping[row["user_id"]]})
                del row["user_id"]
            user_repos.extend(user_repo_data)

            # remove data from table before modifiying it
            remove_data_from_user_repos_query = sa.sql.text("""DELETE FROM user_repos;""")
            session.execute_sql(remove_data_from_user_repos_query)


        table_changes = """
        ALTER TABLE user_repos
            ADD COLUMN group_id BIGINT,
            ADD CONSTRAINT user_repos_group_id_fkey FOREIGN KEY (group_id) REFERENCES user_groups(group_id),
            DROP COLUMN user_id,
            ADD PRIMARY KEY (group_id, repo_id);
        """

        session.execute_sql(sa.sql.text(table_changes))

        for data in user_repos:

            group_id = data["group_id"]
            repo_id = data["repo_id"]

            user_repo_insert = sa.sql.text(f"""INSERT INTO "augur_operations"."user_repos" ("group_id", "repo_id") VALUES ({group_id}, {repo_id});""")
            result = session.execute_sql(user_repo_insert)

    op.create_table('client_applications',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('api_key', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('redirect_url', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['augur_operations.users.user_id'], name='client_application_user_id_fkey'),
    sa.PrimaryKeyConstraint('id'),
    schema='augur_operations'
    )

    op.create_table('user_session_tokens',
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.BigInteger(), nullable=True),
    sa.Column('expiration', sa.BigInteger(), nullable=True),
    sa.Column('application_id', sa.String(), nullable=True),

    sa.ForeignKeyConstraint(['application_id'], ['augur_operations.client_applications.id'], name='user_session_token_application_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['augur_operations.users.user_id'], name='user_session_token_user_fk'),
    sa.PrimaryKeyConstraint('token'),
    schema='augur_operations'
    )

    op.create_table('subscription_types',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='subscription_type_title_unique'),
        schema='augur_operations'
    )
    op.create_table('subscriptions',
        sa.Column('application_id', sa.String(), nullable=False),
        sa.Column('type_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['augur_operations.client_applications.id'], name='subscriptions_application_id_fkey'),
        sa.ForeignKeyConstraint(['type_id'], ['augur_operations.subscription_types.id'], name='subscriptions_type_id_fkey'),
        sa.PrimaryKeyConstraint('application_id', 'type_id'),
        schema='augur_operations'
    )

    op.add_column('user_groups', sa.Column('favorited', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False), schema='augur_operations')


    op.create_table('refresh_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_session_token', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_session_token'], ['augur_operations.user_session_tokens.token'], name='refresh_token_session_token_id_fkey'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_session_token', name='refresh_token_user_session_token_id_unique'),
        schema='augur_operations'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_table('refresh_tokens', schema='augur_operations')

    op.drop_column('user_groups', 'favorited', schema='augur_operations')

    op.drop_table('subscriptions', schema='augur_operations')
    op.drop_table('subscription_types', schema='augur_operations')

    user_group_ids = {}
    group_repo_ids = {}
    with DatabaseSession(logger) as session:
        user_id_query = sa.sql.text("""SELECT * FROM user_groups;""")
        user_groups = session.fetchall_data_from_sql_text(user_id_query)
        for row in user_groups:
            try:
                user_group_ids[row["user_id"]].append(row["group_id"])
            except KeyError:
                user_group_ids[row["user_id"]] = [row["group_id"]]


        group_id_query = sa.sql.text("""SELECT * FROM user_repos;""")
        group_repo_id_result = session.fetchall_data_from_sql_text(group_id_query)
        for row in group_repo_id_result:
            try:
                group_repo_ids[row["group_id"]].append(row["repo_id"])
            except KeyError:
                group_repo_ids[row["group_id"]] = [row["repo_id"]]

        remove_data_from_user_repos_query = sa.sql.text("""DELETE FROM user_repos;""")
        session.execute_sql(remove_data_from_user_repos_query)


        table_changes = """
        ALTER TABLE user_repos
            ADD COLUMN user_id INT,
            ADD CONSTRAINT user_repos_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id),
            DROP COLUMN group_id,
            ADD PRIMARY KEY (user_id, repo_id);
        DROP TABLE user_groups;
        """

        session.execute_sql(sa.sql.text(table_changes))

        for user_id, group_ids in user_group_ids.items():

            repos = []
            for group_id in group_ids:
                try:
                    repos.extend(group_repo_ids[group_id])
                except KeyError:
                    continue

            if repos:

                query_text_array = ["""INSERT INTO "augur_operations"."user_repos" ("repo_id", "user_id") VALUES """]
                for i, repo_id in enumerate(repos):
                    query_text_array.append(f"({repo_id}, {user_id})")

                    delimiter = ";" if i == len(repos) -1 else ","

                    query_text_array.append(delimiter)


                query_text = "".join(query_text_array)

                session.execute_sql(sa.sql.text(query_text))

    op.drop_table('user_session_tokens', schema='augur_operations')
    op.drop_table('client_applications', schema='augur_operations')

    # ### end Alembic commands ###
