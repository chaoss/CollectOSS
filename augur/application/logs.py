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
import augur.tasks.git.facade_tasks as facade_tasks
import augur.tasks.github.issue_tasks as issue_tasks
import augur.tasks.start_tasks as start_tasks

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
    #handler.setFormatter(fmt=fmt)
    handler.setLevel(level)

    return handler

#TODO dynamically define loggers for every task names.
class TaskLogConfig():

    def __init__(self,disable_logs=False,reset_logfiles=True,base_log_dir=ROOT_AUGUR_DIRECTORY + "/logs/"):
        if reset_logfiles is True:
            try:
                shutil.rmtree(base_log_dir)
            except FileNotFoundError as e:
                pass

        self.base_log_dir = Path(base_log_dir)

        self.disable_logs = disable_logs

        self.base_log_dir.mkdir(exist_ok=True)

        task_files = [facade_tasks,issue_tasks,start_tasks]

        self.logger_names = []

        self.__initLoggers(task_files,logging.INFO)
    
    def __initLoggers(self,task_modules,logLevel):
        
        
        for module in task_modules:
            """
            get the name strings of all functions in each module that have the celery.task decorator.
            
            Celery task functions with the decorator are of type celery.local.PromiseProxy
            """

            allTasksInModule = [str(obj[0]) for obj in getmembers(module) if isinstance(obj[1],PromiseProxy)]
            
            #seperate log files by module
            #module_dir = Path(str(self.base_log_dir) + "/" +)

            for task in allTasksInModule:
                #Create logging profiles for each task in seperate files.
                lg = logging.getLogger(task)
                self.logger_names.append(task)

                #Don't bother if logs are disabled.
                if self.disable_logs:
                    lg.disabled = True
                    break
                
                #Put logs in seperate folders by module.
                module_folder = Path(str(self.base_log_dir) + "/" + module.__name__ + "/")
                module_folder.mkdir(exist_ok=True)

                #Each task should have a seperate folder
                task_folder = Path(str(module_folder) + "/" + str(task) + "/")
                task_folder.mkdir(exist_ok=True)

                lg.setLevel(logLevel)

                #Absolute path to log file
                file = str(task_folder) + "/" + str(task)

                stream = logging.StreamHandler()
                stream.setLevel(logLevel)
                lg.addHandler(stream)

                #Create file handlers for each relevant log level and make them colorful
                lg.addHandler(genHandler((file + ".info"), SIMPLE_FORMAT_STRING, logging.INFO)) 
                coloredlogs.install(level=logging.INFO,logger=lg,fmt=SIMPLE_FORMAT_STRING)

                lg.addHandler(genHandler((file + ".err"), ERROR_FORMAT_STRING, logging.ERROR)) 
                coloredlogs.install(level=logging.ERROR,logger=lg,fmt=ERROR_FORMAT_STRING)

                lg.addHandler(genHandler((file + ".debug"), VERBOSE_FORMAT_STRING, logging.DEBUG)) 
                coloredlogs.install(level=logging.DEBUG,logger=lg,fmt=VERBOSE_FORMAT_STRING)
                
                lg.propagate = False

        
        def getLoggerNames(self):
            return self.logger_names


class AugurLogger():
    def __init__(self, logger_name, disable_logs=False,reset_logfiles=True,base_log_dir="/home/isaac/logs"):
        if reset_logfiles is True:
            try:
                shutil.rmtree(base_log_dir)
            except FileNotFoundError as e:
                pass

        self.base_log_dir = Path(base_log_dir)

        self.disable_logs = disable_logs

        self.base_log_dir.mkdir(exist_ok=True)

        self.logger_name = logger_name

        self.lg = logging.getLogger(self.logger_name)

        #Don't bother if logs are disabled.
        if self.disable_logs:
            self.lg.disabled = True
            return

        file = str(self.base_log_dir) + "/" + str(self.logger_name)

        self.lg.addHandler(genHandler((file + ".info"), SIMPLE_FORMAT_STRING, logging.INFO))
        coloredlogs.install(level=logging.INFO,logger=self.lg,fmt=SIMPLE_FORMAT_STRING)

        self.lg.addHandler(genHandler((file + ".err"), ERROR_FORMAT_STRING, logging.ERROR))
        coloredlogs.install(level=logging.ERROR,logger=self.lg,fmt=ERROR_FORMAT_STRING)

        self.lg.addHandler(genHandler((file + ".debug"), VERBOSE_FORMAT_STRING, logging.DEBUG))
        coloredlogs.install(level=logging.DEBUG,logger=self.lg,fmt=VERBOSE_FORMAT_STRING)

        self.lg.propogate = False
    
    def __str__(self):
        return self.logger_name

    def get_logger(self):
        return self.lg

