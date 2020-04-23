import importlib
import os
import glob

from .broker import create_broker_routes
from .manager import create_manager_routes

def create_routes(server):
    create_broker_routes(server)
    create_manager_routes(server)
    # for plugin_name in server._augur._loaded_plugins:
    #     module = server._augur[plugin_name]
    #     module.create_routes(server)
