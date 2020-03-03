from os import walk, chdir, environ
from sys import exit
from subprocess import call
import csv
import click
import sqlalchemy as s
import pandas as pd
from sqlalchemy import exc

# from augur.runtime import pass_application

@click.group('db', short_help='Database utilities')
def cli():
    pass

@cli.command('add_repos', short_help="Add repositories to Augur's database")
@click.argument('filename', type=click.Path(exists=True))
@click.pass_context
def add_repos(ctx, filename):
    app = ctx.obj

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
@click.pass_context
def get_repo_groups(ctx):
    app = ctx.obj

    db = get_db_connection(app)

    df = pd.read_sql(s.sql.text("SELECT repo_group_id, rg_name, rg_description FROM augur_data.repo_groups"), db)
    print(df)

    return df

@cli.command('add_repo_groups', short_help="Create new repo groups in Augur's database")
@click.argument('filename', type=click.Path(exists=True))
@click.pass_context
def add_repo_groups(ctx, filename):
    app = ctx.obj

    db = get_db_connection(app)

    df = pd.read_sql(s.sql.text("SELECT repo_group_id FROM augur_data.repo_groups"), db)
    repo_group_IDs = df['repo_group_id'].values.tolist()

    insertSQL = s.sql.text("""
    INSERT INTO "augur_data"."repo_groups"("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (:repo_group_id, :repo_group_name, '', '', 0, CURRENT_TIMESTAMP, 'Unknown', 'Loaded by user', '1.0', 'Git', CURRENT_TIMESTAMP);
    """)

    with open(filename) as create_repo_groups_file:
        data = csv.reader(create_repo_groups_file, delimiter=',')
        for row in data:
            print(f"Trying repo group with name {row[1]} and ID {row[0]}...")
            try:
                if int(row[0]) not in repo_group_IDs:
                    repo_group_IDs.append(int(row[0]))
                    pd.read_sql(insertSQL, db, params={'repo_group_id': int(row[0]), 'repo_group_name': row[1]})
                else:
                    print(f"Repo group with ID {row[1]} for repo group {row[1]} already exists, skipping...")
            except exc.ResourceClosedError as error:
                print(f"Successfully inserted {row[1]}.\n")
                # pd.read_sql() will throw an AttributeError when it can't sucessfully "fetch" any rows from the result.
                # Since there's no rows to fetch after a successful insert, this is how we know it worked.
                # I know it's weird, sue me (jk please don't)

@cli.command('update_repo_directory', short_help="Update Facade worker repo cloning directory")
@click.argument('repo_directory')
@click.pass_context
def update_repo_directory(ctx, repo_directory):
    app = ctx.obj

    db = get_db_connection(app)

    updateRepoDirectorySQL = s.sql.text("""
        UPDATE augur_data.settings SET VALUE = :repo_directory WHERE setting='repo_directory';
    """)

    try:
        pd.read_sql(updateRepoDirectorySQL, db, params={'repo_directory': repo_directory})
    except exc.ResourceClosedError as error:
        print(f"Successfully updated the Facade worker repo directory.")
        # pd.read_sql() will throw an AttributeError when it can't sucessfully "fetch" any rows from the result.
        # Since there's no rows to fetch after a successful insert, this is how we know it worked.
        # I know it's weird, sue me (jk please don't)

@cli.command('create-schema', short_help="Create schema in the configured database")
@click.pass_context
def create_schema(ctx):
    app = ctx.obj
    check_pgpass_credentials(app)
    run_psql_command(app, '-f', 'schema/0-all.sql')

@cli.command('load-data', short_help="Load sample data into the configured database")
@click.pass_context
def load_data(ctx):
    app = ctx.obj
    check_pgpass_credentials(app)
    run_psql_command(app, '-f', 'schema/load_data.sql')

def run_psql_command(app, target_type, target):
    if target_type not in ['-f', '-c']:
        print("Invalid target type. Exiting...")
        exit(1)

    call(['psql', '-h', app.read_config('Database', 'host'),\
      '-d', app.read_config('Database', 'name'),\
      '-U', app.read_config('Database', 'user'),\
      '-p', str(app.read_config('Database', 'port')),\
      '-a', '-w', target_type, target
    ])

def check_pgpass_credentials(app):
     with open(environ['HOME'] + '/.pgpass', 'a+') as pgpass_file:
        end = pgpass_file.tell()
        credentials_string = str(app.read_config('Database', 'host')) \
                          + ':' + str(app.read_config('Database', 'port')) \
                          + ':' + str(app.read_config('Database', 'name')) \
                          + ':' + str(app.read_config('Database', 'user')) \
                          + ':' + str(app.read_config('Database', 'password'))
        pgpass_file.seek(0)
        if credentials_string.lower() not in [''.join(line.split()).lower() for line in pgpass_file.readlines()]:
            print("Database credentials not found in $HOME/.pgpass. Adding credentials...")
            pgpass_file.seek(end)
            pgpass_file.write(credentials_string + '\n')

def get_db_connection(app):

    user = app.read_config('Database', 'user')
    password = app.read_config('Database', 'password')
    host = app.read_config('Database', 'host')
    port = app.read_config('Database', 'port')
    dbname = app.read_config('Database', 'name')
    schema = app.read_config('Database', 'schema')

    DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
    )

    return s.create_engine(DB_STR, poolclass=s.pool.NullPool)


