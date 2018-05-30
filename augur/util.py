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