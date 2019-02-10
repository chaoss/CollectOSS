import importlib
import os
import glob

from .user import create_user_routes

def create_routes(server):
    create_user_routes(server)
    for plugin_name in server._augur._loaded_plugins:
        module = server._augur[plugin_name]
        module.create_routes(server)
