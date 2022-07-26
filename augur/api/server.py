#SPDX-License-Identifier: MIT
"""
Creates a WSGI server that serves the Augur REST API
"""

import glob
import sys
import inspect
import types
import json
import os
import base64
import logging
import importlib

from flask import Flask, request, Response, redirect
from flask_cors import CORS
import pandas as pd
from beaker.util import parse_cache_config_options
from beaker.cache import CacheManager


from augur.application.logs import AugurLogger
from augur.application.config import AugurConfig
from augur.tasks.util.task_session import TaskSession
from augur.application.db.engine import engine
from metadata import __version__ as augur_code_version

AUGUR_API_VERSION = 'api/unstable'

"""
Initializes the server, creating the Flask application
"""
class Server():

    def __init__(self):

        self.logger = AugurLogger("server", base_log_dir="/Users/andrew_brain/Augur/augur/logs/").get_logger()
        self.session = TaskSession(self.logger)
        self.config = AugurConfig(self.session)

        self.cache = self.create_cache()
        self.server_cache = self.get_server_cache()
        self.app = None
        self.api_version = AUGUR_API_VERSION
        self.show_metadata = False


    def create_app(self):
        self.app = Flask(__name__)
        self.app.augur_api_version = AUGUR_API_VERSION
        self.logger.debug("Created Flask app")
        CORS(self.app)
        self.app.url_map.strict_slashes = False

        self.app.config['WTF_CSRF_ENABLED'] = False


        self.logger.debug("Creating API routes...")
        self.create_routes(self.app)
        self.create_metrics()

        #####################################
        ###          UTILITY              ###
        #####################################

        @self.app.route('/')
        @self.app.route('/ping')
        @self.app.route('/status')
        @self.app.route('/healthcheck')
        def index():
            """
            Redirects to health check route
            """
            return redirect(self.api_version)

        @self.app.route('/{}/'.format(self.api_version))
        @self.app.route('/{}/status'.format(self.api_version))
        def status():
            """
            Health check route
            """
            status = {
                'status': 'OK',
                'version': augur_code_version
            }
            return Response(response=json.dumps(status),
                            status=200,
                            mimetype="application/json")

    def get_app(self):
        return self.app

    def create_routes(self, app):

        route_files = self.get_route_files()

        for route_file in route_files:
            module = importlib.import_module('.' + route_file, 'augur.api.routes')
            module.create_routes(app)


    def get_route_files(self):
        route_files = []

        for filename in glob.iglob("augur/api/routes/*"):
            file_id = self.get_file_id(filename)
            if not file_id.startswith('__') and filename.endswith('.py'):
                route_files.append(file_id)

        return route_files

    def get_file_id(self, path):
        return os.path.splitext(os.path.basename(path))[0]


    def create_metrics(self):

        metric_files = self.get_metric_files()

        # import the metric modules
        for file in metric_files:
            importlib.import_module(f"augur.api.metrics.{file}")
            self.add_metrics(f"augur.api.metrics.{file}")

    def add_metrics(self, module_name):

       #  add the metric endpoints the the server
        for name, obj in inspect.getmembers(sys.modules[module_name]):
            if inspect.isfunction(obj) == True:
                if hasattr(obj, 'is_metric') == True:
                    if obj.metadata['type'] == "standard":
                        self.add_standard_metric(obj, obj.metadata['endpoint'])
                    if obj.metadata['type'] == "toss":
                        self.add_toss_metric(obj, obj.metadata['endpoint'])

    def get_metric_files(self):
        metric_files = []

        for filename in glob.iglob("augur/api/metrics/**"):
            file_id = self.get_file_id(filename)
            if not file_id.startswith('__') and filename.endswith('.py') and file_id != "metrics":
                metric_files.append(file_id)

        return metric_files
        

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

    def flaskify(self, function, cache=True):
        """
        Simplifies API endpoints that just accept owner and repo,
        transforms them and spits them out
        """
        if self.cache:
            def generated_function(*args, **kwargs):
                def heavy_lifting():
                    return self.transform(function, args, kwargs, **request.args.to_dict())
                body = self.server_cache.get(key=str(request.url), createfunc=heavy_lifting)
                return Response(response=body,
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = function.__name__
            self.logger.info(generated_function.__name__)
            return generated_function
        else:
            def generated_function(*args, **kwargs):
                kwargs.update(request.args.to_dict())
                return Response(response=transform(function, args, kwargs, **request.args.to_dict()),
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = function.__name__
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

            if 'repo_group_id' not in kwargs and func.metadata["type"] != "toss":
                kwargs['repo_group_id'] = 1

            data =  self.transform(func, args, kwargs)
            return Response(response=data,
                            status=200,
                            mimetype="application/json")
        generated_function.__name__ = f"{endpoint_type}_" + func.__name__
        return generated_function
        
    def add_standard_metric(self, function, endpoint, **kwargs):
        repo_endpoint = f'/{self.api_version}/repos/<repo_id>/{endpoint}'
        repo_group_endpoint = f'/{self.api_version}/repo-groups/<repo_group_id>/{endpoint}'
        deprecated_repo_endpoint = f'/{self.api_version}/repo-groups/<repo_group_id>/repos/<repo_id>/{endpoint}'
        self.app.route(repo_endpoint)(self.routify(function, 'repo'))
        self.app.route(repo_group_endpoint)(self.routify(function, 'repo_group'))
        self.app.route(deprecated_repo_endpoint )(self.routify(function, 'deprecated_repo'))

    def add_toss_metric(self, function, endpoint, **kwargs):
        repo_endpoint = f'/{self.api_version}/repos/<repo_id>/{endpoint}'
        self.app.route(repo_endpoint)(self.routify(function, 'repo'))

    def create_cache(self):

        cache_config = {
        'cache.type': 'file',
        'cache.data_dir': 'runtime/cache/',
        'cache.lock_dir': 'runtime/cache/'
    }

        if not os.path.exists(cache_config['cache.data_dir']):
            os.makedirs(cache_config['cache.data_dir'])
        if not os.path.exists(cache_config['cache.lock_dir']):
            os.makedirs(cache_config['cache.lock_dir'])
        cache_parsed = parse_cache_config_options(cache_config)
        cache = CacheManager(**cache_parsed)

        return cache

    def get_server_cache(self):

        expire = int(self.config.get_value('Server', 'cache_expire'))
        self.server_cache = self.cache.get_cache('server', expire=expire)
        self.server_cache.clear()

        return self.server_cache

server = Server()
server.create_app()
app = server.get_app()
