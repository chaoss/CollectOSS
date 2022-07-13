#SPDX-License-Identifier: MIT
import logging
import importlib
import os
import glob
import sys
import inspect

logger = logging.getLogger(__name__)

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

def create_routes(server):
    for route_file in route_files:
        module = importlib.import_module('.' + route_file, 'api.routes')
        module.create_routes(server)

    """
        This loops through all the methods that were added to the metrics class.
        Then it checks what type of metric the method is and calls add_standard_metric or 
        add_toss_metric to create the flask endpoint for the method. The type of metric is defined by
        the @register_metric decorator which is defined in api/util.py, and the server.add_standard_metric
        and server.add_toss_metric are defined in api/server.py
    """
    for name, obj in inspect.getmembers(server.augur_app.metrics):
        if hasattr(obj, 'is_metric') == True:
            if obj.metadata['type'] == "standard":
                server.add_standard_metric(obj, obj.metadata['endpoint'])
            if obj.metadata['type'] == "toss":
                server.add_toss_metric(obj, obj.metadata['endpoint'])
