import click
import wget
import os
import sys
import datetime
import json
import csv
from dateutil import parser
from ghdata import GHData

# @todo: Support saving config as a dotfile
class GHDataClient:
    """Stores configuration of the CLI, which can be set using options at the command line"""
    def __init__(self, token=None, username=None, password=None, file=None, dataformat=None, start=None, end=None, now=None):
        if (token):
            self.ghdata = GHData(token)
        if (username and password):
            self.ghdata = GHData(username, password)
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

    def GHDataToText(self, aDict):
        if (self.dataformat == 'json'):
            self.output(json.dumps(GHObj))

    def output(self, text):
        # @todo: Support saving to file
        text = self.GHDataToText(self.ghdata.user())
        click.echo(text)

    def user(username):
        self.output()



# Globals
client = None # Initalized in the base group function below

# Flags and Initialization
@click.group()
@click.option('--token', help='GitHub personal access token')
@click.option('--username', help='GitHub username (if not using tokens)')
@click.option('--password', help='GitHub password (if not using tokens)')
@click.option('--file', type=click.File('wb'), default=False, help='Output file')
@click.option('--format', 'dataformat', default='csv', help='json, csv, or human')
@click.option('--start', default='beginning', help='First date to get data from. Keyword \'beginning\' includes all avaliable historical data (default).')
@click.option('--end', default='now', help='Last date to appear in the data dump. Keyword \'now\' includes realtime data from GitHub API (default).')
@click.option('--now', default=False, is_flag=True, help='Ignore GHTorrent and only interact with the GitHub API. Overrides start/end.')
def cli(token, username, password, file, dataformat, start, end, now):
    """Tool to gather data about GitHub repositories.

    Export the environment variable GITHUB_TOKEN to avoid having to pass it each time.
    To generate a personal access token, go here: https://github.com/settings/tokens/new

    To get help on subcommands, type the command with --help.
    """
    global client
    client = GHDataClient(token, username, password, file, dataformat, start, end, now)




# Get data about a user
@cli.command()
@click.argument('username', default='')
def user(username):
    """Events for a given user"""
    client.user(username)


# Get information about repos, includes subcommands
@cli.group()
def repo(username):
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



# Do
@cli.command(name='download-dump')
@click.option('--url', default='', help='URL of a specific dump')
@click.confirmation_option(prompt='This will download a large database (>40GB compressed). Continue?')
def getdump(url):
    """Downloads the latest GHTorrent MySQL dump"""
    if (url == ''):
        url = 'https://ghtstorage.blob.core.windows.net/downloads/mysql-' + datetime.datetime.now().strftime('%Y-%m') + '-01.tar.gz'

    print('Downloading...' + url)
    wget.download(url)
    
    # @todo: Directly import into database
    click.echo('Downloaded. See https://github.com/gousiosg/github-mirror/tree/master/sql for install instructions.')

# Utility function to stop dangerous operations if user backs out
def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

if __name__ == '__main__':
    cli(auto_envvar_prefix='GITHUB') #Says that we want environment variables prefixed with GITHUB