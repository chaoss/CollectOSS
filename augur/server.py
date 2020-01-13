#SPDX-License-Identifier: MIT
"""
Creates a WSGI server that serves the Augur REST API
"""

import json
import os
import base64
from flask import Flask, request, Response, send_from_directory
from flask_cors import CORS
from flask_login import current_user
import pandas as pd
import augur
from augur.util import annotate, metric_metadata, logger
from augur.routes import create_routes

AUGUR_API_VERSION = 'api/unstable'

class VueCompatibleFlask(Flask):
  jinja_options = Flask.jinja_options.copy()
  jinja_options.update(dict(
    block_start_string='(%',
    block_end_string='%)',
    variable_start_string='%%',
    variable_end_string='%%',
    comment_start_string='(#',
    comment_end_string='#)',
  ))


class Server(object):
    """
    Defines Augur's server's behavior
    """
    def __init__(self, frontend_folder='../frontend/public', manager=None, broker=None, housekeeper=None):
        """
        Initializes the server, creating both the Flask application and Augur application
        """
        # Create Flask application

        self.app = VueCompatibleFlask(__name__, static_folder=frontend_folder, template_folder=frontend_folder)
        self.api_version = AUGUR_API_VERSION
        app = self.app
        CORS(app)
        app.url_map.strict_slashes = False

        # Create Augur application
        self._augur = augur.Application()
        augur_app = self._augur

        # Initialize cache
        expire = int(augur_app.read_config('Server', 'cache_expire', 'AUGUR_CACHE_EXPIRE', 3600))
        self.cache = augur_app.cache.get_cache('server', expire=expire)
        self.cache.clear()

        app.config['SECRET_KEY'] = augur_app.read_config('Server', 'secret_key', 'AUGUR_SECRET_KEY', os.urandom(32))
        app.config['WTF_CSRF_ENABLED'] = False

        self.show_metadata = False

        self.manager = manager
        self.broker = broker
        self.housekeeper = housekeeper

        self.worker_pids = []

        create_routes(self)
        augur_app.metrics.create_routes(self)

        #####################################
        ###          UTILITY              ###
        #####################################

        @app.route('/')
        @app.errorhandler(404)
        @app.errorhandler(405)
        def index(err=None):
            """
            Redirects to health check route
            """
            if AUGUR_API_VERSION in request.url:
                return Response(response=json.dumps({'error': 'Not Found'}),
                            status=404,
                            mimetype="application/json")
            else:

                session_data = {}
                if current_user and hasattr(current_user, 'username'):
                    session_data = { 'username': current_user.username }
                return Response(response=json.dumps(session_data),
                            status=405,
                            mimetype="application/json")#render_template('index.html', session_script=f'window.AUGUR_SESSION={json.dumps(session_data)}\n')

        @app.route('/static/<path:path>')
        def send_static(path):
            return send_from_directory(frontend_folder, path)

        @app.route('/{}/'.format(self.api_version))
        def status():
            """
            Health check route
            """
            status = {
                'status': 'OK',
                'plugins': [p for p in self._augur._loaded_plugins]
            }
            return Response(response=json.dumps(status),
                            status=200,
                            mimetype="application/json")

        """
        @api {post} /batch Batch Requests
        @apiName Batch
        @apiGroup Batch
        @apiDescription Returns results of batch requests
        POST JSON of api requests
        """
        @app.route('/{}/batch'.format(self.api_version), methods=['GET', 'POST'])
        def batch():
            """
            Execute multiple requests, submitted as a batch.
            :statuscode 207: Multi status
            """

            """
            to have on future batch request for each individual chart:
            - timeseries/metric
            - props that are in current card files (title)
            - do any of these things act like the vuex states?
            - what would singular card(dashboard) look like now?
            """

            self.show_metadata = False

            if request.method == 'GET':
                """this will return sensible defaults in the future"""
                return app.make_response('{"status": "501", "response": "Defaults for batch requests not implemented. Please POST a JSON array of requests to this endpoint for now."}')

            try:
                requests = json.loads(request.data.decode('utf-8'))
            except ValueError as e:
                request.abort(400)

            responses = []

            for index, req in enumerate(requests):


                method = req['method']
                path = req['path']
                body = req.get('body', None)

                try:

                    logger.debug('batch-internal-loop: %s %s' % (method, path))

                    with app.app_context():
                        with app.test_request_context(path,
                                                      method=method,
                                                      data=body):
                            try:
                                # Can modify flask.g here without affecting
                                # flask.g of the root request for the batch

                                # Pre process Request
                                rv = app.preprocess_request()

                                if rv is None:
                                    # Main Dispatch
                                    rv = app.dispatch_request()

                            except Exception as e:
                                rv = app.handle_user_exception(e)

                            response = app.make_response(rv)

                            # Post process Request
                            response = app.process_response(response)

                    # Response is a Flask response object.
                    # _read_response(response) reads response.response
                    # and returns a string. If your endpoints return JSON object,
                    # this string would be the response as a JSON string.
                    responses.append({
                        "path": path,
                        "status": response.status_code,
                        "response": str(response.get_data(), 'utf8'),
                    })

                except Exception as e:

                    responses.append({
                        "path": path,
                        "status": 500,
                        "response": str(e)
                    })


            return Response(response=json.dumps(responses),
                            status=207,
                            mimetype="application/json")


        """
        @api {post} /batch Batch Request Metadata
        @apiName BatchMetadata
        @apiGroup Batch
        @apiDescription Returns metadata of batch requests
        POST JSON of API requests metadata
        """
        @app.route('/{}/batch/metadata'.format(self.api_version), methods=['GET', 'POST'])
        def batch_metadata():
            """
            Returns endpoint metadata in batch format
            """

            self.show_metadata = True

            if request.method == 'GET':
                """this will return sensible defaults in the future"""
                return app.make_response(json.dumps(metric_metadata))

            try:
                requests = json.loads(request.data.decode('utf-8'))
            except ValueError as e:
                request.abort(400)

            responses = []

            for index, req in enumerate(requests):

                method = req['method']
                path = req['path']
                body = req.get('body', None)

                try:

                    augur.logger.info('batch endpoint: ' + path)

                    with app.app_context():
                        with app.test_request_context(path,
                                                      method=method,
                                                      data=body):
                            try:
                                # Can modify flask.g here without affecting
                                # flask.g of the root request for the batch

                                # Pre process Request
                                rv = app.preprocess_request()

                                if rv is None:
                                    # Main Dispatch
                                    rv = app.dispatch_request()

                            except Exception as e:
                                rv = app.handle_user_exception(e)

                            response = app.make_response(rv)

                            # Post process Request
                            response = app.process_response(response)

                    # Response is a Flask response object.
                    # _read_response(response) reads response.response
                    # and returns a string. If your endpoints return JSON object,
                    # this string would be the response as a JSON string.

                    responses.append({
                        "path": path,
                        "status": response.status_code,
                        "response": str(response.get_data(), 'utf8'),
                    })

                except Exception as e:

                    responses.append({
                        "path": path,
                        "status": 500,
                        "response": str(e)
                    })

            self.show_metadata = False

            return Response(response=json.dumps(responses),
                            status=207,
                            mimetype="application/json")


    def transform(self, func, args=None, kwargs=None, repo_url_base=None, orient='records',
        group_by=None, on=None, aggregate='sum', resample=None, date_col='date'):
        """
        Serializes a dataframe in a JSON object and applies specified transformations
        """

        if orient is None:
            orient = 'records'

        result = ''

        if not self.show_metadata:

            if repo_url_base:
                kwargs['repo_url'] = str(base64.b64decode(repo_url_base).decode())

            if not args and not kwargs:
                data = func()
            elif args and not kwargs:
                data = func(*args)
            else:
                data = func(*args, **kwargs)

            if hasattr(data, 'to_json'):
                if group_by is not None:
                    data = data.group_by(group_by).aggregate(aggregate)
                if resample is not None:
                    data['idx'] = pd.to_datetime(data[date_col])
                    data = data.set_index('idx')
                    data = data.resample(resample).aggregate(aggregate)
                    data['date'] = data.index
                result = data.to_json(orient=orient, date_format='iso', date_unit='ms')
            else:
                try:
                    result = json.dumps(data)
                except:
                    result = data
        else:
            result = json.dumps(func.metadata)

        return result

    def flaskify(self, func, cache=True):
        """
        Simplifies API endpoints that just accept owner and repo,
        transforms them and spits them out
        """
        if cache:
            def generated_function(*args, **kwargs):
                def heavy_lifting():
                    return self.transform(func, args, kwargs, **request.args.to_dict())
                body = self.cache.get(key=str(request.url), createfunc=heavy_lifting)
                return Response(response=body,
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = func.__class__.__name__ + " _" + func.__name__
            return generated_function
        else:
            def generated_function(*args, **kwargs):
                kwargs.update(request.args.to_dict())
                return Response(response=self.transform(func, args, kwargs, **request.args.to_dict()),
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = func.__class__.__name__ + " _" + func.__name__
            return generated_function

    def routify(self, func, endpoint_type):
        """
        Wraps a metric function allowing it to be mapped to a route,
        get request args and also transforms the metric functions's
        output to json

        :param func: The function to be wrapped
        :param endpoint_type: The type of API endpoint, i.e. 'repo_group' or 'repo'
        """
        def generated_function(*args, **kwargs):
            kwargs.update(request.args.to_dict())

            if 'repo_group_id' not in kwargs:
                kwargs['repo_group_id'] = 1

            data = self.transform(func, args, kwargs)
            return Response(response=data,
                            status=200,
                            mimetype="application/json")
        generated_function.__name__ = f"{endpoint_type}_" + func.__name__
        return generated_function

    def addLicenseMetric(self, function, endpoint, **kwargs):
        endpoint = f'/{self.api_version}/<license_id>/<spdx_binary>/<repo_group_id>/<repo_id>/{endpoint}'
        self.app.route(endpoint)(self.routify(function, 'license_metric'))
        kwargs['endpoint_type'] = 'license_metric'
        self.updateMetricMetadata(function, endpoint, **kwargs)

    def addRepoGroupMetric(self, function, endpoint, **kwargs):
        """Simplifies adding routes that accept repo_group_id"""
        endpoint = f'/{self.api_version}/repo-groups/<repo_group_id>/{endpoint}'
        self.app.route(endpoint)(self.routify(function, 'repo_group'))
        kwargs['endpoint_type'] = 'repo_group'
        self.updateMetricMetadata(function, endpoint, **kwargs)

    def addRepoMetric(self, function, metric_endpoint, **kwargs):
        """Simplifies adding routes that accept repo_group_id and repo_id"""
        endpoint = f'/{self.api_version}/repos/<repo_id>/{metric_endpoint}'
        deprecated_endpoint = f'/{self.api_version}/repo-groups/<repo_group_id>/repos/<repo_id>/{metric_endpoint}'
        self.app.route(endpoint)(self.routify(function, 'repo'))
        self.app.route(deprecated_endpoint)(self.routify(function, 'deprecated_repo'))
        kwargs['endpoint_type'] = 'repo'
        self.updateMetricMetadata(function, endpoint, **kwargs)

    def addMetric(self, function, endpoint, cache=True, **kwargs):
        """Simplifies adding routes that only accept owner/repo"""
        endpoint = '/{}/<owner>/<repo>/{}'.format(self.api_version, endpoint)
        self.app.route(endpoint)(self.flaskify(function, cache=cache))
        self.updateMetricMetadata(function, endpoint, **kwargs)

    def addTimeseries(self, function, endpoint):
        """
        Simplifies adding routes that accept owner/repo and return timeseries

        :param app:       Flask app
        :param function:  Function from a datasource to add
        :param endpoint:  GET endpoint to generate
        """
        self.addMetric(function, 'timeseries/{}'.format(endpoint), metric_type='timeseries')

    def updateMetricMetadata(self, function, endpoint=None, **kwargs):
        """
        Updates a given metric's metadata
        """

        # God forgive me
        #
        # Get the unbound function from the bound function's class so that we can modify metadata
        # across instances of that class.
        real_func = getattr(self._augur.metrics, function.__name__)
        annotate(endpoint=endpoint, **kwargs)(real_func)

    def admin(self):
        return (current_user and current_user.administrator) or (request.args.get('admin_token') == self._augur.read_config('Server', 'admin_token', 'AUGUR_ADMIN_TOKEN', 'changeme'))


def run():
    """
    Runs server with configured hosts/ports
    """
    server = Server()
    host = server._augur.read_config('Server', 'host', 'AUGUR_HOST', '0.0.0.0')
    port = server._augur.read_config('Server', 'port', 'AUGUR_PORT', '5000')
    Server().app.run(host=host, port=int(port), debug=True)


wsgi_app = None
def wsgi(environ, start_response):
    """
    Creates WSGI app
    """
    global wsgi_app
    if (wsgi_app is None):
        app_instance = Server()
        wsgi_app = app_instance.app
    # Stuff to make proxypass work
    script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
    if script_name:
        environ['SCRIPT_NAME'] = script_name
        path_info = environ['PATH_INFO']
        if path_info.startswith(script_name):
            environ['PATH_INFO'] = path_info[len(script_name):]

    scheme = environ.get('HTTP_X_SCHEME', '')
    if scheme:
        environ['wsgi.url_scheme'] = scheme
    server = environ.get('HTTP_X_FORWARDED_SERVER', '')
    if server:
        environ['HTTP_HOST'] = server
    return wsgi_app(environ, start_response)

if __name__ == "__main__":
    run()
