import importlib
import os
import glob
from augur.util import getFileID

def getRouteFiles():
    route_files = []

    for filename in glob.iglob("**/routes/*"):
    	if not getFileID(filename).startswith('__'):
    		route_files.append(getFileID(filename))
    		
    return route_files

route_files = getRouteFiles()

def create_all_datasource_routes(server):
    for route_file in route_files:
        module = importlib.import_module('.' + route_file, 'augur.routes')
        module.create_routes(server)

def create_status_routes(server):
	module = importlib.import_module('.__metric_status_routes', 'augur.routes')
	module.create_routes(server)