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
from augur.application.logs import AugurLogger
from augur.application.config import AugurConfig
from augur.tasks.util.task_session import TaskSession

# TODO: Change cache references
# TODO: Change references to show_metadata

AUGUR_API_VERSION = 'api/unstable'
logger = AugurLogger("server", base_log_dir="/Users/andrew_brain/Augur/augur/logs/").get_logger()
session = TaskSession(logger)
config = AugurConfig(session)

cache = get_cache()
server_cache = get_server_cache(cache, config)

"""
Initializes the server, creating the Flask application
"""
# Create Flask application

def create_app():

    app = Flask(__name__)
    logger.debug("Created Flask app")
    api_version = AUGUR_API_VERSION
    CORS(app)
    app.url_map.strict_slashes = False

    app.config['WTF_CSRF_ENABLED'] = False

    show_metadata = False

    logger.debug("Creating API routes...")
    create_routes(app)
    create_metrics()

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
        return redirect(api_version)

    @app.route('/{}/'.format(api_version))
    @app.route('/{}/status'.format(api_version))
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



def get_route_files():
    route_files = []

    def get_file_id(path):
        return os.path.splitext(os.path.basename(path))[0]

    for filename in glob.iglob("api/routes/*"):
        file_id = get_file_id(filename)
        if not file_id.startswith('__') and filename.endswith('.py'):
            route_files.append(file_id)

    return route_files

route_files = get_route_files()

def create_routes(app):
    for route_file in route_files:
        module = importlib.import_module('.' + route_file, 'augur.api.routes')
        module.create_routes(app)

def get_metric_files():
    metric_files = []

    for filename in glob.iglob("api/metrics/**"):
        file_id = get_file_id(filename)
        if not file_id.startswith('__') and filename.endswith('.py') and file_id != "metrics":
            metric_files.append(file_id)

    return metric_files

metric_files = get_metric_files()

def create_metrics():

    # import the metric modules
    for file in metric_files:
        importlib.import_module(f"augur.api.metrics.{file}")

    # add the metric endpoints the the server
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isfunction(obj) == True:
            if hasattr(obj, 'is_metric') == True:
                if obj.metadata['type'] == "standard":
                    add_standard_metric(obj, obj.metadata['endpoint'])
                if obj.metadata['type'] == "toss":
                    add_toss_metric(obj, obj.metadata['endpoint'])



def transform(func, args=None, kwargs=None, repo_url_base=None, orient='records',
    group_by=None, on=None, aggregate='sum', resample=None, date_col='date'):
    """
    Serializes a dataframe in a JSON object and applies specified transformations
    """

    if orient is None:
        orient = 'records'

    result = ''

    if not show_metadata:

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

def flaskify(function, cache=True):
    """
    Simplifies API endpoints that just accept owner and repo,
    transforms them and spits them out
    """
    if cache:
        def generated_function(*args, **kwargs):
            def heavy_lifting():
                return transform(function, args, kwargs, **request.args.to_dict())
            body = server_cache.get(key=str(request.url), createfunc=heavy_lifting)
            return Response(response=body,
                            status=200,
                            mimetype="application/json")
        generated_function.__name__ = function.__name__
        logger.info(generated_function.__name__)
        return generated_function
    else:
        def generated_function(*args, **kwargs):
            kwargs.update(request.args.to_dict())
            return Response(response=transform(function, args, kwargs, **request.args.to_dict()),
                            status=200,
                            mimetype="application/json")
        generated_function.__name__ = function.__name__
        return generated_function

def routify(func, endpoint_type):
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

        data = transform(func, args, kwargs)
        return Response(response=data,
                        status=200,
                        mimetype="application/json")
    generated_function.__name__ = f"{endpoint_type}_" + func.__name__
    return generated_function
    
def add_standard_metric(function, endpoint, **kwargs):
    repo_endpoint = f'/{api_version}/repos/<repo_id>/{endpoint}'
    repo_group_endpoint = f'/{api_version}/repo-groups/<repo_group_id>/{endpoint}'
    deprecated_repo_endpoint = f'/{api_version}/repo-groups/<repo_group_id>/repos/<repo_id>/{endpoint}'
    app.route(repo_endpoint)(routify(function, 'repo'))
    app.route(repo_group_endpoint)(routify(function, 'repo_group'))
    app.route(deprecated_repo_endpoint )(routify(function, 'deprecated_repo'))

def add_toss_metric(function, endpoint, **kwargs):
    repo_endpoint = f'/{api_version}/repos/<repo_id>/{endpoint}'
    app.route(repo_endpoint)(routify(function, 'repo'))

def create_cache():

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

def get_server_cache(cache, config):

    expire = int(config.get_value('Server', 'cache_expire'))
    server_cache = cache.get_cache('server', expire=expire)
    server_cache_cache.clear()

    return server_cache


if __name__ == '__main__':
    create_app = create_app()
    create_app.run()
else:
    gunicorn_app = create_app()