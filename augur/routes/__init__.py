import importlib
import os
import glob

def create_plugin_routes(server):
    for plugin_name in server._augur._loaded_plugins:
        module = server._augur[plugin_name]
        module.create_routes(server)

def create_metrics_status_routes(server):
    module = importlib.import_module('.__metric_status_routes', 'augur.routes')
    module.create_routes(server)
