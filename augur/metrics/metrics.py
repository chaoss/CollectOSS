import sys
import inspect
import types

from augur import logger

import augur.metrics.commit
import augur.metrics.contributor
import augur.metrics.experimental
import augur.metrics.insight
import augur.metrics.issue
import augur.metrics.message
import augur.metrics.platform
import augur.metrics.pull_request
import augur.metrics.repo_meta
import augur.metrics.util

class Metrics():
    def __init__(self, app):
        self.projects = None
        self.database = app.database
        self.spdx_db = app.spdx_db

        models = ["commit", "contributor", "experimental", "insight", "issue", "message", "platform", "pull_request", "repo_meta", "util"]

        for model in models:
            add_metrics(self, f"augur.metrics.{model}")

def add_metrics(metrics, module_name):
    # find all unbound endpoint functions objects 
    # (ones that have metadata) defined the given module_name 
    # and bind them to the metrics class
    # Derek are you proud of me
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isfunction(obj) == True:
            if hasattr(obj, 'metadata') == True:
                setattr(metrics, name, types.MethodType(obj, metrics))
