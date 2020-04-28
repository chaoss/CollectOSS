#SPDX-License-Identifier: MIT

import logging
import coloredlogs

coloredlogs.install()
logger = logging.getLogger('augur')

# Classes
from .application import Application, logger
