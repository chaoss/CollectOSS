#SPDX-License-Identifier: MIT
"""
Provides shared functions that do not fit in a class of their own
"""
import os
import re
import logging
import inspect
import types
import sys
import coloredlogs
import beaker

# Logging
coloredlogs.install(level=os.getenv('AUGUR_LOG_LEVEL', 'INFO'))
logger = logging.getLogger('augur')

__ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data_path(path):
    """
    Returns data path of given object

    :param path: given path of object
    """
    return os.path.join(__ROOT, 'data', path)

# Default cache is in memory
__memory_cache = None
def get_cache(namespace, cache_manager=None):
    """
    Returns cache of object called 'namespace'

    :param namespace: name associated with the targeted cache
    """
    global __memory_cache
    if cache_manager is None:
        if __memory_cache is None:
            cache_opts = beaker.util.parse_cache_config_options({
                'cache.type': 'memory',
                'cache.lock_dir': '/tmp/augur/'
            })
            __memory_cache = beaker.cache.CacheManager(**cache_opts)
        cache_manager = __memory_cache
    return cache_manager.get_cache(namespace)

metric_metadata = []
def annotate(metadata=None, **kwargs):
    """
    Decorates a function as being a metric
    """
    if metadata is None:
        metadata = {}
    def decorate(func):
        if not hasattr(func, 'metadata'):
            func.metadata = {}
            metric_metadata.append(func.metadata)

        func.metadata.update(metadata)
        if kwargs.get('endpoint_type', None):
            endpoint_type = kwargs.pop('endpoint_type')
            if endpoint_type == 'repo':
                func.metadata['repo_endpoint'] = kwargs.get('endpoint')
            else:
                func.metadata['group_endpoint'] = kwargs.get('endpoint')

        func.metadata.update(dict(kwargs))

        func.metadata['metric_name'] = re.sub('_', ' ', func.__name__).title()
        func.metadata['source'] = re.sub(r'(.*\.)', '', func.__module__)
        func.metadata['ID'] = "{}-{}".format(func.metadata['source'].lower(), func.metadata['tag'])

        return func
    return decorate

def add_metrics(metrics, module_name):
    # find all unbound endpoint functions objects (ones that have metadata) defined the given module_name 
    # and bind them to the metrics class
    # Derek are you proud of me
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isfunction(obj) == True:
            if hasattr(obj, 'metadata') == True:
                setattr(metrics, name, types.MethodType(obj, metrics))

