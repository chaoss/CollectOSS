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

class Persistant():

    ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self, worker_type, data_tables=[],operations_tables=[]):
        
        self.worker_type = worker_type
        #For database functionality
        self.data_tables = data_tables
        self.operations_tables = operations_tables

        self._root_augur_dir = Persistant.ROOT_AUGUR_DIR

        # count of tuples inserted in the database ( to store stats for each task in op tables)
        self.update_counter = 0
        self.insert_counter = 0
        self._results_counter = 0

        # Update config with options that are general and not specific to any worker
        self.augur_config = AugurConfig(self._root_augur_dir)

        #TODO: consider taking parts of this out for the base class and then overriding it in WorkerGitInterfaceable
        self.config = {
                'worker_type': self.worker_type,
                'host': self.augur_config.get_value('Server', 'host')
        }
        self.config.update(self.augur_config.get_section("Logging"))

        try:
            worker_defaults = self.augur_config.get_default_config()['Workers'][self.config['worker_type']]
            self.config.update(worker_defaults)
        except KeyError as e:
            logging.warn('Could not get default configuration for {}'.format(self.config['worker_type']))

        worker_info = self.augur_config.get_value('Workers', self.config['worker_type'])
        self.config.update(worker_info)

        worker_port = self.config['port']
        while True:
            try:
                r = requests.get('http://{}:{}/AUGWOP/heartbeat'.format(
                    self.config['host'], worker_port)).json()
                if 'status' in r:
                    if r['status'] == 'alive':
                        worker_port += 1
            except:
                break

        #add credentials to db config. Goes to databaseable
        self.config.update({
            'port': worker_port,
            'id': "workers.{}.{}".format(self.worker_type, worker_port),
            'capture_output': False,
            'location': 'http://{}:{}'.format(self.config['host'], worker_port),
            'port_broker': self.augur_config.get_value('Server', 'port'),
            'host_broker': self.augur_config.get_value('Server', 'host'),
            'host_database': self.augur_config.get_value('Database', 'host'),
            'port_database': self.augur_config.get_value('Database', 'port'),
            'user_database': self.augur_config.get_value('Database', 'user'),
            'name_database': self.augur_config.get_value('Database', 'name'),
            'password_database': self.augur_config.get_value('Database', 'password')
        })
        
        # Initialize logging in the main process
        self.initialize_logging()

        # Clear log contents from previous runs
        open(self.config["server_logfile"], "w").close()
        open(self.config["collection_logfile"], "w").close()

        # Get configured collection logger
        self.logger = logging.getLogger(self.config["id"])
        self.logger.info('Worker (PID: {}) initializing...'.format(str(os.getpid())))

        #back to base, might be overwritten by git integration subclass?
        self.debug_data = [] if 'debug_data' not in self.config else self.config['debug_data']
        self.specs = {
            'id': self.config['id'], # what the broker knows this worker as
            'location': self.config['location'], # host + port worker is running on (so broker can send tasks here)
            'qualifications':  [
                {
                    'given': self.given, # type of repo this worker can be given as a task
                    'models': self.models # models this worker can fill for a repo as a task
                }
            ],
            'config': self.config
        }