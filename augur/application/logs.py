#SPDX-License-Identifier: MIT
from __future__ import annotations
import logging
import logging.config
import logging.handlers
from logging import FileHandler, StreamHandler, Formatter
from multiprocessing import Process, Queue, Event, current_process
from inspect import getmembers, isfunction
from time import sleep
import os
from pathlib import Path
import atexit
import shutil
import coloredlogs
from copy import deepcopy
import typing
from sqlalchemy.orm import Session

from augur.application.db.models import Config 
from augur.application.config import convert_type_of_value
from augur.application.db.util import execute_session_query

ROOT_AUGUR_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


SIMPLE_FORMAT_STRING = "[%(process)d] %(name)s [%(levelname)s] %(message)s"
VERBOSE_FORMAT_STRING = "%(asctime)s,%(msecs)dms [PID: %(process)d] %(name)s [%(levelname)s] %(message)s"
CLI_FORMAT_STRING = "CLI: [%(module)s.%(funcName)s] [%(levelname)s] %(message)s"
CONFIG_FORMAT_STRING = "[%(levelname)s] %(message)s"
ERROR_FORMAT_STRING = "%(asctime)s [PID: %(process)d] %(name)s [%(funcName)s() in %(filename)s:L%(lineno)d] [%(levelname)s]: %(message)s"

# get formatter for the specified log level
def getFormatter(logLevel):

    if logLevel == logging.INFO:
        return logging.Formatter(fmt=SIMPLE_FORMAT_STRING)

    elif logLevel == logging.DEBUG:
        return logging.Formatter(fmt=VERBOSE_FORMAT_STRING)

    elif logLevel == logging.ERROR:
        return logging.Formatter(fmt=ERROR_FORMAT_STRING)

# create a file handler and set the format and log level
def create_file_handler(file, formatter, level):
    handler = FileHandler(filename=file, mode='a')
    handler.setFormatter(fmt=formatter)
    handler.setLevel(level)

    return handler

# function to create two file handlers and add them to a logger  
def initialize_file_handlers(logger, file, log_level):

    # if DEBUG is enabled then create a DEBUG handler which will log all logs
    if log_level == logging.DEBUG:
        info_file_handler = create_file_handler(f"{file}.info", getFormatter(logging.DEBUG), logging.DEBUG)
    else:
        info_file_handler = create_file_handler(f"{file}.info", getFormatter(logging.INFO), logging.INFO)

    error_file_handler = create_file_handler(f"{file}.error", getFormatter(logging.ERROR), logging.ERROR)

    logger.addHandler(info_file_handler)
    logger.addHandler(error_file_handler)


    
# function to create a StreamHandler and add them to a logger
def initialize_stream_handler(logger, log_level):
    
    stream = logging.StreamHandler()
    stream.setLevel(log_level)
    stream.setFormatter(getFormatter(log_level))
    logger.addHandler(stream)
    coloredlogs.install(level=log_level,logger=logger) 

def get_log_config():
    
    from augur.application.db.engine import create_database_engine

    # we are using this session instead of the 
    # DatabaseSession class because the DatabaseSession 
    # class requires a logger, and we are setting up logger thigns here 
    engine = create_database_engine()
    session = Session(engine)

    query = session.query(Config).filter_by(section_name="Logging")
    section_data = execute_session_query(query, 'all')

    session.close()
    engine.dispose()
        
    section_dict = {}
    for setting in section_data:
        setting_dict = setting.__dict__

        setting_dict = convert_type_of_value(setting_dict)

        setting_name = setting_dict["setting_name"]
        setting_value = setting_dict["value"]

        section_dict[setting_name] = setting_value

    return section_dict


#TODO dynamically define loggers for every task names.
class TaskLogConfig():
    def __init__(self, all_tasks, disable_log_files=False,reset_logfiles=False,base_log_dir=ROOT_AUGUR_DIRECTORY + "/logs/"):
        
        log_config = get_log_config()

        if log_config["logs_directory"] != "":
            base_log_dir=log_config["logs_directory"]

        if reset_logfiles is True:
            try:
                print("(tasks) Reseting log files")
                shutil.rmtree(base_log_dir)
            except FileNotFoundError as e:
                pass

        if log_config["log_level"].lower() == "debug":
            self.logLevel = logging.DEBUG
        else:
            self.logLevel = logging.INFO

        self.base_log_dir = Path(base_log_dir)

        self.disable_log_files = disable_log_files

        self.base_log_dir.mkdir(exist_ok=True)

        self.logger_names = []

        self.__initLoggers(all_tasks)
    
    def __initLoggers(self,task_names_grouped):

        print("Creating task logs")

        for module, task_list in task_names_grouped.items():
            for task in task_list:
                #Create logging profiles for each task in seperate files.
                lg = logging.getLogger(task)
                self.logger_names.append(task)

                # set the log level of the logger
                lg.setLevel(self.logLevel)

                initialize_stream_handler(lg, self.logLevel)
                
                if not self.disable_log_files:
                
                    self.initialize_task_file_logging(lg, module, task)

                lg.propagate = False

    def initialize_task_file_logging(self, logger, module, task):

        #Put logs in seperate folders by module.
        module_folder = Path(str(self.base_log_dir) + "/" + str(module) + "/")
        module_folder.mkdir(exist_ok=True)

        #Each task should have a seperate folder
        task_folder = Path(str(module_folder) + "/" + str(task) + "/")
        task_folder.mkdir(exist_ok=True)

        #Absolute path to log file
        file = str(task_folder) + "/" + str(task)

        initialize_file_handlers(logger, file, self.logLevel)

        
    def getLoggerNames(self):
        return self.logger_names


class AugurLogger():
    def __init__(self, logger_name, disable_log_files=False,reset_logfiles=False,base_log_dir=ROOT_AUGUR_DIRECTORY + "/logs/"):
        
        log_config = get_log_config()
        
        if log_config["logs_directory"] != "":
            base_log_dir=log_config["logs_directory"]

        if reset_logfiles is True:
            try:
                print("(augur) Reseting log files")
                shutil.rmtree(base_log_dir)
            except FileNotFoundError as e:
                pass

        if log_config["log_level"].lower() == "debug":
            self.logLevel = logging.DEBUG
        else:
            self.logLevel = logging.INFO

        self.base_log_dir = Path(base_log_dir)

        self.disable_log_files = disable_log_files

        self.base_log_dir.mkdir(exist_ok=True)

        self.logger_name = logger_name

        self.lg = logging.getLogger(self.logger_name)

        initialize_stream_handler(self.lg, self.logLevel)

        #Don't bother if file logs are disabled.
        if not self.disable_log_files:
           self.initialize_augur_logger_file_logging(self.lg)

        self.lg.propagate = False

    def initialize_augur_logger_file_logging(self, logger):

        file = str(self.base_log_dir) + "/" + str(self.logger_name)

        initialize_file_handlers(logger, file, self.logLevel)
    
    def __str__(self):
        return self.logger_name

    def get_logger(self):
        return self.lg

