#SPDX-License-Identifier: MIT
"""Creates a WSGI server that serves the Augur REST API."""

import glob
import sys
import inspect
import types
import json
import os
import base64
import logging
import importlib

from typing import Optional, List, Any, Tuple

from flask import Flask, request, Response, redirect
from flask_cors import CORS
import pandas as pd
from beaker.util import parse_cache_config_options
from beaker.cache import CacheManager, Cache


from augur.application.db.session import DatabaseSession
from augur.application.logs import AugurLogger
from metadata import __version__ as augur_code_version

AUGUR_API_VERSION = 'api/unstable'



class Server():
    """Initializes the server, creating the Flask application.
    
    Attributes:
        logger (logging.Logger): handles logging
        session (DatabaseSession): used to create the config
        config (AugurConfig): used to access the config in the database
        engine: Sqlalchemy database connection engine
        cache: ?
        server_cache: ?
        app: Flask application
        show_metadata (bool): ?
    """

    def __init__(self):
        """Initialize the Server class."""

        self.logger = AugurLogger("server").get_logger()
        self.session = DatabaseSession(self.logger)
        self.config = self.session.config
        self.engine = self.session.engine

        self.cache_manager = self.create_cache_manager()
        self.server_cache = self.get_server_cache()
        self.app = None
        self.show_metadata = False


    def create_app(self):
        """Define the flask app and configure the routes."""
        self.app = Flask(__name__)
        self.logger.debug("Created Flask app")

        # defines the api version on the flask app, 
        # so when we pass the flask app to the routes files we 
        # know can access the api version via the app variable
        self.app.augur_api_version = AUGUR_API_VERSION


        CORS(self.app)
        self.app.url_map.strict_slashes = False

        self.app.config['WTF_CSRF_ENABLED'] = False


        self.logger.debug("Creating API routes...")
        self.create_all_routes()
        self.create_metrics()

        @self.app.route('/')
        @self.app.route('/ping')
        @self.app.route('/status')
        @self.app.route('/healthcheck')
        def index():
            """
            Redirects to health check route
            """
            return redirect(self.app.augur_api_version)

        @self.app.route(f'/{self.app.augur_api_version}/')
        @self.app.route(f'/{self.app.augur_api_version}/status')
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

   
    def get_app(self) -> Optional[Flask]:
        """Get flask app.

        Returns:
            The flask applcation
        """
        return self.app


    def create_all_routes(self):
        """Add all the routes defined in the files in the augur/api/routes directory to the flask app."""

        # gets a list of the routes files
        route_files = self.get_route_files()

        for route_file in route_files:

            # imports the routes file
            module = importlib.import_module('.' + route_file, 'augur.api.routes')

            # each file that contains routes must contain a create_routes function
            # and this line is calling that function and passing the flask app,
            # so that the routes in the files can be added to the flask app
            module.create_routes(self)

    
    def get_route_files(self) -> List[str]:
        """This function gets a list of all the routes files in the augur/api/routes directory.
        
        Returns:
            list of file names as strings
        """
        route_files = []
        for filename in glob.iglob("augur/api/routes/*"):
            file_id = self.get_file_id(filename)

            # this filters out files like __init__ and __pycache__. And makes sure it only get py files
            if not file_id.startswith('__') and filename.endswith('.py'):
                route_files.append(file_id)

        return route_files


    
    def get_file_id(self, path: str) -> str:
        """Gets the file id of a given path.

        Args:
            path: file path
        
        Examples: 
            If the path /augur/best_routes.py is given it will return "best_routes"

        Returns:
            the filename as a string
        """
        return os.path.splitext(os.path.basename(path))[0]


    
    def create_metrics(self) -> None:
        """Starts process of adding all the functions from the metrics folder to the flask app as routes."""
        # get a list of the metrics files
        metric_files = self.get_metric_files()

        # import the metric modules and add them to the flask app using self.add_metrics
        for file in metric_files:
            importlib.import_module(f"augur.api.metrics.{file}")
            self.add_metrics(f"augur.api.metrics.{file}")


    def add_metrics(self, module_name: str) -> None:
        """Determine type of metric and call function to add them to the flask app.
        
        This function takes modules that contains metrics, 
        and adds them to the flask app via the self.add_standard_metric 
        or self.add_toss_metric methods.

        Note: 
            The attribute is_metric and obj.metadata['type'] 
            are set in file augur/api/routes/util.py in the function 
            register_metric(). This function is a decorator and is 
            how a function is defined as a metric.

        Args:
            module_name: path to the module
        """

        # gets all the members in the module and loops through them
        for _, obj in inspect.getmembers(sys.modules[module_name]):

            # cheks if the object is a function
            if inspect.isfunction(obj) is True:

                # checks if the function has the attribute is_metric. 
                # If it does then it is a metric function and needs to be added to the flask app
                if hasattr(obj, 'is_metric') is True:

                    # determines the type of metric and calls the correct method to add it to the flask app
                    if obj.metadata['type'] == "standard":
                        self.add_standard_metric(obj, obj.metadata['endpoint'])
                    if obj.metadata['type'] == "toss":
                        self.add_toss_metric(obj, obj.metadata['endpoint'])



    def get_metric_files(self) -> List[str]:
        """Get list of all the metrics files in the augur/api/metrics directory,

        Returns:
            list of file names
        """
        metric_files = []

        for filename in glob.iglob("augur/api/metrics/**"):
            file_id = self.get_file_id(filename)
            
            # this filters out files like __init__ and __pycache__. And makes sure it only get py files
            if not file_id.startswith('__') and filename.endswith('.py'):
                metric_files.append(file_id)

        return metric_files
        
    # NOTE: Paramater on=None removed, since it is not used in the function Aug 18, 2022 - Andrew Brain
    def transform(self, func: Any, args: Any=None, kwargs: dict=None, repo_url_base: str=None, orient: str ='records',
        group_by: str=None, aggregate: str='sum', resample=None, date_col: str='date') -> str:
        """Call a metric function and apply data transformations.

        Note:
            This function takes a function and it arguments, calls the function, then converts it to json if possible.
            It also does some manipulation of the data if paramaters like group_by, aggregate, and respample are set

        Args:
            func: function that is called
            args:
            kwargs:
            repo_url_base:
            orient: 
            group_byf
            on
            aggregate:
            resample:
            date_col:

        Returns:
            The result of calling the function and applying the data transformations
        """
        # this defines the way a pandas dataframe is converted to json
        if orient is None:
            orient = 'records'

        result = ''

        if not self.show_metadata:

            if args is None:
                args = ()

            if kwargs is None:
                kwargs = {}

            if repo_url_base:
                kwargs['repo_url'] = str(base64.b64decode(repo_url_base).decode())

            # calls the function that was passed to get the data
            data = func(*args, **kwargs)
            
            # most metrics return a pandas dataframe, which has the attribute to_json
            # so basically this is checking if it is a pandas dataframe
            if hasattr(data, 'to_json'):

                # if group_by is defined it groups by the group_by value 
                # and uses the aggregate to determine the operation performed
                if group_by is not None:
                    data = data.group_by(group_by).aggregate(aggregate)

                # This code block is resampling the pandas dataframe, here is the documentation for it
                # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
                if resample is not None:
                    data['idx'] = pd.to_datetime(data[date_col])
                    data = data.set_index('idx')
                    data = data.resample(resample).aggregate(aggregate)
                    data['date'] = data.index
                
                # converts pandas dataframe to json
                result = data.to_json(orient=orient, date_format='iso', date_unit='ms')
            else:
                # trys to convert dict to json
                try:
                    
                    result = json.dumps(data)
                except:
                    result = data
        else:
            result = json.dumps(func.metadata)

        # returns the result of the function
        return result

    def flaskify(self, function: Any) -> Any:
        """Simplifies API endpoints that just accept owner and repo, transforms them and spits them out.
        """
        if self.cache_manager:
            def cache_generated_function(*args, **kwargs):
                def heavy_lifting():
                    return self.transform(function, args, kwargs, **request.args.to_dict())
                body = self.server_cache.get(key=str(request.url), createfunc=heavy_lifting)
                return Response(response=body,
                                status=200,
                                mimetype="application/json")
            cache_generated_function.__name__ = function.__name__
            self.logger.info(cache_generated_function.__name__)
            return cache_generated_function

        def generated_function(*args, **kwargs):
            kwargs.update(request.args.to_dict())
            return Response(response=self.transform(function, args, kwargs, **request.args.to_dict()),
                            status=200,
                            mimetype="application/json")
        generated_function.__name__ = function.__name__
        return generated_function

    def routify(self, func: Any, endpoint_type: str) -> Any:
        """Wraps a metric function allowing it to be mapped to a route,
        get request args and also transforms the metric functions's
        output to json

        :param func: The function to be wrapped
        :param endpoint_type: The type of API endpoint, i.e. 'repo_group' or 'repo'
        """

        # this is that is generated by self.routify() as passed to the self.app.route() decorator
        # basically this is the function that is called when an endpoint is pinged
        def endpoint_function(*args, **kwargs) -> Response:

            # sets the kwargs as the query paramaters or the arguments sent in the headers 
            kwargs.update(request.args.to_dict()) 

            # if repo_group_id is not specified, it sets it to 1 which is the default repo group
            if 'repo_group_id' not in kwargs and func.metadata["type"] != "toss":
                kwargs['repo_group_id'] = 1


            # this function call takes the arguments specified when the endpoint is pinged
            # and calls the actual function in the metrics folder and then returns the result
            # NOTE: This also converts the data into json if the function returns a pandas dataframe or dict
            data =  self.transform(func, args, kwargs)


            # this is where the Response is created for all the metrics 
            return Response(response=data,
                            status=200,
                            mimetype="application/json")

        # this sets the name of the endpoint function
        # so that the repo_endpoint, repo_group_endpoint, and deprecated_repo_endpoint
        # don't create endpoint funcitons with the same name
        endpoint_function.__name__ = f"{endpoint_type}_" + func.__name__
        return endpoint_function

        
    def add_standard_metric(self, function: Any, endpoint: str) -> None:
        """Add standard metric routes to the flask app.
        
        Args:
            function: the function that needs to be mapped to the routes
            endpoint: the path that the endpoint should be defined as
        """
        repo_endpoint = f'/{self.app.augur_api_version}/repos/<repo_id>/{endpoint}'
        repo_group_endpoint = f'/{self.app.augur_api_version}/repo-groups/<repo_group_id>/{endpoint}'
        deprecated_repo_endpoint = f'/{self.app.augur_api_version}/repo-groups/<repo_group_id>/repos/<repo_id>/{endpoint}'

        
        # These three lines are defining routes on the flask app, and passing a function.
        # Essetially the strucutre of this is self.app.route(endpoint)(function).
        # So when this code is executed, it calls self.routify() which returns a function.
        # The function that is returned is the function that is registerred with the route, and called when the route is pinged
        
        # Simply self.routify() is called by the route being pinged, and 
        # then self.routify() returns a function so it is called, 
        # and then that function returns a Response
        self.app.route(repo_endpoint)(self.routify(function, 'repo'))
        self.app.route(repo_group_endpoint)(self.routify(function, 'repo_group'))
        self.app.route(deprecated_repo_endpoint )(self.routify(function, 'deprecated_repo'))

    def add_toss_metric(self, function: Any, endpoint: str) -> None:
        """Add toss metric routes to the flask app.
        
        Args:
            function: the function that needs to be mapped to the routes
            endpoint: the path that the endpoint should be defined as
        """
        repo_endpoint = f'/{self.app.augur_api_version}/repos/<repo_id>/{endpoint}'
        self.app.route(repo_endpoint)(self.routify(function, 'repo'))

    def create_cache_manager(self) -> CacheManager:
        """Create cache for endpoints?
        
        Returns:
            manager of the cache
        """

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

    def get_server_cache(self) -> Cache:
        """Create the server cache, set expiration, and clear
        
        Returns:
            server cache
        """

        expire = int(self.config.get_value('Server', 'cache_expire'))
        server_cache = self.cache_manager.get_cache('server', expire=expire)
        server_cache.clear()

        return server_cache

# this is where the flask app is defined and the server is insantiated
server = Server()
server.create_app()
app = server.get_app()
