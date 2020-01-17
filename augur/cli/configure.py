#SPDX-License-Identifier: MIT
"""
Augur library script for generating a config file
"""

import os
import click
import json

ENVVAR_PREFIX = "AUGUR_"

@click.group('configure', short_help='Generate an augur.config.json')
def cli():
    pass

@cli.command('generate', short_help='Generate an augur.config.json')
@click.option('--db_name', help="Database name for your data collection database", envvar=ENVVAR_PREFIX + 'DB_NAME')
@click.option('--db_host', help="Host for your data collection database", envvar=ENVVAR_PREFIX + 'DB_HOST')
@click.option('--db_user', help="User for your data collection database", envvar=ENVVAR_PREFIX + 'DB_USER')
@click.option('--db_port', help="Port for your data collection database", envvar=ENVVAR_PREFIX + 'DB_PORT')
@click.option('--db_password', help="Password for your data collection database", envvar=ENVVAR_PREFIX + 'DB_PASSWORD')
@click.option('--github_api_key', help="GitHub API key for data collection from the GitHub API", envvar=ENVVAR_PREFIX + 'GITHUB_API_KEY')
@click.option('--facade_repo_directory', help="Directory on the database server where Facade should clone repos", envvar=ENVVAR_PREFIX + 'FACADE_REPO_DIRECTORY')
def generate(db_name, db_host, db_user, db_port, db_password, github_api_key, facade_repo_directory):
    config = None

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    try:
        with open('../default.config.json') as default_config:
            config = json.load(default_config)
    except Exception as e:
        print("Error reading default.config.json " + str(e))

    if db_name is not None:
        config['Database']['database'] = db_name
    if db_host is not None:
        config['Database']['host'] = db_host
    if db_port is not None:
        config['Database']['port'] = db_port
    if db_user is not None:
        config['Database']['user'] = db_user
    if db_password is not None:
        config['Database']['password'] = db_password
    if github_api_key is not None:
        config['Database']['key'] = github_api_key
    if facade_repo_directory is not None:
        config['Workers']['facade_worker']['repo_directory'] = facade_repo_directory

    config['Database']['schema'] = "augur_data"

    try:
        with open('../../augur.config.json', 'w') as f:
            f.write(json.dumps(config, indent=4))
            print('augur.config.json successfully created')
    except Exception as e:
        print("Error writing augur.config.json " + str(e))

# @cli.command('env', short_help='Generate a default augur.config.json from environment variables')
    """
    Generate a default augur.config.json from an environment file or the CLI
    """

