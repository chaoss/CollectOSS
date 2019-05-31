import importlib
import glob
import ipdb
import os

def get_route_files():
    route_files = []
    for filename in glob.iglob("**/routes/*"):
        if not get_file_id(filename).startswith('__'):
            route_files.append(get_file_id(filename))
    return route_files

def create_all_routes(server):
    for route_file in get_route_files():
        module = importlib.import_module('.' + route_file, 'broker.routes')
        module.create_routes(server)

def get_file_id(path):
    return os.path.splitext(os.path.basename(path))[0]
