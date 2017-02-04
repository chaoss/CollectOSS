#SPDX-License-Identifier: MIT

import click
import os
import sys
import datetime
if (sys.version_info > (3, 0)):
    import configparser as configparser
else:
    import ConfigParser as configparser
from dateutil import parser, tz
from ghdata import GHData

# @todo: Support saving config as a dotfile
class GHDataClient:
    """Stores configuration of the CLI, which can be set using options at the command line"""
    def __init__(self, db_host='127.0.0.1', db_port=3306, db_user='root', db_pass='', db_name='ghtorrent', file=None, dataformat=None, start=None, end=None, connect=False):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        self.file = file
        self.dataformat = dataformat

        if (connect):
            self.connect()
        # Parse start time
        if (start == 'earliest'):
            self.start = None
        elif (start != None):
            self.start = parser.parse(start, fuzzy=True)
            self.start = self.start
        
        # Parse end time
        if (end == 'latest'):
            self.end = None
        else:
            self.end = parser.parse(end, fuzzy=True)

    def connect(self):
        self.dbstr = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(self.db_user, self.db_pass, self.db_host, self.db_port, self.db_name)
        self.ghdata = GHData(self.dbstr)

    def output(self, obj):
        click.echo(obj.export(self.dataformat))

    def user(self, username):
        self.output(self.ghdata.user(username, self.start, self.end))



# Globals
client = None # Initalized in the base group function below
# Flags and Initialization
@click.group()
@click.option('--host', default='127.0.0.1', help='Database host (default: localhost)')
@click.option('--port', default='3306', help='Database port (default: 3306)')
@click.option('--db', default='ghtorrent', help='Database name (default: ghtorrent)')
@click.option('--user', default='root', help='Database user (default: root)')
@click.option('--password', default='root', help='Database pass (default: root)')
@click.option('--file', type=click.File('wb'), default=sys.stdout, help='Output file')
@click.option('--config', type=click.File('rb'), help='Configuration file')
@click.option('--format', 'dataformat', default='csv', help='csv (default), json, yaml, json, xls, xlsx, human')
@click.option('--start', default='earliest', help='First date to get data from. Keyword \'earliest\' includes oldest data (default).')
@click.option('--end', default='latest', help='Last date to get data from. Keyword \'latest\' includes newest data (default)' )
def cli(host, port, db, user, password, file, config, dataformat, start, end):
    """Tool to gather data about GitHub repositories.

    Requires the GHTorrent MySQL database (http://ghtorrent.org/).

    To get an up to date copy:  https://github.com/OSSHealth/ghtorrent-sync

    To get help on subcommands, type the command with --help.
    """
    # Read config file if passed
    if (config):
        parser = configparser.ConfigParser()
        parser.readfp(config)
        host = parser.get('Database', 'host')
        port = parser.get('Database', 'port')
        user = parser.get('Database', 'user')
        password = parser.get('Database', 'pass')
        db = parser.get('Database', 'name')
        dataformat = parser.get('Format', 'format')

    global client
    
    client = GHDataClient(db_host=host, db_port=port, db_user=user, db_pass=password, db_name=db, file=file, dataformat=dataformat, start=start, end=end)




# Get data about a user
@cli.command()
@click.argument('username', default='')
def user(username):
    """Events for a given user"""
    client.connect()
    client.user(username)


# Get information about repos, includes subcommands
@cli.group()
def repo():
    """Events for a given repository"""
    # @todo: All events related to a repo
    return

@repo.command()
@click.argument('repo', default='')
def commits(username):
    # @todo: Releases
    return

@repo.command()
@click.argument('repo', default='')
def starring(username):
    # @todo: Stargazers and when they started starring
    return

@repo.command()
@click.argument('repo', default='')
def forks(username):
    # @todo: Fork timeseries
    return

@repo.command()
@click.option('--with-comments', 'comments', is_flag=True, default=False)
@click.argument('repo', default='')
def pullrequests(comments, username):
    # @todo: Pull requests and their events
    return

@repo.command()
@click.argument('repo', default='')
def issues(username):
    # @todo: Issues and their metadata
    return

@repo.command()
@click.argument('repo', default='')
def statistics(username):
    # @todo: Statistics from the Statistics API
    return

@repo.command()
@click.argument('repo', default='')
def releases(username):
    # @todo: Releases
    return

# Generates a default config file
@cli.command(name="create-default-config")
@click.argument('username', default='')
def create_default_config(username):
    """Generates default .cfg file"""
    config = configparser.RawConfigParser()
    config.add_section('Database')
    config.set('Database', 'host', '127.0.0.1')
    config.set('Database', 'port', '3306')
    config.set('Database', 'user', 'root')
    config.set('Database', 'pass', 'root')
    config.set('Database', 'name', 'ghtorrent')
    config.add_section('Format')
    config.set('Format', 'format', 'csv')
    # Writing our configuration file to 'example.cfg'
    with open('default.cfg', 'wb') as configfile:
        config.write(configfile)
    click.echo('Default config saved to default.cfg')


if __name__ == '__main__':
    cli(auto_envvar_prefix='GHDATA') #Says that we want environment variables prefixed with GHDATA