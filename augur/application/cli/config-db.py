#SPDX-License-Identifier: MIT
"""
Augur library script for generating a db.config.json config file
"""

import os
import click
import json

@click.group('db-config', short_help='Generate an db.config.json')
def cli():
    pass

@cli.command('init')
@click.option('--user', required=True)
@click.option('--password', required=True)
@click.option('--host', required=True)
@click.option('--port', required=True)
@click.option('--database-name', required=True)
def create_db_config(user, password, host, port, database_name):

    db_config = {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database_name": database_name 
    }
    with open('db.config.json', 'w') as fp:
        json.dump(db_config, fp, indent=4)

@cli.command('init-celery')
@click.option('--user', required=True)
def create_celery_config(instance_name):

    celery_config = {
        "instance_name": instance_name
    }

    with open('celery.config.json', 'w') as fp:
        json.dump(celery_config, fp, indent=4)
