#SPDX-License-Identifier: MIT
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
import psycopg2.extensions
import csv
import io
from logging import FileHandler, Formatter, StreamHandler
from multiprocessing import Process, Queue, Pool, Value
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

        self.db_schema = None
        self.helper_schema = None
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

    #Return string representation of an object with all information needed to recreate the object (Think of it like a pickle made out of text)
    #Called using repr(*object*). eval(repr(*object*)) == *object*
    def __repr__(self):
        return f"{self.config['id']}"

    def initialize_logging(self):
        #Get the log level in upper case from the augur config's logging section.
        self.config['log_level'] = self.config['log_level'].upper()
        if self.config['debug']:
            self.config['log_level'] = 'DEBUG'

        if self.config['verbose']:
            format_string = AugurLogging.verbose_format_string
        else:
            format_string = AugurLogging.simple_format_string

        #Use stock python formatter for stdout
        formatter = Formatter(fmt=format_string)
        #User custom for stderr, Gives more info than verbose_format_string
        error_formatter = Formatter(fmt=AugurLogging.error_format_string)

        worker_dir = AugurLogging.get_log_directories(self.augur_config, reset_logfiles=False) + "/workers/"
        Path(worker_dir).mkdir(exist_ok=True)
        logfile_dir = worker_dir + f"/{self.worker_type}/"
        Path(logfile_dir).mkdir(exist_ok=True)

        #Create more complex sublogs in the logfile directory determined by the AugurLogging class
        server_logfile = logfile_dir + '{}_{}_server.log'.format(self.worker_type, self.config["port"])
        collection_logfile = logfile_dir + '{}_{}_collection.log'.format(self.worker_type, self.config["port"])
        collection_errorfile = logfile_dir + '{}_{}_collection.err'.format(self.worker_type, self.config["port"])
        self.config.update({
            'logfile_dir': logfile_dir,
            'server_logfile': server_logfile,
            'collection_logfile': collection_logfile,
            'collection_errorfile': collection_errorfile
        })

        collection_file_handler = FileHandler(filename=self.config['collection_logfile'], mode="a")
        collection_file_handler.setFormatter(formatter)
        collection_file_handler.setLevel(self.config['log_level'])

        collection_errorfile_handler = FileHandler(filename=self.config['collection_errorfile'], mode="a")
        collection_errorfile_handler.setFormatter(error_formatter)
        collection_errorfile_handler.setLevel(logging.WARNING)

        logger = logging.getLogger(self.config['id'])
        logger.handlers = []
        logger.addHandler(collection_file_handler)
        logger.addHandler(collection_errorfile_handler)
        logger.setLevel(self.config['log_level'])
        logger.propagate = False

        if self.config['debug']:
            self.config['log_level'] = 'DEBUG'
            console_handler = StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(self.config['log_level'])
            logger.addHandler(console_handler)

        if self.config['quiet']:
            logger.disabled = True

        self.logger = logger

    #database interface, the git interfaceable adds additional function to the super method.
    def initialize_database_connections(self):
        DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user_database'], self.config['password_database'], self.config['host_database'], self.config['port_database'], self.config['name_database']
        )

        # Create an sqlalchemy engine for both database schemas
        self.logger.info("Making database connections")

        self.db_schema = 'augur_data'
        self.db = s.create_engine(DB_STR,  poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(self.db_schema)})
        # , 'client_encoding': 'utf8'
        self.helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(self.helper_schema)})

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

        try:
            self.logger.info(HelperBase.classes.keys())
        except:
            pass

        for table in self.operations_tables:
            try:
                setattr(self, '{}_table'.format(table), HelperBase.classes[table].__table__)
            except Exception as e:
                self.logger.error("Error setting attribute for table: {} : {}".format(table, e))

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.logger.info("Trying to find max id of table...")
        try:
            self.history_id = self.get_max_id('worker_history', 'history_id', operations_table=True) + 1
        except Exception as e:
            self.logger.info(f"Could not find max id. ERROR: {e}")

        #25151
        #self.logger.info(f"Good, passed the max id getter. Max id: {self.history_id}")

    #Make sure the type used to store date is synced with the worker?
    def sync_df_types(self, subject, source, subject_columns, source_columns):

        type_dict = {}

        ## Getting rid of nan's and NoneTypes across the dataframe to start:

        subject = subject.fillna(value=numpy.nan)
        source = source.fillna(value=numpy.nan)

        for index in range(len(source_columns)):
            if type(source[source_columns[index]].values[0]) == numpy.datetime64:
                subject[subject_columns[index]] = pd.to_datetime(
                    subject[subject_columns[index]], utc=True
                )
                source[source_columns[index]] = pd.to_datetime(
                    source[source_columns[index]], utc=True
                )
                continue
            ## Dealing with an error coming from paginate endpoint and the GitHub issue worker
            ### For a release in mid september, 2021. #SPG  This did not work on Ints or Floats
            # if type(source[source_columns[index]].values[0]).isnull():
            #     subject[subject_columns[index]] = pd.fillna(value=np.nan)
            #     source[source_columns[index]] = pd.fillna(value=np.nan)
            #     continue
            source_index = source_columns[index]
            try:
                source_index = source_columns[index]
                type_dict[subject_columns[index]] = type(source[source_index].values[0])
                
                #self.logger.info(f"Source data column is {source[source_index].values[0]}")
                #self.logger.info(f"Type dict at {subject_columns[index]} is : {type(source[source_index].values[0])}")
            except Exception as e:
                self.logger.info(f"Source data registered exception: {source[source_index]}")
                self.print_traceback("", e, True)

        subject = subject.astype(type_dict)

        return subject, source

    #Convert safely from sql type to python type?
    def get_sqlalchemy_type(self, data, column_name=None):
        if type(data) == str:
            try:
                time.strptime(data, "%Y-%m-%dT%H:%M:%SZ")
                return s.types.TIMESTAMP
            except ValueError:
                return s.types.String
        elif (
            isinstance(data, (int, numpy.integer))
            or (isinstance(data, float) and column_name and 'id' in column_name)
        ):
            return s.types.BigInteger
        elif isinstance(data, float):
            return s.types.Float
        elif type(data) in [numpy.datetime64, pd._libs.tslibs.timestamps.Timestamp]:
            return s.types.TIMESTAMP
        elif column_name and 'id' in column_name:
            return s.types.BigInteger
        return s.types.String

    def _convert_float_nan_to_int(self, df):
        for column in df.columns:
            if (
                df[column].dtype == float
                and ((df[column] % 1 == 0) | (df[column].isnull())).all()
            ):
                df[column] = df[column].astype("Int64").astype(object).where(
                    pd.notnull(df[column]), None
                )
        return df

    def _setup_postgres_merge(self, data_sets, sort=False):

        metadata = s.MetaData()

        data_tables = []

        # Setup/create tables
        for index, data in enumerate(data_sets):

            data_table = s.schema.Table(f"merge_data_{index}_{os.getpid()}", metadata)
            df = pd.DataFrame(data)

            columns = sorted(list(df.columns)) if sort else df.columns
            df = self._convert_float_nan_to_int(df)
            for column in columns:
                data_table.append_column(
                    s.schema.Column(
                        column, self.get_sqlalchemy_type(
                            df.fillna(method='bfill').iloc[0][column], column_name=column
                        )
                    )
                )

            data_tables.append(data_table)

        metadata.create_all(self.db, checkfirst=True)

        # Insert data to tables
        for data_table, data in zip(data_tables, data_sets):
            self.bulk_insert(
                data_table, insert=data, increment_counter=False, convert_float_int=True
            )

        session = s.orm.Session(self.db)
        self.logger.info("Session created for merge tables")

        return data_tables, metadata, session

    def _close_postgres_merge(self, metadata, session):

        session.close()
        self.logger.info("Session closed")

        # metadata.reflect(self.db, only=[new_data_table.name, table_values_table.name])
        metadata.drop_all(self.db, checkfirst=True)
        self.logger.info("Merge tables dropped")

    def _get_data_set_columns(self, data, columns):
        if not len(data):
            return []
        self.logger.info("Getting data set columns")
        df = pd.DataFrame(data, columns=data[0].keys())
        final_columns = copy.deepcopy(columns)
        for column in columns:
            if '.' not in column:
                continue
            root = column.split('.')[0]
            if root not in df.columns:
                df[root] = None
            expanded_column = pd.DataFrame(
                df[root].where(df[root].notna(), lambda x: [{}]).tolist()
            )
            expanded_column.columns = [
                f'{root}.{attribute}' for attribute in expanded_column.columns
            ]
            if column not in expanded_column.columns:
                expanded_column[column] = None
            final_columns += list(expanded_column.columns)
            try:
                df = df.join(expanded_column)
            except ValueError:
                # columns already added (happens if trying to expand the same column twice)
                # TODO: Catch this before by only looping unique prefixs?
                self.logger.info("Columns have already been added, moving on...")
                pass
        self.logger.info(final_columns)
        self.logger.info(list(set(final_columns)))
        self.logger.info("Finished getting data set columns")
        return df[list(set(final_columns))].to_dict(orient='records')

    def organize_needed_data(
        self, new_data, table_values, table_pkey=None, action_map={}, in_memory=True
    ):
        """
        This method determines which rows need to be inserted into the database (ensures data ins't inserted more than once)
        and determines which rows have data that needs to be updated

        :param new_data: list of dictionaries - needs to be compared with data in database to see if any updates are
            needed or if the data needs to be inserted
        :param table_values: list of SQLAlchemy tuples - data that is currently in the database
        :param action_map: dict with two keys (insert and update) and each key's value contains a list of the fields
            that are needed to determine if a row is unique or if a row needs to be updated
        :param in_memory: boolean - determines whether the method is done is memory or database
            (currently everything keeps the default of in_memory=True)

        :return: list of dictionaries that contain data that needs to be inserted into the database
        :return: list of dictionaries that contain data that needs to be updated in the database
        """

        if len(table_values) == 0:
            return new_data, []

        if len(new_data) == 0:
            return [], []

        need_insertion = pd.DataFrame()
        need_updates = pd.DataFrame()

        if not in_memory:

            new_data_columns = action_map['insert']['source']
            table_value_columns = action_map['insert']['augur']
            if 'update' in action_map:
                new_data_columns += action_map['update']['source']
                table_value_columns += action_map['update']['augur']

            (new_data_table, table_values_table), metadata, session = self._setup_postgres_merge(
                [
                    self._get_data_set_columns(new_data, new_data_columns),
                    self._get_data_set_columns(table_values, table_value_columns)
                ]
            )

            need_insertion = pd.DataFrame(session.query(new_data_table).join(table_values_table,
                eval(
                    ' and '.join([
                        f"table_values_table.c.{table_column} == new_data_table.c.{source_column}" \
                        for table_column, source_column in zip(action_map['insert']['augur'],
                        action_map['insert']['source'])
                    ])
                ), isouter=True).filter(
                    table_values_table.c[action_map['insert']['augur'][0]] == None
                ).all(), columns=table_value_columns)

            self.logger.info("need_insertion calculated successfully")

            need_updates = pd.DataFrame(columns=table_value_columns)
            if 'update' in action_map:
                need_updates = pd.DataFrame(session.query(new_data_table).join(table_values_table,
                    s.and_(
                        eval(' and '.join([f"table_values_table.c.{table_column} == new_data_table.c.{source_column}" for \
                        table_column, source_column in zip(action_map['insert']['augur'], action_map['insert']['source'])])),

                        eval(' and '.join([f"table_values_table.c.{table_column} != new_data_table.c.{source_column}" for \
                        table_column, source_column in zip(action_map['update']['augur'], action_map['update']['source'])]))
                    ) ).all(), columns=table_value_columns)
                self.logger.info("need_updates calculated successfully")

            self._close_postgres_merge(metadata, session)

            new_data_df = pd.DataFrame(new_data)

            need_insertion, new_data_df = self.sync_df_types(
                need_insertion, new_data_df, table_value_columns, new_data_columns
            )
            need_insertion = need_insertion.merge(
                new_data_df, how='inner', left_on=table_value_columns, right_on=new_data_columns
            )

            self.logger.info(
                f"Table needs {len(need_insertion)} insertions and "
                f"{len(need_updates)} updates.\n")

        else:
            #create panda tabluar data from the keys of the passed table values
            table_values_df = pd.DataFrame(table_values, columns=table_values[0].keys())
            new_data_df = pd.DataFrame(new_data).dropna(subset=action_map['insert']['source'])

            new_data_df, table_values_df = self.sync_df_types(new_data_df, table_values_df,
                    action_map['insert']['source'], action_map['insert']['augur'])

            #Throwing value errors. 'cannot use name of an existing column for indicator column'


            '''
                This is how uniqueness, or whether a piece of data needs to be inserted, or
                if that data already exists.

                With regards to the comment_action_map (for insertion of issue_comments and pull_request_comments
                we need to recognize the following:

                    paginate_endpoint() then gets a dataframe of all the data that needs to be inserted.
                    Earlier, we added 'tool_source' to the augur side of the action map, and left
                    'id' alone on the source side (since tool_source) is our variable, and part of our
                    natural key.

                    --Andrew Brain and Sean Goggins 9/16/2021. Debugging duplicate insert errors for
                    comments after initial collection.
            '''

            try:
                need_insertion = new_data_df.merge(table_values_df, suffixes=('','_table'),
                        how='outer', indicator=True, left_on=action_map['insert']['source'],
                        right_on=action_map['insert']['augur']).loc[lambda x : x['_merge']=='left_only']
            except ValueError as e:

                #Log the error, try to merge again without label to avoid ValueError
                self.logger.warning(f"Error thrown during pandas merge: {e}")
                need_insertion = new_data_df.merge(table_values_df, suffixes=('','_table'),
                        how='outer', indicator=False, left_on=action_map['insert']['source'],
                        right_on=action_map['insert']['augur']).loc[lambda x : x['_merge']=='left_only']



            if 'update' in action_map:
                new_data_df, table_values_df = self.sync_df_types(new_data_df, table_values_df,
                    action_map['update']['source'], action_map['update']['augur'])

                partitions = math.ceil(len(new_data_df) / 1000)
                attempts = 0
                while attempts < 50:
                    try:
                        need_updates = pd.DataFrame()
                        self.logger.info(f"Trying {partitions} partitions\n")
                        for sub_df in numpy.array_split(new_data_df, partitions):
                            self.logger.info(f"Trying a partition, len {len(sub_df)}\n")
                            need_updates = pd.concat([ need_updates, sub_df.merge(table_values_df, left_on=action_map['insert']['source'],
                                right_on=action_map['insert']['augur'], suffixes=('','_table'), how='inner',
                                indicator=False).merge(table_values_df, left_on=action_map['update']['source'],
                                right_on=action_map['update']['augur'], suffixes=('','_table'), how='outer',
                                indicator=True).loc[lambda x : x['_merge']=='left_only'] ])
                            self.logger.info(f"need_updates merge: {len(sub_df)} worked\n")
                        break

                    except MemoryError as e:
                        self.logger.info(f"new_data ({sub_df.shape}) is too large to allocate memory for " +
                            f"need_updates df merge.\nMemoryError: {e}\nTrying again with {partitions + 1} partitions...\n")
                        partitions += 1
                        attempts += 1
                    # self.logger.info(f"End attempt # {attempts}\n")
                if attempts >= 50:
                    self.loggger.info("Max need_updates merge attempts exceeded, cannot perform " +
                        "updates on this repo.\n")
                else:
                    need_updates = need_updates.drop([column for column in list(need_updates.columns) if \
                        column not in action_map['update']['augur'] and column not in action_map['insert']['augur']],
                        axis='columns')

                    for column in action_map['insert']['augur']:
                        need_updates[f'b_{column}'] = need_updates[column]

                    need_updates = need_updates.drop([column for column in action_map['insert']['augur']], axis='columns')

        return need_insertion.to_dict('records'), need_updates.to_dict('records')


    def assign_tuple_action(self, new_data, table_values, update_col_map, duplicate_col_map, table_pkey, value_update_col_map={}):
        """ DEPRECATED
        SPG 9/15/2021 TODO -- Why is this deprecated?
            Include an extra key-value pair on each element of new_data that represents
            the action that should be taken with this element (i.e. 'need_insertion')

        :param new_data: List of dictionaries, data to be assigned an action to
        :param table_values: Pandas DataFrame, existing data in the database to check
            what action should be taken on the new_data depending on the presence of
            each element in this DataFrame
        :param update_col_map: Dictionary, maps the column names of the source data
            to the field names in our database for columns that should be checked for
            updates (if source data value != value in existing database row, then an
            update is needed). Key is source data column name, value is database field name.
            Example: {'id': 'gh_issue_id'}
        :param duplicate_col_map: Dictionary, maps the column names of the source data
            to the field names in our database for columns that should be checked for
            duplicates (if source data value == value in existing database row, then this
            element is a duplicate and would not need an insertion). Key is source data
            column name, value is database field name. Example: {'id': 'gh_issue_id'}
        :param table_pkey: String, the field name of the primary key of the table in
            the database that we are checking the table_values for.
        :param value_update_col_map: Dictionary, sometimes we add a new field to a table,
            and we want to trigger an update of that row in the database even if all of the
            data values are the same and would not need an update ordinarily. Checking for
            a specific existing value in the database field allows us to do this. The key is the
            name of the field in the database we are checking for a specific value to trigger
            an update, the value is the value we are checking for equality to trigger an update.
            Example: {'cntrb_id': None}
        :return: List of dictionaries, contains all the same elements of new_data, except
            each element now has an extra key-value pair with the key being 'flag', and
            the value being 'need_insertion', 'need_update', or 'none'
        """
        need_insertion_count = 0
        need_update_count = 0

        if type(table_values) == list:
            if len(table_values) > 0:
                table_values = pd.DataFrame(table_values, columns=table_values[0].keys())
            else:
                table_values = pd.DataFrame(table_values)

        for i, obj in enumerate(new_data):
            if type(obj) != dict:
                new_data[i] = {'flag': 'none'}
                continue

            obj['flag'] = 'none' # default of no action needed
            existing_tuple = None
            for db_dupe_key in list(duplicate_col_map.keys()):

                if table_values.isin([obj[duplicate_col_map[db_dupe_key]]]).any().any():
                    if table_values[table_values[db_dupe_key].isin(
                        [obj[duplicate_col_map[db_dupe_key]]])].to_dict('records'):

                        existing_tuple = table_values[table_values[db_dupe_key].isin(
                            [obj[duplicate_col_map[db_dupe_key]]])].to_dict('records')[0]
                    continue

                obj['flag'] = 'need_insertion'
                need_insertion_count += 1
                break

            if obj['flag'] == 'need_insertion':
                continue

            if not existing_tuple:
                self.logger.info('An existing tuple was not found for this data ' +
                    'point and we have reached the check-updates portion of assigning ' +
                    'tuple action, so we will now move to next data point\n')
                continue

            # If we need to check the values of the existing tuple to determine if an update is needed
            '''  This "value_check" is really really what I think we want to be doing for the update to issue status
                 TODO SPG 9/15/2021. '''

            for augur_col, value_check in value_update_col_map.items():
                not_nan_check = not (math.isnan(value_check) and math.isnan(existing_tuple[augur_col])) if value_check is not None else True
                if existing_tuple[augur_col] != value_check and not_nan_check:
                    continue
                self.logger.info("Found a tuple that needs an update for column: {}\n".format(augur_col))
                obj['flag'] = 'need_update'
                obj['pkey'] = existing_tuple[table_pkey]
                need_update_count += 1

            if obj['flag'] == 'need_update':
                self.logger.info('Already determined that current tuple needs update, skipping checking further updates. '
                    'Moving to next tuple.\n')
                continue

            # Now check the existing tuple's values against the response values to determine if an update is needed
            for col in update_col_map.keys():
                if update_col_map[col] not in obj:
                    continue
                if obj[update_col_map[col]] == existing_tuple[col]:
                    continue
                self.logger.info("Found a tuple that needs an update for column: {}\n".format(col))
                obj['flag'] = 'need_update'
                self.logger.info(existing_tuple)
                obj['pkey'] = existing_tuple[table_pkey]
                need_update_count += 1

        self.logger.info("Page recieved has {} tuples, while filtering duplicates this ".format(len(new_data)) +
            "was reduced to {} tuples, and {} tuple updates are needed.\n".format(need_insertion_count, need_update_count))
        return new_data

    def check_duplicates(self, new_data, table_values, key):
        """ Filters what items of the new_data json (list of dictionaries) that are not
        present in the table_values df

        :param new_data: List of dictionaries, new data to filter duplicates out of
        :param table_values: Pandas DataFrame, existing data to check what data is already
            present in the database
        :param key: String, key of each dict in new_data whose value we are checking
            duplicates with
        :return: List of dictionaries, contains elements of new_data that are not already
            present in the database
        """
        need_insertion = []
        for obj in new_data:
            if type(obj) != dict:
                continue
            if not table_values.isin([obj[key]]).any().any():
                need_insertion.append(obj)
        self.logger.info("Page recieved has {} tuples, while filtering duplicates this ".format(str(len(new_data))) +
            "was reduced to {} tuples.\n".format(str(len(need_insertion))))
        return need_insertion


    def get_max_id(self, table, column, default=25150, operations_table=False):
        """ Gets the max value (usually used for id/pk's) of any Integer column
            of any table

        :param table: String, the table that consists of the column you want to
            query a max value for
        :param column: String, the column that you want to query the max value for
        :param default: Integer, if there are no values in the
            specified column, the value of this parameter will be returned
        :param operations_table: Boolean, if True, this signifies that the table/column
            that is wanted to be queried is in the augur_operations schema rather than
            the augur_data schema. Default False
        :return: Integer, the max value of the specified column/table
        """
        maxIdSQL = s.sql.text("""
            SELECT max({0}.{1}) AS {1}
            FROM {0}
        """.format(table, column))
        db = self.db if not operations_table else self.helper_db
        rs = pd.read_sql(maxIdSQL, db, params={})
        if rs.iloc[0][column] is not None:
            max_id = int(rs.iloc[0][column]) + 1
            self.logger.info("Found max id for {} column in the {} table: {}\n".format(column, table, max_id))
        else:
            max_id = default
            self.logger.warning("Could not find max id for {} column in the {} table... " +
                "using default set to: {}\n".format(column, table, max_id))
        return max_id

    def get_table_values(self, cols, tables, where_clause=""):
        """ Can query all values of any column(s) from any table(s)
            with an optional where clause

        :param cols: List of Strings, column(s) that user wants to query
        :param tables: List of Strings, table(s) that user wants to query
        :param where_clause: String, optional where clause to filter the values
            queried
        :return: Pandas DataFrame, contains all values queried in the columns, tables, and
            optional where clause provided
        """
        table_str = tables[0]
        del tables[0]

        col_str = cols[0]
        del cols[0]

        for table in tables:
            table_str += ", " + table
        for col in cols:
            col_str += ", " + col

        table_values_sql = s.sql.text("""
            SELECT {} FROM {} {}
        """.format(col_str, table_str, where_clause))
        self.logger.info("Getting table values with the following PSQL query: \n{}\n".format(
            table_values_sql))
        values = pd.read_sql(table_values_sql, self.db, params={})
        return values


    def bulk_insert(
        self, table, insert=[], update=[], unique_columns=[], update_columns=[],
        max_attempts=3, attempt_delay=3, increment_counter=True, convert_float_int=False
    ):
        """ Performs bulk inserts/updates of the given data to the given table

            :param table: String, name of the table that we are inserting/updating rows
            :param insert: List of dicts, data points to insert
            :param update: List of dicts, data points to update, only needs key/value
                pairs of the update_columns and the unique_columns
            :param unique_columns: List of strings, column names that would uniquely identify any
                given data point
            :param update_columns: List of strings, names of columns that are being updated
            :param max_attempts: Integer, number of attempts to perform on inserting/updating
                before moving on
            :param attempt_delay: Integer, number of seconds to wait in between attempts
            :returns: SQLAlchemy database execution response object(s), contains metadata
                about number of rows inserted etc. This data is not often used.
        """

        self.logger.info(
            f"{len(insert)} insertions are needed and {len(update)} "
            f"updates are needed for {table}"
        )

        update_result = None
        insert_result = None

        if len(update) > 0:
            attempts = 0
            update_start_time = time.time()
            while attempts < max_attempts:
                try:
                    update_result = self.db.execute(
                        table.update().where(
                                eval(
                                    ' and '.join(
                                        [
                                            f"self.{table}_table.c.{key} == bindparam('b_{key}')"
                                            for key in unique_columns
                                        ]
                                    )
                                )
                            ).values(
                                {key: key for key in update_columns}
                            ),
                        update
                    )
                    if increment_counter:
                        self.update_counter += update_result.rowcount
                    self.logger.info(
                        f"Updated {update_result.rowcount} rows in "
                        f"{time.time() - update_start_time} seconds"
                    )
                    break
                except Exception as e:
                    self.logger.info(f"Warning! Error bulk updating data: {e}")
                    time.sleep(attempt_delay)
                attempts += 1

        if len(insert) > 0:

            insert_start_time = time.time()

            def psql_insert_copy(table, conn, keys, data_iter):
                """
                Execute SQL statement inserting data

                Parameters
                ----------
                table : pandas.io.sql.SQLTable
                conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
                keys : list of str
                    Column names
                data_iter : Iterable that iterates the values to be inserted
                """
                # gets a DBAPI connection that can provide a cursor
                dbapi_conn = conn.connection
                with dbapi_conn.cursor() as curs:
                    s_buf = io.StringIO()
                    writer = csv.writer(s_buf)
                    writer.writerows(data_iter)
                    s_buf.seek(0)

                    columns = ', '.join('"{}"'.format(k) for k in keys)
                    if table.schema:
                        table_name = '{}.{}'.format(table.schema, table.name)
                    else:
                        table_name = table.name

                    sql = 'COPY {} ({}) FROM STDIN WITH (FORMAT CSV, encoding "UTF-8")'.format(
                        table_name, columns)                        

                    #(FORMAT CSV, FORCE_NULL(column_name))

                    self.logger.debug(f'table name is: {table_name}, and columns are {columns}.')
                    self.logger.debug(f'sql is: {sql}')

                    #This causes the github worker to throw an error with pandas
                    #cur.copy_expert(sql=sql, file=self.text_clean(s_buf))
                    # s_buf_encoded = s_buf.read().encode("UTF-8")
                    #self.logger.info(f"this is the sbuf_encdoded {s_buf_encoded}")
                    try:
                        #Session=sessy.sessionmaker(bind=curs)
                        #session=Session()
                        #session.copy_expert(sql=sql, file=s_buf)
                        #copy_expert(sql=sql, file=s_buf)
                        curs.copy_expert(sql=sql, file=s_buf)
                        #session.commit()
                        #self.logger.info("message committed")
                        dbapi_conn.commit()
                        # self.logger.debug("good dog. record committed! Watson, come quick!!!")
                    except psycopg2.errors.UniqueViolation as e: 
                        self.logger.info(f"{e}")
                        dbapi_conn.rollback()                        
                    except Exception as e:
                        self.print_traceback("Bulk insert error", e, True)
                        dbapi_conn.rollback()

            try: 
                df = pd.DataFrame(insert)
                if convert_float_int:
                    df = self._convert_float_nan_to_int(df)
                df.to_sql(
                    schema = self.db_schema,
                    name=table.name,
                    con=self.db,
                    if_exists="append",
                    index=False,
                    #method=None,
                    method=psql_insert_copy,
                    #dtype=dict,
                    chunksize=1
                )
                if increment_counter:
                    self.insert_counter += len(insert)

                self.logger.info(
                    f"Inserted {len(insert)} rows in {time.time() - insert_start_time} seconds "
                    "thanks to postgresql's COPY FROM CSV! :)"
                )
            except Exception as e: 
                self.logger.info(f"Bulk insert error 2: {e}. exception registered.")

        return insert_result, update_result

    def text_clean(self, data, field):
        """ "Cleans" the provided field of each dict in the list of dicts provided
            by removing NUL (C text termination) characters
            Example: "\u0000"

            :param data: List of dicts
            :param field: String
            :returns: Same data list with each element's field updated with NUL characters
                removed
        """
        #self.logger.info(f"Original data point{field:datapoint[field]}")

        return [
            {
                **data_point,
                #field: data_point[field].replace("\x00", "\uFFFD")
                #self.logger.info(f"Null replaced data point{field:datapoint[field]}")
                ## trying to use standard python3 method for text cleaning here.
                # This was after `data_point[field]` for a while as `, "utf-8"` and did not work
                # Nay, it cause silent errors without insert; or was part of that hot mess.
                # field: bytes(data_point[field]).decode("utf-8", "ignore")
                field: bytes(data_point[field], "utf-8").decode("utf-8", "ignore").replace("\x00", "\uFFFD")
                #0x00
            } for data_point in data
        ]

    # def text_clean(self, data, field):
    #     """ "Cleans" the provided field of each dict in the list of dicts provided
    #         by removing NUL (C text termination) characters
    #         Example: "\u0000"

    #         :param data: List of dicts
    #         :param field: String
    #         :returns: Same data list with each element's field updated with NUL characters
    #             removed
    #     """
    #     return [
    #         {
    #             **data_point,
    #             field: data_point[field].replace("\x00", "\uFFFD")
    #         } for data_point in data
    #     ]

    def _add_nested_columns(self, df, column_names):
        # todo: support deeper nests (>1) and only expand necessary columns
        # todo: merge with _get_data_set_columns

        for column in column_names:
            self.logger.debug(f"column included: {column}.")
            if '.' not in column:
                continue
            # if the column is already present then we
            # dont' need to try to add it again
            if column in df.columns:
                continue
            root = column.split('.')[0]
            if root not in df.columns:
                df[root] = None
            expanded_column = pd.DataFrame(
                df[root].where(df[root].notna(), lambda x: [{}]).tolist()
            )

            expanded_column.columns = [
                f'{root}.{attribute}' for attribute in expanded_column.columns
            ]


            self.logger.debug('\n')
            self.logger.debug('\n')
            self.logger.debug('\n')
            self.logger.debug('\n')
            self.logger.debug(f'Expanded Columns Are:{expanded_column.columns}')
            self.logger.debug('\n')
            self.logger.debug('\n')
            self.logger.debug('\n')
            
            if column not in expanded_column.columns:
                expanded_column[column] = None
            try:
                df = df.join(expanded_column)
            except ValueError as e:
                # columns already added (happens if trying to expand the same column twice)
                # TODO: Catch this before by only looping unique prefixs?
                self.print_traceback("value error in _add_nested_columns", e, True)

            except Exception as e:
                self.print_traceback("_add_nested_columns", e, True)

            finally: 
                self.logger.debug(f"finished _add_nested_columns.")

        return df


    def enrich_data_primary_keys(
        self, source_data, table, gh_merge_fields, augur_merge_fields, in_memory=True
    ):

        ''' the gh_merge_fields are almost always direct from the source in the action map.
            the augur_merge fields are the fieldnames where augur perists the source values.
            These are almost never (never) the primary keys on our table. They are the natural
            keys at the source, I think, with some probability close to 1 (SPG 9/13/2021).'''

        ''' SPG 9/15/2021: This seems method may be the source of duplicate inserts that seem like
            they should not actually get run because we are specifying the natural key in the insert map.
            I really don't completely understand what we are doing here.  '''

        self.logger.info("Preparing to enrich data.\n")

        if source_data == None or len(source_data) == 0:
            self.logger.info("There is no source data to enrich.\n")
            return source_data

        source_df = self._add_nested_columns(pd.DataFrame(source_data), gh_merge_fields)

        if not in_memory:

            source_pk_columns = list(source_df.columns)
            ## This seems to be the biggest issue. The primary keys do not actually
            ## represent the natural key we are mapping for inserts.
            source_pk_columns.insert(0, list(table.primary_key)[0].name)

            (source_table, ), metadata, session = self._setup_postgres_merge(
                #This next line was commented out, which seems like it might be problematic
                #    Wouldn't we *want* to have all of this mapping included?
                #    [self._get_data_set_columns(source_data, gh_merge_fields)]
                #   However, it does turn out that this line creates the error:
                    #      2021-09-15 21:44:59,261,261ms [PID: 1942874] workers.github_worker.57631 [ERROR] Traceback (most recent call last):
                    #   File "/home/sean/github/release-test/workers/worker_base.py", line 180, in collect
                    #     model_method(message, repo_id)
                    #   File "/home/sean/github/release-test/workers/github_worker/github_worker.py", line 199, in issues_model
                    #     pk_source_issues = self._get_pk_source_issues()
                    #   File "/home/sean/github/release-test/workers/github_worker/github_worker.py", line 181, in _get_pk_source_issues
                    #     pk_source_issues_increment_insert(source_issues,action_map)
                    #   File "/home/sean/github/release-test/workers/github_worker/github_worker.py", line 166, in pk_source_issues_increment_insert
                    #     self.pk_source_issues += self.enrich_data_primary_keys(
                    #   File "/home/sean/github/release-test/workers/worker_persistance.py", line 928, in enrich_data_primary_keys
                    #     [self._get_data_set_columns(source_data, gh_merge_fields)]
                    # TypeError: list indices must be integers or slices, not list

                [source_df.to_dict(orient='records')]
            )

            source_pk = pd.DataFrame(

                # eval(
                #     "session.query("
                #         + ", ".join(
                #             [
                #                 f"table.c['{column}']" for column in [list(table.primary_key)[0].name]
                #                 + augur_merge_fields
                #             ]
                #         )
                #     + ")"
                # )
                session.query(
                    table.c[list(table.primary_key)[0].name],
                    source_table
                    # eval(
                    #     f"table.c['{list(table.primary_key)[0].name}'], "
                    #     + ", ".join(
                    #         [
                    #             f"source_table.c['{column}']" for column in source_pk_columns
                    #         ]
                    #     )
                    # )
                ).join(
                    source_table,
                    eval(
                        ' and '.join(
                            [
                                f"table.c['{table_column}'] == source_table.c['{source_column}']"
                                for table_column, source_column in zip(
                                    augur_merge_fields, gh_merge_fields
                                )
                            ]
                        )
                    )
                ).all(), columns=source_pk_columns  # gh_merge_fields
            )

            source_pk = self._eval_json_columns(source_pk)

            # source_pk, source_df = self.sync_df_types(
            #     source_pk, source_df, gh_merge_fields, gh_merge_fields
            # )
            # source_pk = source_pk.merge(source_df, how='inner', on=gh_merge_fields)

            self.logger.info("source_pk calculated successfully")

            self._close_postgres_merge(metadata, session)
            self.logger.info("Done")

        else:

            # s_tuple = s.tuple_([table.c[field] for field in augur_merge_fields])
            # s_tuple.__dict__['clauses'] = s_tuple.__dict__['clauses'][0].effective_value
            # s_tuple.__dict__['_type_tuple'] = []
            # for field in augur_merge_fields:
            #     s_tuple.__dict__['_type_tuple'].append(table.c[field].__dict__['type'])

            # try:
            #     primary_keys = self.db.execute(s.sql.select(
            #             [table.c[field] for field in augur_merge_fields] + [table.c[list(table.primary_key)[0].name]]
            #         ).where(
            #             s_tuple.in_(

            #                 list(source_df[gh_merge_fields].itertuples(index=False))
            #             ))).fetchall()
            # except psycopg2.errors.UniqueViolation as e: 
            # except psycopg2.errors.StatementTooComplex as e:
            self.logger.info("Retrieve pk statement too complex, querying all instead " +
                "and performing partitioned merge.\n")
            all_primary_keys = self.db.execute(s.sql.select(
                    [table.c[field] for field in augur_merge_fields] + [table.c[list(table.primary_key)[0].name]]
                )).fetchall()
            self.logger.info("Queried all")
            all_primary_keys_df = pd.DataFrame(all_primary_keys,
                columns=augur_merge_fields + [list(table.primary_key)[0].name])
            self.logger.info("Converted to df")

            source_df, all_primary_keys_df = self.sync_df_types(source_df, all_primary_keys_df,
                    gh_merge_fields, augur_merge_fields)

            self.logger.info("Synced df types")

            partitions = math.ceil(len(source_df) / 600)#1000)
            attempts = 0
            while attempts < 50:
                try:
                    source_pk = pd.DataFrame()
                    self.logger.info(f"Trying {partitions} partitions of new data, {len(all_primary_keys_df)} " +
                        "pk data points to enrich\n")
                    for sub_df in numpy.array_split(source_df, partitions):
                        self.logger.info(f"Trying a partition, len {len(sub_df)}\n")
                        source_pk = pd.concat([ source_pk, sub_df.merge(all_primary_keys_df, suffixes=('','_table'),
                            how='inner', left_on=gh_merge_fields, right_on=augur_merge_fields) ])
                        self.logger.info(f"source_pk merge: {len(sub_df)} worked\n")
                    break

                except MemoryError as e:
                    self.logger.info(f"new_data ({sub_df.shape}) is too large to allocate memory for " +
                        f"source_pk df merge.\nMemoryError: {e}\nTrying again with {partitions + 1} partitions...\n")
                    partitions += 1
                    attempts += 1
                # self.logger.info(f"End attempt # {attempts}\n")
            if attempts >= 50:
                self.logger.info("Max source_pk merge attempts exceeded, cannot perform " +
                    "updates on this repo.\n")
            else:
                self.logger.info(f"Data enrichment successful, length: {len(source_pk)}\n")

            # all_primary_keys_df.to_json(path_or_buf='all_primary_keys_df.json', orient='records')

            # all_primary_keys_dask_df = dd.from_pandas(all_primary_keys_df, chunksize=1000)
            # source_dask_df = dd.from_pandas(source_df, chunksize=1000)
            # result = json.loads(source_dask_df.merge(all_primary_keys_dask_df, suffixes=('','_table'),
            #     how='inner', left_on=gh_merge_fields, right_on=augur_merge_fields).compute(
            #     ).to_json(default_handler=str, orient='records'))
        return source_pk.to_dict(orient='records')

        # if len(primary_keys) > 0:
        #     primary_keys_df = pd.DataFrame(primary_keys,
        #         columns=augur_merge_fields + [list(table.primary_key)[0].name])
        # else:
        #     self.logger.info("There are no inserted primary keys to enrich the source data with.\n")
        #     return []

        # source_df, primary_keys_df = self.sync_df_types(source_df, primary_keys_df,
        #         gh_merge_fields, augur_merge_fields)

        # source_df = dd.from_pandas(source_df, chunksize=1000)
        # primary_keys_df = dd.from_pandas(primary_keys_df, chunksize=1000)

        # result = json.loads(source_df.merge(primary_keys_df, suffixes=('','_table'),
        #     how='inner', left_on=gh_merge_fields, right_on=augur_merge_fields).compute().to_json(
        #     default_handler=str, orient='records'))

        # self.logger.info("Data enrichment successful.\n")
        # return result

    def _eval_json_columns(self, df):
        if not len(df):
            return df
        for column in df.columns:
            first_valid_value = df.fillna(method='bfill').iloc[0][column]
            if isinstance(first_valid_value, str):
                if (
                    first_valid_value[0] == '{' and first_valid_value[-1] == '}'
                    or first_valid_value[0] == '[' and first_valid_value[-1] == ']'
                ):
                    df[column] = df[column].fillna("'null_placeholder'").apply(eval).replace(
                        "null_placeholder", numpy.nan
                    ).where(df[column].notna(), lambda x: [{}])
        return df

    def new_organize_needed_data(
        self, new_data, augur_table=None, where_clause=True, action_map={}
    ):

        self.logger.info(f"Beginning to organize needed data from {len(new_data)} data points...")

        if len(new_data) == 0:
            return [], []

        new_data_columns = pd.DataFrame(new_data).columns

        # # new_data_columns = copy.deepcopy(action_map['insert']['source'])
        # table_value_columns = copy.deepcopy(action_map['insert']['augur'])
        #
        # if 'update' in action_map:
        #     # new_data_columns += action_map['update']['source']
        #     table_value_columns += action_map['update']['augur']

        (new_data_table, ), metadata, session = self._setup_postgres_merge(
            [
                new_data
                # self._get_data_set_columns(new_data, new_data_columns)
            ]
        )

        need_insertion = pd.DataFrame(
            session.query(new_data_table).join(
                augur_table,
                eval(
                    ' and '.join(
                        [
                            f"augur_table.c['{table_column}'] == new_data_table.c['{source_column}']"
                            for table_column, source_column in zip(
                                action_map['insert']['augur'], action_map['insert']['source']
                            )
                        ]
                    )
                ), isouter=True
            ).filter(
                augur_table.c[action_map['insert']['augur'][0]] == None
            ).all(), columns=new_data_columns  # table_value_columns
        )

        need_insertion = self._eval_json_columns(need_insertion)

        # new_data_df = pd.DataFrame(new_data)

        # need_insertion, new_data_df = self.sync_df_types(
        #     need_insertion, new_data_df, table_value_columns, new_data_columns
        # )
        # need_insertion = need_insertion.merge(
        #     new_data_df, how='inner', left_on=table_value_columns, right_on=new_data_columns
        # )

        self.logger.info("need_insertion calculated successfully")

        need_updates = pd.DataFrame(columns=new_data_columns)
        if 'update' in action_map:
            need_updates = pd.DataFrame(
                session.query(new_data_table).join(
                    augur_table,
                    s.and_(
                        eval(
                            ' and '.join(
                                [
                                    (
                                        f"augur_table.c.{table_column} "
                                        f"== new_data_table.c.{source_column}"
                                    ) for table_column, source_column in zip(
                                        action_map['insert']['augur'],
                                        action_map['insert']['source']
                                    )
                                ]
                            )
                        ),

                        eval(
                            ' and '.join(
                                [
                                    (
                                        f"augur_table.c.{table_column} "
                                        f"!= new_data_table.c.{source_column}"
                                    ) for table_column, source_column in zip(
                                        action_map['update']['augur'],
                                        action_map['update']['source']
                                    )
                                ]
                            )
                        )
                    )
                ).all(), columns=new_data_columns
            )
            self.logger.info("need_updates calculated successfully")

        self._close_postgres_merge(metadata, session)

        self.logger.info(
            f"Table needs {len(need_insertion)} insertions and "
            f"{len(need_updates)} updates.\n"
        )

        return need_insertion.to_dict('records'), need_updates.to_dict('records')

    def get_relevant_columns(self, table, action_map={}):
        columns = copy.deepcopy(action_map['update']['augur']) if 'update' in action_map else []
        columns += action_map['value_update']['augur'] if 'value_update' in action_map else []
        columns += action_map['insert']['augur'] if 'insert' in action_map else []
        try:
            relevant_columns_return = [table.c[column] for column in columns + [list(table.primary_key)[0].name]]
            return relevant_columns_return
        except Exception as e:
            self.logger.info(f"Column may not exist in the database -- registered exception: {e}.")
            self.print_traceback("", e, True)

    def retrieve_tuple(self, key_values, tables):
        table_str = tables[0]
        del tables[0]

        key_values_items = list(key_values.items())
        for col, value in [key_values_items[0]]:
            where_str = col + " = '" + value + "'"
        del key_values_items[0]

        for col, value in key_values_items:
            where_str += ' AND ' + col + " = '" + value + "'"
        for table in tables:
            table_str += ", " + table

        retrieveTupleSQL = s.sql.text("""
            SELECT * FROM {} WHERE {}
            """.format(table_str, where_str))
        values = json.loads(
            pd.read_sql(retrieveTupleSQL, self.db, params={}).to_json(orient="records")
        )
        return values

    """
    Prints the traceback when an exception occurs
    
    Params
        exception_message: String - Explain the location that the exception occurred
        exception: String - Exception object that python returns during an Exception
        debug_log: Boolean - Determines whether the message is printed to the debug log or info log
        
    Notes
        To print the location of the exception to the info log and the traceback to the debug log, 
        add a self.logger.info call then call self.print_traceback("", e) to print the traceback to only the debug log
    """
    def print_traceback(self, exception_message, exception, debug_log=True):

        if debug_log:
            self.logger.debug(f"{exception_message}. ERROR: {exception}", exc_info=sys.exc_info())
        else:
            self.logger.info(f"{exception_message}. ERROR: {exception}", exc_info=sys.exc_info())
