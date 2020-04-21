import importlib
import os
import glob

from .broker import create_broker_routes
from .manager import create_manager_routes
from .batch import create_batch_routes

def create_routes(server):
    create_broker_routes(server)
    create_manager_routes(server)
    create_batch_routes(server)
