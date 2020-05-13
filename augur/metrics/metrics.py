import os
import glob
import sys
import inspect
import types
import importlib
from augur import logger

class Metrics():
    def __init__(self, app):
        self.database = app.database
        self.spdx_db = app.spdx_db

        models = [] #TODO: standardize this
        for filename in glob.iglob("augur/metrics/**"):
            file_id = get_file_id(filename)
            if not file_id.startswith('__') and filename.endswith('.py') and file_id != "metrics":
                models.append(file_id)

        for model in models:
            importlib.import_module(f"augur.metrics.{model}")

        for model in models:
            add_metrics(self, f"augur.metrics.{model}")

def get_file_id(path):
    return os.path.splitext(os.path.basename(path))[0]

def add_metrics(metrics, module_name):
    # find all unbound endpoint functions objects 
    # (ones that have metadata) defined the given module_name 
    # and bind them to the metrics class
    # Derek are you proud of me
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isfunction(obj) == True:
            if hasattr(obj, 'metadata') == True:
                setattr(metrics, name, types.MethodType(obj, metrics))

