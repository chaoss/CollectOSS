#SPDX-License-Identifier: MIT
"""
Analyzes Augur source and CHAOSS repos to determine metric implementation status
"""

import re
import copy
from abc import ABC
import requests
from augur.util import metric_metadata
from augur import logger
import sqlalchemy as s
import pandas as pd
import json

import pprint
pp = pprint.PrettyPrinter()


class MetricsStatus(object):

    def __init__(self, user, password, host, port, dbname, schema):
        """
        Connect to Augur

        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the Augur database
        """
        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
        )

        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
                                  connect_args={'options': '-csearch_path={}'.format(schema)})
        logger.debug('Augur DB: Connecting to {} schema of {}:{}/{} as {}'.format(schema, host, port, dbname, user))

        self.metrics_status = []

    def get_metrics_status(self):
        statusSQL = s.sql.text("""
            SELECT cm_info as tag, cm_group as group, cm_name as name,
                cm_backend_status as backend_status, cm_frontend_status as frontend_status,
                cm_api_endpoint_repo as endpoint_repo, cm_api_endpoint_rg as endpoint_rg,
                cm_source as source, cm_type as metric_type, cm_defined as is_defined,
                cm_working_group as working_group
            FROM chaoss_metric_status
        """)
        results = pd.read_sql(statusSQL, self.db)

        return results

    def get_metrics_metadata(self):
        sourceTypeSQL = s.sql.text("""
        SELECT distinct(cm_source)
        FROM chaoss_metric_status
        WHERE cm_source is not null 
        """)
        sources = pd.read_sql(sourceTypeSQL, self.db).values.flatten().tolist()

        tagSQL = s.sql.text("""
            SELECT distinct(cm_info::text)
            FROM chaoss_metric_status
            WHERE cm_info is not null
        """)
        tags = pd.read_sql(tagSQL, self.db).values.flatten().tolist()

        typeSQL = s.sql.text("""
            SELECT distinct(cm_type)
            FROM chaoss_metric_status
            WHERE cm_type is not null
        """)
        types = pd.read_sql(typeSQL, self.db).values.flatten().tolist()

        groups = {
            "evolution": "Evolution",
            "diversity-inclusion": "Diversity and Inclusion metrics",
            "value": "Value",
            "risk": "Risk",
            "common": "Common",
            "experimental": "Experimental",
            "all": "All"
        }

        return {
            "groups": groups,
            "data_sources": sources,
            "metric_types": types,
            "tags": tags
        }


class Metric(ABC):

    def __init__(self):
        self.ID = None
        self.tag = None
        self.display_name = None
        self.group = None
        self.backend_status = 'unimplemented'
        self.frontend_status = 'unimplemented'
        self.chart_mapping = None
        self.data_source = None
        self.metric_type = None
        self.documentation_url = None
        self.is_defined = False
        self.focus_area = None
        self.endpoint_group = None
        self.endpoint_repo = None