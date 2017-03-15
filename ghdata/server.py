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
    """
    Reads the configuration file, creates an instance of GHData, serializes dataframes into JSON
    """

    def __init__(self, db_host='127.0.0.1', db_port=3306, db_user='root', db_pass='', db_name='ghtorrent', public_www_api_key=None, file=None, connect=False, debug=False):
        """
        Stores configuration, optionally connects to the database
        """
        self.__db_host = db_host
        self.__db_port = db_port
        self.__db_user = db_user
        self.__db_pass = db_pass
        self.__db_name = db_name
        self.__public_www_api_key = public_www_api_key
        self.__file = file

        if (debug == '1'):
            self.DEBUG = True
        else:
            self.DEBUG = False

        if (connect):
            self.__connect()

    def __connect(self):
        """
        Generates the dbstr from the configuration loaded earlier, opens the connection
        """
        try:
            if (hasattr(self, '__ghdata') == False):
                self.__dbstr = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(self.__db_user, self.__db_pass, self.__db_host, self.__db_port, self.__db_name)
                self.__ghdata = GHData(dbstr=self.__dbstr, public_www_api_key=self.__public_www_api_key)
        except:
            print('Failed to connect to database using:')
            print(self.__dbstr)


    def get(self, key, **args):
        # Interact with ghdata and convert dataframes to JSON
        self.__connect()
        data = getattr(self.__ghdata, key)(**args)
        if (hasattr(data, 'to_json')):
            return data.to_json(orient='records', date_format='iso', date_unit='ms')
        else:
            return data



def basic_endpoint(flaskapp, table):
    """
    Simplifies API endpoints that just accept owner and repo
    """
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
        public_www_api_key = parser.get('PublicWWW', 'APIKey')
        debug = parser.get('Development', 'developer')
        try:
            global client
            client = GHDataClient(db_host=host, db_port=port, db_user=user, db_pass=password, db_name=db, public_www_api_key=public_www_api_key, debug=debug)
        except:
            print('Couldn\'t start. Double check ghdata.cfg for errors.')

    except:
        # Uh-oh. Save a new config file.
        print('Failed to open config file.')
        config = configparser.RawConfigParser()
        config.add_section('Database')
        config.set('Database', 'host', '127.0.0.1')
        config.set('Database', 'port', '3306')
        config.set('Database', 'user', 'root')
        config.set('Database', 'pass', 'root')
        config.set('Database', 'name', 'ghtorrent')
        config.add_section('PublicWWW')
        config.set('PublicWWW', 'APIKey', '0')
        config.add_section('Development')
        config.set('Development', 'developer', '0')
        # Writing our configuration file to 'example.cfg'
        with open('ghdata.cfg', 'w') as configfile:
            config.write(configfile)
        print('Default config saved to ghdata.cfg')
        sys.exit()


    if (client.DEBUG):
        # Serve the front-end files in debug mode to make it easier for developers to work on the interface
        # @todo: Figure out why this isn't working.
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


"""
@api {get} / API Status
@apiName Status
@apiGroup Misc
"""
@app.route('/{}/'.format(GHDATA_API_VERSION))
def api_root():
    """API status"""
    # @todo: When we support multiple data sources this should keep track of their status
    info = Response(response='{"status": "healthy", "ghtorrent": "online"}'.format(GHDATA_API_VERSION),
                    status=200,
                    mimetype="application/json")
    return info

#######################
#     Timeseries      #
#######################

"""
@api {get} /:owner/:repo/commits Commits by Week
@apiName CommitsByWeek
@apiGroup Timeseries

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2015-01-01T00:00:00.000Z", 
                            "commits": 153
                        }, 
                        {
                            "date": "2015-01-08T00:00:00.000Z",
                            "commits": 192
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/timeseries/commits'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'commits'))

"""
@api {get} /:owner/:repo/forks Forks by Week
@apiName ForksByWeek
@apiGroup Timeseries

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2015-01-01T00:00:00.000Z", 
                            "forks": 13
                        }, 
                        {
                            "date": "2015-01-08T00:00:00.000Z",
                            "forks": 12
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/timeseries/forks'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'forks'))

"""
@api {get} /:owner/:repo/issues Issues by Week
@apiName IssuesByWeek
@apiGroup Timeseries

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2015-01-01T00:00:00.000Z", 
                            "issues":13
                        }, 
                        {
                            "date": "2015-01-08T00:00:00.000Z",
                            "issues":15
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/timeseries/issues'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'issues'))

"""
@api {get} /:owner/:repo/issues/response_time Response Time for Issues
@apiName IssueResponseTime
@apiGroup Timeseries

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            "created_at": "2013-09-16T17:00:54.000Z",
                            "responded_at": "2013-09-16T17:20:58.000Z"
                        },
                        {
                            "created_at": "2013-09-16T09:31:34.000Z",
                            "responded_at": "2013-09-16T09:43:03.000Z"
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/timeseries/issues/response_time'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'issue_response_time'))

"""
@api {get} /:owner/:repo/pulls Pull Requests by Week
@apiName PullRequestsByWeek
@apiGroup Timeseries

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2015-01-01T00:00:00.000Z", 
                            "pull_requests": 1
                            "comments": 11
                        }, 
                        {
                            "date": "2015-01-08T00:00:00.000Z",
                            "pull_requests": 2
                            "comments": 31
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/timeseries/pulls'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'pulls'))

"""
@api {get} /:owner/:repo/stargazers Stargazers by Week
@apiName StargazersByWeek
@apiGroup Timeseries

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2015-01-01T00:00:00.000Z", 
                            "watchers": 133
                        }, 
                        {
                            "date": "2015-01-08T00:00:00.000Z",
                            "watchers": 54
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/timeseries/stargazers'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'stargazers'))

"""
@api {get} /:owner/:repo/pulls/acceptance_rate Pull Request Acceptance Rate by Week
@apiDescription For each week, the rate is calculated as (pull requests merged that week) / (pull requests opened that week)
@apiName Stargazers
@apiGroup Timeseries

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2015-01-01T00:00:00.000Z", 
                            "rate": 0.5
                        }, 
                        {
                            "date": "2015-01-08T00:00:00.000Z",
                            "rate": 0.33
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/pulls/acceptance_rate'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'pull_acceptance_rate'))

# Contribution Trends
"""
@api {get} /:owner/:repo/contributors Total Contributions by User
@apiName TotalContributions
@apiGroup Users

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                   [
                        {
                            "login": "foo",
                            "location": "Springfield",
                            "commits": 1337.0,
                            "pull_requests": 60.0,
                            "issues": null,
                            "commit_comments": 158.0,
                            "pull_request_comments": 718.0,
                            "issue_comments": 1668.0
                        },
                        {
                            "login": "bar",
                            "location": null,
                            "commits": 3968.0,
                            "pull_requests": null,
                            "issues": 12.0,
                            "commit_comments": 158.0,
                            "pull_request_comments": 718.0,
                            "issue_comments": 1568.0
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/contributors'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'contributors'))

#######################
# Contribution Trends #
#######################

"""
@api {get} /:owner/:repo/contributions Contributions by Week
@apiName ContributionsByWeek
@apiGroup Timeseries

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository
@apiParam (String) user Limit results to the given user's contributions

@apiSuccessExample {json} Success-Response:
                   [
                        {
                            "date": "2015-01-01T00:00:00.000Z", 
                            "commits": 37.0,
                            "pull_requests": null,
                            "issues": null,
                            "commit_comments": 7.0,
                            "pull_request_comments": 8.0,
                            "issue_comments": 17.0
                        },
                        {
                            "date": "2015-01-08T00:00:00.000Z", 
                            "commits": 68.0,
                            "pull_requests": null,
                            "issues": 12.0,
                            "commit_comments": 18.0,
                            "pull_request_comments": 13.0,
                            "issue_comments": 28.0
                        }
                    ]
"""
@app.route('/{}/<owner>/<repo>/contributions'.format(GHDATA_API_VERSION))
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

# Diversity

"""
@api {get} /:owner/:repo/commits/locations Commits and Location by User
@apiName Stargazers
@apiGroup Diversity

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            "login": "bonnie",
                            "location": "Rowena, TX",
                            "commits": 12
                        },
                        {   
                            "login":"clyde",
                            "location":"Ellis County, TX",
                            "commits": 12
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/commits/locations'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'committer_locations'))

# Popularity
"""
@api {get} /:owner/:repo/linking_websites Linking Websites
@apiDescription Returns an array of websites and their rank according to http://publicwww.com/
@apiName LinkingWebsites
@apiGroup Popularity

@apiParam {String} owner Username of the owner of the GitHub repository
@apiParam {String} repo Name of the GitHub repository

@apiSuccessExample {json} Success-Response:
                    [
                        {
                            "url": "missouri.edu",
                            "rank": "1"
                        },
                        {
                            "url": "unomaha.edu",
                            "rank": "2"
                        }
                    ]
"""
app.route('/{}/<owner>/<repo>/linking_websites'.format(GHDATA_API_VERSION))(basic_endpoint(app, 'linking_websites'))

if __name__ == '__main__':
    init()
