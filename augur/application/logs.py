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
from celery.local import PromiseProxy


import os
ROOT_AUGUR_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# logger = logging.getLogger(__name__)


SIMPLE_FORMAT_STRING = "[%(process)d] %(name)s [%(levelname)s] %(message)s"
VERBOSE_FORMAT_STRING = "%(asctime)s,%(msecs)dms [PID: %(process)d] %(name)s [%(levelname)s] %(message)s"
CLI_FORMAT_STRING = "CLI: [%(module)s.%(funcName)s] [%(levelname)s] %(message)s"
CONFIG_FORMAT_STRING = "[%(levelname)s] %(message)s"
ERROR_FORMAT_STRING = "%(asctime)s [PID: %(process)d] %(name)s [%(funcName)s() in %(filename)s:L%(lineno)d] [%(levelname)s]: %(message)s"

#Deal with creating the handler in one line with proper handler and log level
def genHandler(file,fmt,level):
    handler = FileHandler(filename=file,mode='a')
    formatter = logging.Formatter(fmt=fmt)
    handler.setFormatter(fmt=formatter)
    handler.setLevel(level)

    return handler

#TODO dynamically define loggers for every task names.
class TaskLogConfig():
    def __init__(self, all_tasks, disable_log_files=False,reset_logfiles=True,base_log_dir="/var/log/augur",logLevel=logging.INFO,list_of_task_modules=None):
        if reset_logfiles is True:
            try:
                shutil.rmtree(base_log_dir)
            except FileNotFoundError as e:
                pass

        self.base_log_dir = Path(base_log_dir)

        self.disable_log_files = disable_log_files

        self.base_log_dir.mkdir(exist_ok=True)

        self.logger_names = []

        self.__initLoggers(all_tasks, logLevel)
    
    def __initLoggers(self,task_names_grouped,logLevel):

        for module, task_list in task_names_grouped.items():
            for task in task_list:
                #Create logging profiles for each task in seperate files.
                lg = logging.getLogger(task)
                self.logger_names.append(task)

                lg.setLevel(logLevel)

                stream = logging.StreamHandler()
                stream.setLevel(logLevel)
                lg.addHandler(stream)

                if not self.disable_log_files:
                
                    #Put logs in seperate folders by module.
                    module_folder = Path(str(self.base_log_dir) + "/" + str(module) + "/")
                    module_folder.mkdir(exist_ok=True)

                    #Each task should have a seperate folder
                    task_folder = Path(str(module_folder) + "/" + str(task) + "/")
                    task_folder.mkdir(exist_ok=True)

                    #Absolute path to log file
                    file = str(task_folder) + "/" + str(task)

                    #Create file handlers for each relevant log level and make them colorful
                    lg.addHandler(genHandler((file + ".info"), SIMPLE_FORMAT_STRING, logging.INFO))
                    lg.addHandler(genHandler((file + ".err"), ERROR_FORMAT_STRING, logging.ERROR))
                    if logLevel == logging.DEBUG:
                        lg.addHandler(genHandler((file + ".debug"), VERBOSE_FORMAT_STRING, logging.DEBUG))

                coloredlogs.install(level=logging.INFO,logger=lg,fmt=SIMPLE_FORMAT_STRING)                
                coloredlogs.install(level=logging.ERROR,logger=lg,fmt=ERROR_FORMAT_STRING)

                if logLevel == logging.DEBUG:
                    coloredlogs.install(level=logging.DEBUG,logger=lg,fmt=VERBOSE_FORMAT_STRING)

                lg.propagate = False

        
        def getLoggerNames(self):
            return self.logger_names


class AugurLogger():
    def __init__(self, logger_name, disable_log_files=False,reset_logfiles=True,base_log_dir="/home/isaac/logs",logLevel=logging.INFO):
        if reset_logfiles is True:
            try:
                shutil.rmtree(base_log_dir)
            except FileNotFoundError as e:
                pass

        self.base_log_dir = Path(base_log_dir)

        self.disable_log_files = disable_log_files

        self.base_log_dir.mkdir(exist_ok=True)

        self.logger_name = logger_name

        self.lg = logging.getLogger(self.logger_name)

        stream = logging.StreamHandler()
        stream.setLevel(logLevel)
        lg.addHandler(stream)

        #Don't bother if file logs are disabled.
        if not self.disable_log_files:
            file = str(self.base_log_dir) + "/" + str(self.logger_name)
            self.lg.addHandler(genHandler((file + ".info"), SIMPLE_FORMAT_STRING, logging.INFO))
            self.lg.addHandler(genHandler((file + ".err"), ERROR_FORMAT_STRING, logging.ERROR))
            self.lg.addHandler(genHandler((file + ".debug"), VERBOSE_FORMAT_STRING, logging.DEBUG))

        coloredlogs.install(level=logging.INFO,logger=self.lg,fmt=SIMPLE_FORMAT_STRING)
        coloredlogs.install(level=logging.ERROR,logger=self.lg,fmt=ERROR_FORMAT_STRING)
        coloredlogs.install(level=logging.DEBUG,logger=self.lg,fmt=VERBOSE_FORMAT_STRING)

        self.lg.propagate = False
    
    def __str__(self):
        return self.logger_name

    def get_logger(self):
        return self.lg

