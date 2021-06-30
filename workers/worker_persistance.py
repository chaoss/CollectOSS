#SPDX-License-Identifier: MIT
#WORK IN PROGRESS NOT TO BE USED AT ALL IN PRESENT STATE
""" Helper methods constant across all workers """
import requests
import datetime
import time
import traceback
import json
import os
import sys
import math
import logging
import numpy
import copy
import concurrent
import multiprocessing
import psycopg2
import csv
import io
from logging import FileHandler, Formatter, StreamHandler
from multiprocessing import Process, Queue, Pool
from os import getpid
import sqlalchemy as s
import pandas as pd
from pathlib import Path
from urllib.parse import urlparse, quote
from sqlalchemy.ext.automap import automap_base
from augur.config import AugurConfig
from augur.logging import AugurLogging
from sqlalchemy.sql.expression import bindparam
from concurrent import futures
import dask.dataframe as dd