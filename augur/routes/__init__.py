import importlib
import os
import glob

def create_plugin_routes(server):
    for plugin_name in server._augur._loaded_plugins:
        module = server._augur[plugin_name]
        module.create_routes(server)
