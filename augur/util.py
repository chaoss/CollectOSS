#SPDX-License-Identifier: MIT
import pandas as pd
import os
import re
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

metrics = []
def annotate(metadata=None, **kwargs):
    """
    Decorate a function as being a metric
    """
    if metadata is None:
        metadata ={}
    def decorate(func):
        if not hasattr(func, 'metadata'):
            func.metadata = {}
            metrics.append(func.metadata)
        func.metadata.update(metadata)
        func.metadata.update(dict(kwargs))
        return func
    return decorate

def fileExists(path):
    return os.path.exists(path)

class frontendExtractor(object):
    def __init__(self, endpoint):
        self.api = None
        self.endpoint_attributes = None
        self.frontend_card_files = []
        self.endpoint = endpoint


def extractEndpointsAndAttributes(extractor):
        if fileExists('../../frontend/app/AugurAPI.js'):
            extractor.api = open("../../frontend/app/AugurAPI.js", 'r')
            extractor.frontend_card_files = ['../../frontend/app/components/DiversityInclusionCard.vue', 
                       '../../frontend/app/components/GrowthMaturityDeclineCard.vue', 
                       '../../frontend/app/components/RiskCard.vue', 
                       '../../frontend/app/components/ValueCard.vue',
                       '../../frontend/app/components/ExperimentalCard.vue',
                       '../../frontend/app/components/GitCard.vue']

        if fileExists('frontend/app/AugurAPI.js'):
            extractor.api = open("frontend/app/AugurAPI.js", 'r')
            extractor.frontend_card_files = ['frontend/app/components/DiversityInclusionCard.vue', 
                       'frontend/app/components/GrowthMaturityDeclineCard.vue', 
                       'frontend/app/components/RiskCard.vue', 
                       'frontend/app/components/ValueCard.vue',
                       'frontend/app/components/ExperimentalCard.vue',
                       'frontend/app/components/GitCard.vue']

        extractor.endpoint_attributes = re.findall(r'(?:(?:Timeseries|Endpoint)\(repo, )\'(.*)\', \'(.*)\'', extractor.api.read())
        return extractor

def determineFrontendStatus(endpoint):
    fe = frontendExtractor(endpoint)

    extractor = extractEndpointsAndAttributes(fe)

    attribute = [attribute[0] for attribute in extractor.endpoint_attributes if attribute[1] in endpoint]
    # print(extractor.frontend_card_files)

    status = 'unimplemented'
    for card in extractor.frontend_card_files:
        card = open(card, 'r').read()
        if len(attribute) != 0 and attribute[0] in card:
            status = 'implemented'
            break

    return status
