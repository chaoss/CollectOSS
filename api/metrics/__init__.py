#SPDX-License-Identifier: MIT
import os
import glob
import sys
import inspect
import types
import importlib
import logging

from augur_db.engine import engine

logger = logging.getLogger(__name__)

class Metrics():
    def __init__(self):
        print("Importing metrics")
        self.database = engine
        # self.spdx_db = app.spdx_database

        self.models = [] #TODO: standardize this
        for filename in glob.iglob("api/metrics/**"):
            file_id = get_file_id(filename)
            if not file_id.startswith('__') and filename.endswith('.py') and file_id != "metrics":
                self.models.append(file_id)

        for model in self.models:
            importlib.import_module(f"api.metrics.{model}")
            add_metrics(self, f"api.metrics.{model}")

def get_file_id(path):
    return os.path.splitext(os.path.basename(path))[0]

def add_metrics(metrics, module_name):
    # find all unbound endpoint functions objects
    # (ones that have metadata) defined the given module_name
    # and bind them to the metrics class
    """
    this allows the loop in routes/__init.py to find the methods that 
    are metrics so they can be added transformed into flask endpoints
    the reason we can't add the endpoints here is because the flask app 
    hasn't been created yet
    """
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isfunction(obj) == True:
            if hasattr(obj, 'is_metric') == True:
                setattr(metrics, name, types.MethodType(obj, metrics))

