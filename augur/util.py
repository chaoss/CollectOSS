#SPDX-License-Identifier: MIT
"""
Provides shared functions that do not fit in a class of their own
"""
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

def getFileID(path):
    """
    Returns file ID of given object

    :param path: path of given object
    """
    return os.path.splitext(os.path.basename(path))[0]

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
        func.metadata.update(dict(kwargs))

        func.metadata['metric_name'] = re.sub('_', ' ', func.__name__).title()
        func.metadata['source'] = re.sub(r'(.*\.)', '', func.__module__)
        func.metadata['ID'] = "{}-{}".format(func.metadata['source'].lower(), func.metadata['tag'])

        return func
    return decorate


#
# IPython
#

def init_shell_config():
    from IPython.terminal.prompts import Prompts, Token
    from traitlets.config.loader import Config
    
    class PYRCSSPrompt(Prompts):
        def in_prompt_tokens(self, cli=None):
           return [
                (Token.Prompt, 'augur ['),
                (Token.PromptNum, str(self.shell.execution_count)),
                (Token.Prompt, ']: '),
            ]
        def out_prompt_tokens(self):
           return [
                (Token.OutPrompt, 'output ['),
                (Token.OutPromptNum, str(self.shell.execution_count)),
                (Token.OutPrompt, ']: '),
            ]

    try:
        get_ipython
    except NameError:
        nested = 0
        cfg = Config()
        cfg.TerminalInteractiveShell.prompts_class=PYRCSSPrompt
    else:
        print("Running nested copies of the augur shell.")
        cfg = Config()
        nested = 1
    return cfg
