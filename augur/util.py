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


_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data_path(path):
    return os.path.join(_ROOT, 'data', path)


memory_cache = None

def get_cache(namespace, creation_function, cache_manager=None):
    global memory_cache
    if cache_manager is None:
        if memory_cache is None:
            cache_opts = beaker.util.parse_cache_config_options({
                'cache.type': 'memory',
                'cache.lock_dir': 'runtime'
            })
            memory_cache = beaker.cache.CacheManager(**cache_opts)
        cache_manger = memory_cache
    return cache_manager.get_cache(namespace)