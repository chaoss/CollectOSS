#SPDX-License-Identifier: MIT

from flask import Flask, Response, json
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
        self.__db_host = db_host
        self.__db_port = db_port
        self.__db_user = db_user
        self.__db_pass = db_pass
        self.__db_name = db_name
        self.__file = file
        self.__dataformat = dataformat

        if (connect):
            self.__connect()
        # Parse start time
        """
        if (start == 'earliest'):
            self.__start = None
        elif (start != None):
            self.__start = parser.parse(start, fuzzy=True)
            self.__start = self.start
        
        # Parse end time
        if (end == 'latest'):
            self.__end = None
        else:
            self.__end = parser.parse(end, fuzzy=True)
        """


    def __connect(self):
        if (self.__ghdata):
            self.__dbstr = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(self.db_user, self.db_pass, self.db_host, self.db_port, self.db_name)
            self.__ghdata = GHData(self.dbstr)
         

    """If an attribute doesn't exist, assume it's a GHData method and handle that"""
    def get(self, key, **args):
        self.__connect()
        print(self.__ghdata.__class__.__dict__)
        self.__output(getattr(self.__ghdata, key)(start=self.__start, end=self.__end, **args))



# Globals
client = None # Initalized in the base group function below
app = Flask(__name__)
# Flags and Initialization

def init():
    """Tool to gather data about GitHub repositories.

    Requires the GHTorrent MySQL database (http://ghtorrent.org/).

    To get an up to date copy:  https://github.com/OSSHealth/ghtorrent-sync

    To get help on subcommands, type the command with --help.
    """
    # Read config file if passed
    try:
        parser = configparser.ConfigParser()
        parser.read('ghdata.cfg')
        host = parser.get('Database', 'host')
        port = parser.get('Database', 'port')
        user = parser.get('Database', 'user')
        password = parser.get('Database', 'pass')
        db = parser.get('Database', 'name')
        dataformat = parser.get('Format', 'format')
        global client
        client = GHDataClient(db_host=host, db_port=port, db_user=user, db_pass=password, db_name=db, file=file, dataformat=dataformat)
        app.run()
    except:
        print('Failed to open config file.')
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
        with open('ghdata.cfg', 'wb') as configfile:
            config.write(configfile)
        print('Default config saved to ghdata.cfg')
    

"""

"""


@app.route('/')
def root():
    info = Response(response='{"status": "active"}',
                    status=200,
                    mimetype="application/json")
    return info

@app.route('/user/:username')
def user(username):
    return ''

# Generates a default config file
def create_default_config(username):
    """Generates default .cfg file"""
    


if __name__ == '__main__':
    init()