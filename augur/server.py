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

from flask import Flask, request, Response, redirect
from flask_cors import CORS
import pandas as pd

import augur
from augur.routes import create_routes

AUGUR_API_VERSION = 'api/unstable'

logger = logging.getLogger(__name__)

class Server(object):
    """
    Defines Augur's server's behavior
    """
    def __init__(self, augur_app=None):
        """
        Initializes the server, creating both the Flask application and Augur application
        """
        # Create Flask application

        self.app = Flask(__name__)
        logger.debug("Created Flask app")
        self.api_version = AUGUR_API_VERSION
        app = self.app
        CORS(app)
        app.url_map.strict_slashes = False

        self.augur_app = augur_app
        self.manager = augur_app.manager
        self.broker = augur_app.broker
        self.housekeeper = augur_app.housekeeper

        # Initialize cache
        expire = int(self.augur_app.config.get_value('Server', 'cache_expire'))
        self.cache = self.augur_app.cache.get_cache('server', expire=expire)
        self.cache.clear()

        app.config['WTF_CSRF_ENABLED'] = False

        self.show_metadata = False

        logger.debug("Creating API routes...")
        create_routes(self)

        #####################################
        ###          UTILITY              ###
        #####################################

        @app.route('/')
        @app.route('/ping')
        @app.route('/status')
        @app.route('/healthcheck')
        def index():
            """
            Redirects to health check route
            """
            return redirect(self.api_version)

        @app.route('/{}/'.format(self.api_version))
        @app.route('/{}/status'.format(self.api_version))
        def status():
            """
            Health check route
            """
            status = {
                'status': 'OK',
            }
            return Response(response=json.dumps(status),
                            status=200,
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

    def flaskify(self, function, cache=True):
        """
        Simplifies API endpoints that just accept owner and repo,
        transforms them and spits them out
        """
        if cache:
            def generated_function(*args, **kwargs):
                def heavy_lifting():
                    return self.transform(function, args, kwargs, **request.args.to_dict())
                body = self.cache.get(key=str(request.url), createfunc=heavy_lifting)
                return Response(response=body,
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = function.__name__
            logger.info(generated_function.__name__)
            return generated_function
        else:
            def generated_function(*args, **kwargs):
                kwargs.update(request.args.to_dict())
                return Response(response=self.transform(function, args, kwargs, **request.args.to_dict()),
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

            data = self.transform(func, args, kwargs)
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
