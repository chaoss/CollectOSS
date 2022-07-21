#SPDX-License-Identifier: MIT
"""
Augur library script for generating a db.json config file
"""

import os
import click
import json
import logging

logger = logging.getLogger(__name__)

@click.group('db-config', short_help='Generate an augur.config.json')
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
    with open('db.json', 'w') as fp:
        json.dump(db_config, fp)



