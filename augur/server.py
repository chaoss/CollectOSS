#SPDX-License-Identifier: MIT
"""
Creates a WSGI server that serves the Augur REST API
"""

import json
import base64
from flask import Flask, request, Response, redirect, url_for, send_from_directory
from flask_cors import CORS
import pandas as pd
import augur
from augur.util import annotate, metric_metadata, logger
from augur.routes import create_plugin_routes

AUGUR_API_VERSION = 'api/unstable'

class Server(object):
    """
    Defines Augur's server's behavior
    """
    def __init__(self):
        """
        Initializes the server, creating both the Flask application and Augur application
        """
        # Create Flask application
        self.app = Flask(__name__, static_folder='../frontend/public')
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

        self.show_metadata = False

        create_plugin_routes(self)

        # this needs to be the last route creation function called so that all the metrics have their metadata updated
        # create_metrics_status_routes(self)

        #####################################
        ###          UTILITY              ###
        #####################################

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def index(path):
            """
            Redirects to health check route
            """
            return app.send_static_file('index.html')

        @app.route('/static/<path:path>')
        def send_static(path):
            return send_from_directory('../frontend/public', path)

        @app.route('/{}/'.format(self.api_version))
        def status():
            """
            Health check route
            """
            status = {
                'status': 'OK'
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
                print(kwargs['repo_url'])

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
            generated_function.__name__ = func.__self__.__class__.__name__ + " _" + func.__name__
            return generated_function
        else:
            def generated_function(*args, **kwargs):
                kwargs.update(request.args.to_dict())
                return Response(response=self.transform(func, args, kwargs, **request.args.to_dict()),
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = func.__self__.__class__.__name__ + " _" + func.__name__
            return generated_function

    def addMetric(self, function, endpoint, cache=True, **kwargs):
        """Simplifies adding routes that only accept owner/repo"""
        endpoint = '/{}/<owner>/<repo>/{}'.format(self.api_version, endpoint)
        self.app.route(endpoint)(self.flaskify(function, cache=cache))
        self.updateMetricMetadata(function, endpoint, **kwargs)

    def addGitMetric(self, function, endpoint, cache=True):
        """Simplifies adding git routes"""
        endpoint = '/{}/git/{}'.format(self.api_version, endpoint)
        self.app.route(endpoint)(self.flaskify(function, cache=cache))
        self.updateMetricMetadata(function, endpoint=endpoint, metric_type='git')

    def addTimeseries(self, function, endpoint):
        """
        Simplifies adding routes that accept owner/repo and return timeseries
        
        :param app:       Flask app
        :param function:  Function from a datasource to add
        :param endpoint:  GET endpoint to generate
        """
        self.addMetric(function, 'timeseries/{}'.format(endpoint), metric_type='timeseries')

    def updateMetricMetadata(self, function, endpoint, **kwargs):
        """
        Updates a given metric's metadata
        """

        # God forgive me
        #
        # Get the unbound function from the bound function's class so that we can modify metadata
        # across instances of that class.
        real_func = getattr(function.__self__.__class__, function.__name__)
        annotate(endpoint=endpoint, **kwargs)(real_func)

def run():
    """
    Runs server with configured hosts/ports
    """
    server = Server()
    host = server._augur.read_config('Server', 'host', 'AUGUR_HOST', '0.0.0.0')
    port = server._augur.read_config('Server', 'port', 'AUGUR_PORT', '5000')
    Server().app.run(host=host, port=int(port))

wsgi_app = None
def wsgi(env, start_response):
    """
    Creates WSGI app
    """
    global wsgi_app
    if (wsgi_app is None):
        app_instance = Server()
        wsgi_app = app_instance.app
    return wsgi_app(env, start_response)

if __name__ == "__main__":
    run()
