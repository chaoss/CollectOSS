import csv
import click
import sqlalchemy as s
import pandas as pd

from augur.application import Application
from augur.runtime import pass_application

@click.group('db', short_help='Database maintenance')
def cli():
    pass

@cli.command('add_repos', short_help="Add repositories to Augur's database")
@click.argument('filename', type=click.Path(exists=True))
@pass_application
def add_repos(app, filename):

    app = Application()

    user = app.read_config('Database', 'user', 'AUGUR_DB_USER', 'augur')
    password = app.read_config('Database', 'password', 'AUGUR_DB_PASS', 'password')
    host = app.read_config('Database', 'host', 'AUGUR_DB_HOST', '127.0.0.1')
    port = app.read_config('Database', 'port', 'AUGUR_DB_PORT', '5433')
    dbname = app.read_config('Database', 'database', 'AUGUR_DB_NAME', 'augur')
    schema = app.read_config('Database', 'schema', 'AUGUR_DB_SCHEMA', 'augur_data')

    DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
    )

    db = s.create_engine(DB_STR, poolclass=s.pool.NullPool)

    insertSQL = """
        INSERT INTO augur_data.repo(repo_group_id, repo_git, repo_status, 
        tool_source, tool_version, data_source, data_collection_date) 
        VALUES (:repo_group_id, :repo_git, 'New', 'CLI', 1.0, 'Git', CURRENT_TIMESTAMP)
    """

    with open(filename) as upload_repos_file:
        data = csv.reader(upload_repos_file, delimiter=',')
        for row in data:
            print(f"Adding repo with Git URL `{row[1]}` to repo group {row[0]}...")
            # pd.read_sql(insertSQL, db, params={'repo_group_id': row[0], 'repo_id': row[1]})
