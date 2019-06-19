import importlib
import os
import glob

from .user import create_user_routes
from .repo import create_repo_routes
from .broker import create_broker_routes

def create_routes(server):
    create_user_routes(server)
    create_repo_routes(server)
    create_broker_routes(server)
    for plugin_name in server._augur._loaded_plugins:
        module = server._augur[plugin_name]
        module.create_routes(server)
