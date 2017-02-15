#SPDX-License-Identifier: MIT

from flask import Flask, request, Response, json, send_from_directory
from flask_cors import CORS, cross_origin
import os
import sys
import datetime
if (sys.version_info > (3, 0)):
    import configparser as configparser
else:
    import ConfigParser as configparser
from dateutil import parser, tz
from ghdata import GHData

GHDATA_API_VERSION = 'unstable'

# @todo: Support saving config as a dotfile
class GHDataClient:
    """Wrangles unrefined free-range dataframes into 100% pure JSON"""
    
    def __init__(self, db_host='127.0.0.1', db_port=3306, db_user='root', db_pass='', db_name='ghtorrent', file=None, dataformat=None, start=None, end=None, connect=False, debug=False):
        """Stores configuration of the CLI, which can be set using options at the command line"""
        self.__db_host = db_host
        self.__db_port = db_port
        self.__db_user = db_user
        self.__db_pass = db_pass
        self.__db_name = db_name
        self.__file = file
        self.__dataformat = dataformat

        if (debug == '1'):
            self.DEBUG = True
        else:
            self.DEBUG = False

        if (connect):
            self.__connect()

    def __connect(self):
        try:
            """Connect to the database"""
            if (hasattr(self, '__ghdata') == False):
                self.__dbstr = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(self.__db_user, self.__db_pass, self.__db_host, self.__db_port, self.__db_name)
                self.__ghdata = GHData(self.__dbstr)
        except:
            print('Failed to connect to database using:')
            print(self.__dbstr)

    
    def get(self, key, **args):
        """Interact with ghdata and convert dataframes to JSON"""
        self.__connect()
        data = getattr(self.__ghdata, key)(**args)
        if (hasattr(data, 'to_json')):
            if ('date' in data):
                return data.fillna(0, downcast='infer').to_json(orient='records', date_format='iso', date_unit='s')
            else:
                return data.to_json(orient='records', date_format='iso', date_unit='s')
        else:
            return data
        


def basic_endpoint(flaskapp, table):
    """Simplifies API endpoints that just accept owner, repo, and params"""
    def generated_function(owner, repo):
        repoid = client.get('repoid', owner=owner, repo=repo)
        return Response(response=client.get(table, repoid=repoid),
                status=200,
                mimetype="application/json")
    generated_function.__name__ = table
    return generated_function

# Globals
client = None # Initalized in the base group function below
app = Flask(__name__)
CORS(app)
# Flags and Initialization

def init():
    """Reads the config file"""
    try:
        # Try to open the config file and parse it
        parser = configparser.RawConfigParser()
        parser.read('ghdata.cfg')
        host = parser.get('Database', 'host')
        port = parser.get('Database', 'port')
        user = parser.get('Database', 'user')
        password = parser.get('Database', 'pass')
        db = parser.get('Database', 'name')
        debug = parser.get('Development', 'developer')
        try:
            global client
            client = GHDataClient(db_host=host, db_port=port, db_user=user, db_pass=password, db_name=db, debug=debug)
        except:
            print('Couldn\'t start. Double check ghdata.cfg for errors.')
        
    except IOError:
        # Uh-oh. Save a new config file.
        print('Failed to open config file.')
        config = configparser.RawConfigParser()
        config.add_section('Database')
        config.set('Database', 'host', '127.0.0.1')
        config.set('Database', 'port', '3306')
        config.set('Database', 'user', 'root')
        config.set('Database', 'pass', 'root')
        config.set('Database', 'name', 'ghtorrent')
        config.add_section('Development')
        config.set('Development', 'developer', '0')
        # Writing our configuration file to 'example.cfg'
        with open('ghdata.cfg', 'w') as configfile:
            config.write(configfile)
        print('Default config saved to ghdata.cfg')


    if (client.DEBUG):
        # Serve the front-end files in debug mode to make it easier for developers to work on the interface
        @app.route('/')
        def root():
            return app.send_static_file('frontend/index.html')

        @app.route('/scripts/<path>')
        def send_scripts(path):
            return send_from_directory('frontend/scripts', path)

        @app.route('/styles/<path>')
        def send_styles(path):
            return send_from_directory('frontend/styles', path)

        app.debug = True

    app.run(debug=client.DEBUG)


##################
#     Routes     #
##################

# Serve static files (For development only!)



@app.route('/{}/'.format(GHDATA_API_VERSION))
def api_root():
    """API status"""
    # @todo: When we support multiple data sources this should keep track of their status
    info = Response(response='{"status": "healthy", "ghtorrent": "online"}'.format(GHDATA_API_VERSION),
                    status=200,
                    mimetype="application/json")
    return info

# Timeseries
app.route('/{}/<owner>/<repo>/ts/commits'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'commits'))
app.route('/{}/<owner>/<repo>/ts/forks'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'forks'))
app.route('/{}/<owner>/<repo>/ts/issues'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'issues'))
app.route('/{}/<owner>/<repo>/ts/pulls'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'pulls'))
app.route('/{}/<owner>/<repo>/ts/stargazers'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'stargazers'))

# Contribution Trends
@app.route('/{}/<owner>/<repo>/contribs'.format(GHDATA_API_VERSION))
def contributions(owner, repo):
    repoid = client.get('repoid', owner=owner, repo=repo)
    user = request.args.get('user')
    if (user):
        userid = client.get('userid', username=user)
        contribs = client.get('contributions', repoid=repoid, userid=userid)
    else:
        contribs = client.get('contributions', repoid=repoid)
    return Response(response=contribs,
                    status=200,
                    mimetype="application/json")

if __name__ == '__main__':
    init()