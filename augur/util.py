#SPDX-License-Identifier: MIT
import pandas as pd
import os
import logging
import coloredlogs
import beaker

# Logging
coloredlogs.install(level=os.getenv('AUGUR_LOG_LEVEL', 'INFO'))
logger = logging.getLogger('augur')

# end imports
# (don't remove the above line, it's for a script)


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

metrics = {}
def update_metric(metric_name, metadata=None):
    """
    Updates a metric's metadata
    """
    global metrics
    if metadata is None:
        metadata = {}
    if metric_name not in metrics:
            metrics[metric_name] = {}
    if metadata not in metrics[metric_name]:
        metrics[metric_name]['metadata'] = {}
    metrics['metric_name']['metadata'].update(metadata)

def implements_metric(*args, **kwargs):
    """
    Decorate a function as being a metric
    """
    def decorate(func):
        update_metric(*args, **kwargs)
        metrics['metric_name']['func'] = func
        return func
    return decorate