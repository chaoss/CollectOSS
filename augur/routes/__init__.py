import importlib
import os
import glob

from augur import logger

def get_route_files():
    route_files = []
    metric_route_files = []

    def get_file_id(path):
        return os.path.splitext(os.path.basename(path))[0]

    for filename in glob.iglob("**/routes/*"):
        file_id = get_file_id(filename)
        if not file_id.startswith('__') and filename.endswith('.py'):
            route_files.append(file_id)

    for filename in glob.iglob("**/routes/metrics/*"):
        file_id = get_file_id(filename)
        if not file_id.startswith('__') and filename.endswith('.py'):
            metric_route_files.append(file_id)
            
    return route_files, metric_route_files

route_files, metric_route_files = get_route_files()

def create_routes(server):
    for route_file in route_files:
        module = importlib.import_module('.' + route_file, 'augur.routes')
        module.create_routes(server)

    for route_file in metric_route_files:
        module = importlib.import_module('.' + route_file, 'augur.routes.metrics')
        module.create_routes(server)
