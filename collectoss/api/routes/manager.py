#SPDX-License-Identifier: MIT
"""
Creates routes for the manager
"""


# TODO: Need to come back and fix this later

import logging
import time
import requests
import sqlalchemy as s
from sqlalchemy import exc
from flask import request, Response
# from collectoss.config import SystemConfig
import os 
import traceback 

from collectoss.api.routes import API_VERSION
from ..server import app

logger = logging.getLogger(__name__)

