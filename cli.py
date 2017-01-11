import click
import wget
import os
import sys
import datetime
from dateutil import parser
from ghdata import GHData

# Stores configuration of the CLI, which can be set using options at the command line
# TODO: Support saving config as a dotfile
class Config:
    def __init__(self, token=None, username=None, password=None, file=None, dataformat=None, start=None, end=None, now=None):
        self.token = token
        self.username = username
        self.password = password
        self.file = file
        self.dataformat = dataformat
        self.now = now

        #Parse start time
        print(start)
        if (start == 'beginning'):
            self.start = None
        elif (start != None):
            self.start = parser.parse(start, fuzzy=True)
        
        #Parse end time
        if (end == 'now'):
            self.end = None
        else:
            self.end = parser.parse(end, fuzzy=True)

# Globals
client = None
config = None

# Flags and Initialization
@click.group()
@click.option('--token', help='GitHub personal access token')
@click.option('--username', help='GitHub username (if not using tokens)')
@click.option('--password', help='GitHub password (if not using tokens)')
@click.option('--file', type=click.File('wb'), default=False, help='output file')
@click.option('--format', 'dataformat', default='csv', help='json, csv, or human')
@click.option('--start', default='beginning', help='First date to get data from. \'beginning\' includes all data (default).')
@click.option('--end', default='now', help='Last date to appear in the data dump. \'now\' includes current data from GitHub API (default).')
@click.option('--now', default=False, is_flag=True, help='Ignore GHTorrent and only interact with the GitHub API. Overrides start/end.')
def cli(token, username, password, file, dataformat, start, end, now):
    """Tool to gather data about GitHub repositories.

    Export the environment variable GITHUB_TOKEN to avoid having to pass it each time.
    To generate a personal access token, go here: https://github.com/settings/tokens/new
    """
    global client, config
    config = Config(token, username, password, file, dataformat, start, end, now)
    if (token):
        client = GHData(token)
    if (username and password):
        client = GHData(username, password)
    

# Get data about a user
@cli.command()
@click.argument('username', default='')
def user(username):
        print(client.user(username=username, start=config.start, end=config.end))

# Do
@cli.command()
@click.option('--url', default='', help='URL of a specific dump')
@click.confirmation_option(prompt='This will download a large database (>40GB compressed). Continue?')
def getdump(url):
    """Downloads the latest GHTorrent MySQL dump"""
    if (url == ''):
        url = 'https://ghtstorage.blob.core.windows.net/downloads/mysql-' + datetime.datetime.now().strftime('%Y-%m') + '-01.tar.gz'

    print('Downloading...' + url)
    wget.download(url)
    
    # TODO: Directly import into database
    click.echo('Downloaded. See https://github.com/gousiosg/github-mirror/tree/master/sql for install instructions.')

# Utility function to stop dangerous operations if user backs out
def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

if __name__ == '__main__':
    cli(auto_envvar_prefix='GITHUB') #Says that we want environment variables prefixed with GITHUB