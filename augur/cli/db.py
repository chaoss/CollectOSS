import csv
import click
import sqlalchemy as s
import pandas as pd
from sqlalchemy import exc

from augur.application import Application
from augur.runtime import pass_application

@click.group('db', short_help='Database utilities')
def cli():
    pass

@cli.command('add_repos', short_help="Add repositories to Augur's database")
@click.argument('filename', type=click.Path(exists=True))
@pass_application
def add_repos(app, filename):

    db = get_db_connection(app)

    df = pd.read_sql(s.sql.text("SELECT repo_group_id FROM augur_data.repo_groups"), db)
    repo_group_IDs = df['repo_group_id'].values.tolist()

    insertSQL = s.sql.text("""
        INSERT INTO augur_data.repo(repo_group_id, repo_git, repo_status, 
        tool_source, tool_version, data_source, data_collection_date) 
        VALUES (:repo_group_id, :repo_git, 'New', 'CLI', 1.0, 'Git', CURRENT_TIMESTAMP)
    """)

    with open(filename) as upload_repos_file:
        data = csv.reader(upload_repos_file, delimiter=',')
        for row in data:
            print(f"Trying repo with Git URL `{row[1]}` to repo group {row[0]}...\n")
            try:
                if int(row[0]) in repo_group_IDs:
                    pd.read_sql(insertSQL, db, params={'repo_group_id': int(row[0]), 'repo_git': row[1]})
                else:
                    print(f"Invalid repo group id specified for {row[1]}, skipping.")
            except exc.ResourceClosedError as error:
                print(f"Successfully inserted {row[1]}.")
                # pd.read_sql() will throw an AttributeError when it can't sucessfully "fetch" any rows from the result.
                # Since there's no rows to fetch after a successful insert, this is how we know it worked.
                # I know it's weird

@cli.command('get_repo_groups', short_help="List all repo groups and their associated IDs")
@pass_application
def get_repo_groups(app):

    db = get_db_connection(app)

    df = pd.read_sql(s.sql.text("SELECT repo_group_id, rg_name, rg_description FROM augur_data.repo_groups"), db)
    print(df)

    return df

@cli.command('add_repo_groups', short_help="Create new repo groups in Augur's database")
@click.argument('filename', type=click.Path(exists=True))
@pass_application
def add_repo_groups(app, filename):

    db = get_db_connection(app)

    df = pd.read_sql(s.sql.text("SELECT repo_group_id FROM augur_data.repo_groups"), db)
    repo_group_IDs = df['repo_group_id'].values.tolist()

    insertSQL = s.sql.text("""
    INSERT INTO "augur_data"."repo_groups"("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (:repo_group_id, :repo_group_name, '', '', 0, CURRENT_TIMESTAMP, 'Unknown', 'Loaded by user', '1.0', 'Git', CURRENT_TIMESTAMP);
    """)

    with open(filename) as create_repo_groups_file:
        data = csv.reader(create_repo_groups_file, delimiter=',')
        for row in data:
            print(f"\nTrying repo group with name {row[1]} and ID {row[0]}...")
            try:
                if int(row[0]) not in repo_group_IDs:
                    repo_group_IDs.append(int(row[0]))
                    pd.read_sql(insertSQL, db, params={'repo_group_id': int(row[0]), 'repo_group_name': row[1]})
                else:
                    print(f"Repo group with ID {row[1]} for repo group {row[1]} already exists, skipping...")
            except exc.ResourceClosedError as error:
                print(f"Successfully inserted {row[1]}.")
                # pd.read_sql() will throw an AttributeError when it can't sucessfully "fetch" any rows from the result.
                # Since there's no rows to fetch after a successful insert, this is how we know it worked.
                # I know it's weird, sue me (jk please don't)

def get_db_connection(app):

    user = app.read_config('Database', 'user', 'AUGUR_DB_USER', 'augur')
    password = app.read_config('Database', 'password', 'AUGUR_DB_PASS', 'password')
    host = app.read_config('Database', 'host', 'AUGUR_DB_HOST', '127.0.0.1')
    port = app.read_config('Database', 'port', 'AUGUR_DB_PORT', '5433')
    dbname = app.read_config('Database', 'database', 'AUGUR_DB_NAME', 'augur')
    schema = app.read_config('Database', 'schema', 'AUGUR_DB_SCHEMA', 'augur_data')

    DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
    )

    return s.create_engine(DB_STR, poolclass=s.pool.NullPool)
