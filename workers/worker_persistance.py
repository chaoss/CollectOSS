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

    def __init__(self, config={}, data_tables=[],operations_tables=[]):
        self.data_tables = data_tables
        self.operations_tables = operations_tables

        self._root_augur_dir = Persistant.ROOT_AUGUR_DIR

        # count of tuples inserted in the database ( to store stats for each task in op tables)
        self.update_counter = 0
        self.insert_counter = 0
        self._results_counter = 0

        # Update config with options that are general and not specific to any worker
        self.augur_config = AugurConfig(self._root_augur_dir)

        self.config = {
                #'worker_type': self.worker_type,
                'host': self.augur_config.get_value('Server', 'host'),
                #'gh_api_key': self.augur_config.get_value('Database', 'key'),
                #'gitlab_api_key': self.augur_config.get_value('Database', 'gitlab_api_key'),
                'offline_mode': False
        }
        self.config.update(self.augur_config.get_section("Logging"))

        self.config.update({
            #'port': worker_port,
            #'id': "workers.{}.{}".format(self.worker_type, worker_port),
            #'capture_output': False,
            #'location': 'http://{}:{}'.format(self.config['host'], worker_port),
            'port_broker': self.augur_config.get_value('Server', 'port'),
            'host_broker': self.augur_config.get_value('Server', 'host'),
            'host_database': self.augur_config.get_value('Database', 'host'),
            'port_database': self.augur_config.get_value('Database', 'port'),
            'user_database': self.augur_config.get_value('Database', 'user'),
            'name_database': self.augur_config.get_value('Database', 'name'),
            'password_database': self.augur_config.get_value('Database', 'password')
        })

    #database interface, the git interfaceable adds additional function to the super method.
    def initialize_database_connections(self):
        DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user_database'], self.config['password_database'], self.config['host_database'], self.config['port_database'], self.config['name_database']
        )

        db_schema = 'augur_data'
        self.db = s.create_engine(DB_STR,  poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(db_schema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        metadata = s.MetaData()
        helper_metadata = s.MetaData()

        # Reflect only the tables we will use for each schema's metadata object
        metadata.reflect(self.db, only=self.data_tables)
        helper_metadata.reflect(self.helper_db, only=self.operations_tables)

        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)

        Base.prepare()
        HelperBase.prepare()

        # So we can access all our tables when inserting, updating, etc
        for table in self.data_tables:
            setattr(self, '{}_table'.format(table), Base.classes[table].__table__)


    def get_max_id(self, table, column, operations_table=False):
        """ Gets the max value (usually used for id/pk's) of any Integer column
            of any table

        :param table: String, the table that consists of the column you want to
            query a max value for
        :param column: String, the column that you want to query the max value for
        :param operations_table: Boolean, if True, this signifies that the table/column
            that is wanted to be queried is in the augur_operations schema rather than
            the augur_data schema. Default False
        :return: Integer, the max value of the specified column/table, None if the value cannot be found.
        """
        maxIdSQL = s.sql.text("""
            SELECT max({0}.{1}) AS {1}
            FROM {0}
        """.format(table, column))
        db = self.db if not operations_table else self.helper_db
        rs = pd.read_sql(maxIdSQL, db, params={})
        if rs.iloc[0][column] is not None:
            max_id = int(rs.iloc[0][column]) + 1
            #self.logger.info("Found max id for {} column in the {} table: {}\n".format(column, table, max_id))
        else:
            max_id = None
            #self.logger.warning("Could not find max id for {} column in the {} table... " +
            #    "using default set to: {}\n".format(column, table, max_id))
        return max_id

