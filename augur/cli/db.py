from os import walk, chdir, environ
from sys import exit
from collections import OrderedDict
from subprocess import call
import csv
import click
import sqlalchemy as s
import pandas as pd
from sqlalchemy import exc

@click.group('db', short_help='Database utilities')
def cli():
    pass

@cli.command('add-repos', short_help="Add repositories to Augur's database")
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

@cli.command('get-repo-groups', short_help="List all repo groups and their associated IDs")
@click.pass_context
def get_repo_groups(ctx):
    app = ctx.obj

    db = get_db_connection(app)

    df = pd.read_sql(s.sql.text("SELECT repo_group_id, rg_name, rg_description FROM augur_data.repo_groups"), db)
    print(df)

    return df

@cli.command('add-repo-groups', short_help="Create new repo groups in Augur's database")
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

@cli.command('update-repo-directory', short_help="Update Facade worker repo cloning directory")
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

@cli.command('version', short_help="Get the version of the configured database")
@click.pass_context
def print_db_version(ctx):
    print(f"Augur DB version: {get_db_version(ctx.obj)}")

@cli.command('upgrade', short_help="Upgrade the configured database to the latest version")
@click.pass_context
def upgrade_db_version(ctx):
    current_db_version = get_db_version(ctx.obj)

    update_scripts_filenames = []
    for (_, _, filenames) in walk('schema/generate'):
        update_scripts_filenames.extend([file for file in filenames if 'update' in file])
        # files_temp.extend([file.split("-")[1][14:].split(".")[0] for file in filenames if 'update' in file])
        break

    target_version_script_map = {}
    for script in update_scripts_filenames:
        upgrades_to = int(script.split("-")[1][14:].split(".")[0])
        target_version_script_map[upgrades_to] = str(script)

    target_version_script_map = OrderedDict(sorted(target_version_script_map.items()))

    most_recent_version = list(target_version_script_map.keys())[-1]
    if current_db_version == most_recent_version:
        print("Your database is already up to date. ")
    elif current_db_version > most_recent_version:
        print(f"Unrecognized version: {current_db_version}\nThe most recent version is {most_recent_version}. Please contact your system administrator to resolve this error.")

    for target_version, script_location in target_version_script_map.items():
        if target_version == current_db_version + 1:
            print("Upgrading from", current_db_version, "to", target_version)
            run_psql_command_in_database(ctx.obj, '-f', f"schema/generate/{script_location}")
            current_db_version += 1

def get_db_version(app):
    db = get_db_connection(app)

    db_version_sql = s.sql.text("""
        SELECT * FROM augur_operations.augur_settings WHERE setting = 'augur_data_version'
    """)

    return int(db.execute(db_version_sql).fetchone()[2])

@cli.command('create-schema', short_help="Create schema in the configured database")
@click.pass_context
def create_schema(ctx):
    app = ctx.obj
    check_pgpass_credentials(app.config)
    run_psql_command_in_database(app, '-f', 'schema/create_schema.sql')

@cli.command('load-data', short_help="Load sample data into the configured database")
@click.pass_context
def load_data(ctx):
    app = ctx.obj
    check_pgpass_credentials(app.config)
    run_psql_command_in_database(app, '-f', 'schema/sample_data/load_sample_data.sql')

@cli.command('check-pgpass', short_help="Check the ~/.pgpass file for Augur's database credentials")
@click.pass_context
def load_data(ctx):
    app = ctx.obj
    check_pgpass_credentials(app.config)

@cli.command('init-database', short_help="Create database on the configured port")
@click.option('--default-db-name', default='postgres')
@click.option('--default-user', default='postgres')
@click.option('--default-password', default='postgres')
@click.option('--target-db-name', default='augur')
@click.option('--target-user', default='augur')
@click.option('--target-password', default='augur')
@click.option('--host', default='localhost')
@click.option('--port', default='5432')
@click.pass_context
def init_database(ctx, default_db_name, default_user, default_password, target_db_name, target_user, target_password, host, port):
    app = ctx.obj
    config = {
        'Database': {
            'name': default_db_name,
            'user': default_user,
            'password': default_password,
            'host': host,
            'port': port
        }
    }
    check_pgpass_credentials(config)
    run_db_creation_psql_command(host, port, default_user, default_db_name, f'CREATE DATABASE {target_db_name};')
    run_db_creation_psql_command(host, port, default_user, default_db_name, f'CREATE USER {target_user} WITH ENCRYPTED PASSWORD \'{target_password}\';')
    run_db_creation_psql_command(host, port, default_user, default_db_name, f'ALTER DATABASE {target_db_name} OWNER TO {target_user};')
    run_db_creation_psql_command(host, port, default_user, default_db_name, f'GRANT ALL PRIVILEGES ON DATABASE {target_db_name} TO {target_user};')

def run_db_creation_psql_command(host, port, user, name, command):
    call(['psql', '-h', host, '-p', port, '-U', user, '-d', name, '-a', '-w', '-c', command])

def run_psql_command_in_database(app, target_type, target):
    if target_type not in ['-f', '-c']:
        print("Invalid target type. Exiting...")
        exit(1)

    call(['psql', '-h', app.read_config('Database', 'host'),\
      '-d', app.read_config('Database', 'name'),\
      '-U', app.read_config('Database', 'user'),\
      '-p', str(app.read_config('Database', 'port')),\
      '-a', '-w', target_type, target
    ])

def check_pgpass_credentials(config):
    with open(environ['HOME'] + '/.pgpass', 'a+') as pgpass_file:
        end = pgpass_file.tell()
        credentials_string = str(config['Database']['host']) \
                          + ':' + str(config['Database']['port']) \
                          + ':' + str(config['Database']['name']) \
                          + ':' + str(config['Database']['user']) \
                          + ':' + str(config['Database']['password'])
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


