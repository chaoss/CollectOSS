#SPDX-License-Identifier: MIT
"""
Provides shared functions that do not fit in a class of their own
"""
import pandas as pd
import os
import re
import json
import logging
import coloredlogs
import beaker

# Logging
coloredlogs.install(level=os.getenv('AUGUR_LOG_LEVEL', 'INFO'))
logger = logging.getLogger('augur')

# end imports
# (don't remove the above line, it's for a script)

def getFileID(path):
    return os.path.splitext(os.path.basename(path))[0]

__ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data_path(path):
    return os.path.join(__ROOT, 'data', path)

# Default cache is in memory
__memory_cache = None
def get_cache(namespace, cache_manager=None):
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
    Decorate a function as being a metric
    """
    if metadata is None:
        metadata ={}
    def decorate(func):
        if not hasattr(func, 'metadata'):
            func.metadata = {}
            metric_metadata.append(func.metadata)
        func.metadata.update(metadata)
        func.metadata.update(dict(kwargs))

        func.metadata['metric_name'] = re.sub('_', ' ', func.__name__).title()
        func.metadata['source'] = re.sub(r'(.*\.)', '', func.__module__)
        func.metadata['ID'] = "{}-{}".format(func.metadata['source'].lower(), func.metadata['tag'])

        return func
    return decorate
