#SPDX-License-Identifier: MIT
import ghdata

import os
import sys
if (sys.version_info > (3, 0)):
    import configparser as configparser
else:
    import ConfigParser as configparser

from flask import Flask, request, Response, send_from_directory
from flask_cors import CORS

GHDATA_API_VERSION = 'unstable'

def serialize(func, **args):
    """
    Serailizes a function that returns a dataframe
    """
    data = func(**args)
    if hasattr(data, 'to_json'):
        return data.to_json(orient='records', date_format='iso', date_unit='ms')
    else:
        return data


def flaskify_ghtorrent(ghtorrent, func):
    """
    Simplifies API endpoints that just accept owner and repo,
    serializes them and spits them out
    """
    def generated_function(owner, repo):
        repoid = ghtorrent.repoid(owner=owner, repo=repo)
        return Response(response=serialize(func, repoid=repoid),
                        status=200,
                        mimetype="application/json")
    generated_function.__name__ = func.__name__
    return generated_function

def flaskify(func):
    """
    Simplifies API endpoints that just accept owner and repo,
    serializes them and spits them out
    """
    def generated_function(owner, repo):
        return Response(response=serialize(func, owner=owner, repo=repo),
                        status=200,
                        mimetype="application/json")
    generated_function.__name__ = func.__name__
    return generated_function

def read_config(parser, section, name, environment_variable, default):
    try:
        value = os.getenv(environment_variable, parser.get(section, name))
        return value
    except:
        if not parser.has_section(section):
            parser.add_section(section)
        parser.set(section, name, default)
        with open('ghdata.cfg', 'w') as configfile:
            parser.write(configfile)
        return default


def run(): 

    app = Flask(__name__)
    CORS(app)
    # Try to open the config file and parse it
    parser = configparser.RawConfigParser()
    parser.read('ghdata.cfg')

    try:
        dbstr = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
            read_config(parser, 'Database', 'user', 'GHDATA_DB_USER', 'root'),
            read_config(parser, 'Database', 'pass', 'GHDATA_DB_PASS', 'password'),
            read_config(parser, 'Database', 'host', 'GHDATA_DB_HOST', '127.0.0.1'),
            read_config(parser, 'Database', 'port', 'GHDATA_DB_PORT', '3306'),
            read_config(parser, 'Database', 'name', 'GHDATA_DB_NAME', 'msr14')
        )
        print("Connecting with " + dbstr)
        ghtorrent = ghdata.GHTorrent(dbstr=dbstr)
    except Exception as e:
        print("Failed to connect to database (" + str(e) + ")");

    host = read_config(parser, 'Server', 'host', 'GHDATA_HOST', '0.0.0.0')
    port = read_config(parser, 'Server', 'port', 'GHDATA_PORT', '5000')

    publicwww = ghdata.PublicWWW(api_key=read_config(parser, 'PublicWWW', 'APIKey', 'GHDATA_PUBLIC_WWW_API_KEY', 'None'))
    github = ghdata.GitHubAPI(api_key=read_config(parser, 'GitHub', 'APIKey', 'GHDATA_GITHUB_API_KEY', 'None'))

    if (read_config(parser, 'Development', 'developer', 'GHDATA_DEBUG', '0') == '1'):
        debugmode = True
    else:
        debugmode = False



    """
    @api {get} / API Status
    @apiName Status
    @apiGroup Misc
    """
    @app.route('/{}/'.format(GHDATA_API_VERSION))
    def api_root():
        """API status"""
        # @todo: When we support multiple data sources this should keep track of their status
        # @todo: Add GHTorrent test to determine status
        ghtorrent_status = "good"
        # @todo: Add GitHub API status
        # @todo: Add PublicWWW API status
        return """{"status": "healthy", "ghtorrent": "{}"}""".format(ghtorrent_status)

    #######################
    #     Timeseries      #
    #######################

    # @todo: Link to LF Metrics

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
    app.route('/{}/<owner>/<repo>/timeseries/commits'.format(GHDATA_API_VERSION))(
        flaskify_ghtorrent(ghtorrent, ghtorrent.commits))

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
    app.route('/{}/<owner>/<repo>/timeseries/forks'.format(GHDATA_API_VERSION))(
        flaskify_ghtorrent(ghtorrent, ghtorrent.forks))

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
    app.route('/{}/<owner>/<repo>/timeseries/issues'.format(GHDATA_API_VERSION))(
        flaskify_ghtorrent(ghtorrent, ghtorrent.issues))

    """
    @api {get} /:owner/:repo/issues/response_time Issue Response Time
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
    app.route('/{}/<owner>/<repo>/timeseries/issues/response_time'.format(GHDATA_API_VERSION))(
        flaskify_ghtorrent(ghtorrent, ghtorrent.issue_response_time))

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
    app.route('/{}/<owner>/<repo>/timeseries/pulls'.format(GHDATA_API_VERSION))(
        flaskify_ghtorrent(ghtorrent, ghtorrent.pulls))

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
    app.route('/{}/<owner>/<repo>/timeseries/stargazers'.format(GHDATA_API_VERSION))(
        flaskify_ghtorrent(ghtorrent, ghtorrent.stargazers))

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
    app.route('/{}/<owner>/<repo>/pulls/acceptance_rate'.format(GHDATA_API_VERSION))(
        flaskify_ghtorrent(ghtorrent, ghtorrent.pull_acceptance_rate))

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
    app.route('/{}/<owner>/<repo>/contributors'.format(GHDATA_API_VERSION))(
        flaskify_ghtorrent(ghtorrent, ghtorrent.contributors))

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
        repoid = ghtorrent.repoid(owner=owner, repo=repo)
        user = request.args.get('user')
        if (user):
            userid = ghtorrent.userid(username=user)
            contribs = ghtorrent.contributions(repoid=repoid, userid=userid)
        else:
            contribs = ghtorrent.contributions(repoid=repoid)
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
    app.route('/{}/<owner>/<repo>/commits/locations'.format(GHDATA_API_VERSION))(
        flaskify_ghtorrent(ghtorrent, ghtorrent.committer_locations))

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
    app.route('/{}/<owner>/<repo>/linking_websites'.format(GHDATA_API_VERSION))(flaskify(publicwww.linking_websites))


    if (debugmode):
        print(" * Serving static routes")
        # Serve the front-end files in debug mode to make it easier for developers to work on the interface
        # @todo: Figure out why this isn't working.
        @app.route('/')
        def index():
            root_dir = os.path.dirname(os.getcwd())
            print(root_dir + '/ghdata/static')
            return send_from_directory(root_dir + '/ghdata/ghdata/static', 'index.html')

        @app.route('/scripts/<path>')
        def send_scripts(path):
            root_dir = os.path.dirname(os.getcwd())
            return send_from_directory(root_dir + '/ghdata/ghdata/static/scripts', path)

        @app.route('/styles/<path>')
        def send_styles(path):
            root_dir = os.path.dirname(os.getcwd())
            return send_from_directory(root_dir+ '/ghdata/ghdata/static/styles', path)

        app.debug = True

    app.run(host=host, port=int(port), debug=debugmode)

if __name__ == '__main__':
    run()