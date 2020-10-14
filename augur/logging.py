#SPDX-License-Identifier: MIT
import logging
import logging.config
import logging.handlers
from logging import FileHandler, StreamHandler, Formatter
from multiprocessing import Process, Queue, Event, current_process
from time import sleep
import os
from pathlib import Path
import atexit
import shutil
import coloredlogs
from copy import deepcopy

from augur import ROOT_AUGUR_DIRECTORY

logger = logging.getLogger(__name__)

class AugurLogging():

    simple_format_string = "[%(process)d] %(name)s [%(levelname)s] %(message)s"
    verbose_format_string = "%(asctime)s,%(msecs)dms [PID: %(process)d] %(name)s [%(levelname)s] %(message)s"
    cli_format_string = "CLI: [%(module)s.%(funcName)s] [%(levelname)s] %(message)s"
    config_format_string = "[%(levelname)s] %(message)s"
    error_format_string = "%(asctime)s [PID: %(process)d] %(name)s [%(funcName)s() in %(filename)s:L%(lineno)d] [%(levelname)s]: %(message)s"

    @staticmethod
    def get_log_directories(augur_config, reset_logfiles=True):
        LOGS_DIRECTORY = augur_config.get_value("Logging", "logs_directory")

        if LOGS_DIRECTORY[0] != "/":
            LOGS_DIRECTORY = ROOT_AUGUR_DIRECTORY + "/" + LOGS_DIRECTORY

        if LOGS_DIRECTORY[-1] != "/":
            LOGS_DIRECTORY += "/"

        if reset_logfiles is True:
            try:
                shutil.rmtree(LOGS_DIRECTORY)
            except FileNotFoundError as e:
                pass

        Path(LOGS_DIRECTORY).mkdir(exist_ok=True)

        return LOGS_DIRECTORY

    def __init__(self, disable_logs=False, reset_logfiles=True):
        self.stop_event = None
        self.LOGS_DIRECTORY = None
        self.WORKER_LOGS_DIRECTORY = None
        self.LOG_LEVEL = None
        self.VERBOSE = None
        self.QUIET = None
        self.DEGBUG = None

        self.logfile_config = None
        self.housekeeper_job_config = None

        self._reset_logfiles = reset_logfiles

        self.formatters = {
            "simple": {
                "class": "logging.Formatter",
                "format": AugurLogging.simple_format_string
            },
            "verbose": {
                "class": "logging.Formatter",
                "format": AugurLogging.verbose_format_string
            },
            "cli": {
                "class": "logging.Formatter",
                "format": AugurLogging.cli_format_string
            },
            "config": {
                "class": "logging.Formatter",
                "format": AugurLogging.config_format_string
            },
            "error": {
                "class": "logging.Formatter",
                "format": AugurLogging.error_format_string
            }
        }

        self._configure_cli_logger()

        level = logging.INFO
        config_handler = StreamHandler()
        config_handler.setFormatter(Formatter(fmt=AugurLogging.config_format_string))
        config_handler.setLevel(level)

        config_initialization_logger = logging.getLogger("augur.config")
        config_initialization_logger.setLevel(level)
        config_initialization_logger.handlers = []
        config_initialization_logger.addHandler(config_handler)
        config_initialization_logger.propagate = False

        coloredlogs.install(level=level, logger=config_initialization_logger, fmt=AugurLogging.config_format_string)

        if disable_logs:
            self._disable_all_logging()

    def _disable_all_logging(self):
        for logger in ["augur", "augur.application", "augur.housekeeper", "augur.config", "augur.cli", "root"]:
            lg = logging.getLogger(logger)
            lg.disabled = True

    def _configure_cli_logger(self):
        cli_handler = StreamHandler()
        cli_handler.setLevel(logging.INFO)

        cli_logger = logging.getLogger("augur.cli")
        cli_logger.setLevel(logging.INFO)
        cli_logger.handlers = []
        cli_logger.addHandler(cli_handler)
        cli_logger.propagate = False

        coloredlogs.install(level=logging.INFO, logger=cli_logger, fmt=AugurLogging.cli_format_string)

    def _set_config(self, augur_config):
        self.LOGS_DIRECTORY = AugurLogging.get_log_directories(augur_config, self._reset_logfiles)
        self.LOG_LEVEL = augur_config.get_value("Logging", "log_level")
        self.QUIET = int(augur_config.get_value("Logging", "quiet"))
        self.DEBUG = int(augur_config.get_value("Logging", "debug"))
        self.VERBOSE = int(augur_config.get_value("Logging", "verbose"))
        # self.JOB_NAMES = [job["model"] for job in deepcopy(augur_config.get_value("Housekeeper", "jobs"))]

        if self.QUIET:
            self._disable_all_logging()

        if self.DEBUG:
            self.LOG_LEVEL = "DEBUG"
            self.VERBOSE = True

        if self.VERBOSE:
            self.FORMATTER = "verbose"
        else:
            self.FORMATTER = "simple"
        self.format_string = self.formatters[self.FORMATTER]["format"]

    def configure_logging(self, augur_config):
        self._set_config(augur_config)
        self._configure_logfiles()
        self._configure_cli_logger()
        self._configure_gunicorn_logging()

    def _configure_logfiles(self):
        self.logfile_config = {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": self.formatters,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": self.FORMATTER,
                    "level": self.LOG_LEVEL
                },
                "logfile": {
                    "class": "logging.FileHandler",
                    "filename": self.LOGS_DIRECTORY + "augur.log",
                    "mode": "a",
                    "level": self.LOG_LEVEL,
                    "formatter": self.FORMATTER
                },
                "errorfile": {
                    "class": "logging.FileHandler",
                    "filename": self.LOGS_DIRECTORY + "augur.err",
                    "mode": "a",
                    "level": logging.WARNING,
                    "formatter": "error"
                },
                "server_logfile": {
                    "class": "logging.FileHandler",
                    "filename": self.LOGS_DIRECTORY + "gunicorn.log",
                    "mode": "a",
                    "level": self.LOG_LEVEL,
                    "formatter": self.FORMATTER
                },
                "housekeeper_logfile": {
                    "class": "logging.FileHandler",
                    "filename": self.LOGS_DIRECTORY + "housekeeper.log",
                    "mode": "a",
                    "level": self.LOG_LEVEL,
                    "formatter": self.FORMATTER
                },
                "housekeeper_errorfile": {
                    "class": "logging.FileHandler",
                    "filename": self.LOGS_DIRECTORY + "housekeeper.err",
                    "mode": "a",
                    "level": logging.WARNING,
                    "formatter": "error",
                },
            },
            "loggers": {
                "augur": {
                    "handlers": ["console", "logfile", "errorfile"],
                    "level": self.LOG_LEVEL
                },
                "augur.server": {
                    "handlers": ["server_logfile"],
                    "level": self.LOG_LEVEL,
                    "propagate": False
                },
                "augur.housekeeper": {
                    "handlers": ["housekeeper_logfile", "housekeeper_errorfile"],
                    "level": self.LOG_LEVEL,
                },
                "augur.jobs": {
                    "handlers": ["housekeeper_logfile", "housekeeper_errorfile", "logfile", "errorfile"],
                    "level": self.LOG_LEVEL,
                    "propagate": False
                }
            },
            "root": {
                "handlers": [],
                "level": self.LOG_LEVEL
            }
        }

        logging.config.dictConfig(self.logfile_config)
        for logger_name in ["augur", "augur.housekeeper", "augur.jobs"]:
            coloredlogs.install(logger=logging.getLogger(logger_name), level=self.LOG_LEVEL, fmt=self.format_string)

        logger.debug("Logfiles initialized at " + self.LOGS_DIRECTORY)

    def initialize_housekeeper_logging_listener(self):
            queue = Queue()
            self.housekeeper_job_config = {
                "version": 1,
                "disable_existing_loggers": True,
                "formatters": self.formatters,
                "handlers": {
                    "queue": {
                        "class": "logging.handlers.QueueHandler",
                        "queue": queue
                    }
                },
                "root": {
                    "handlers": ["queue"],
                    "level": self.LOG_LEVEL
                }
            }

            stop_event = Event()
            self.lp = Process(target=logging_listener_process, name='housekeeper_logging_listener',
                 args=(queue, stop_event, self.logfile_config))
            self.lp.start()
            sleep(2) # just to let it fully start up
            self.stop_event = stop_event
            logger.debug("Houseekeeper logging listener initialized")

    def get_config(self):
        return {
            "log_level": self.LOG_LEVEL,
            "quiet": self.QUIET,
            "verbose": self.VERBOSE,
            "debug": self.DEBUG,
            "format_string": self.format_string
        }

    def _configure_gunicorn_logging(self):
        gunicorn_log_file = self.LOGS_DIRECTORY + "gunicorn.log"
        self.gunicorn_logging_options = {
            "errorlog": gunicorn_log_file,
            "accesslog": gunicorn_log_file,
            "loglevel": self.LOG_LEVEL,
            "capture_output": False
        }

def logging_listener_process(queue, stop_event, config):
    """
    This could be done in the main process, but is just done in a separate
    process for illustrative purposes.

    This initialises logging according to the specified configuration,
    starts the listener and waits for the main process to signal completion
    via the event. The listener is then stopped, and the process exits.
    """
    logging.config.dictConfig(config)
    listener = logging.handlers.QueueListener(queue, AugurLoggingHandler())
    listener.start()
    try:
        stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()

class AugurLoggingHandler:
    """
    A simple handler for logging events. It runs in the listener process and
    dispatches events to loggers based on the name in the received record,
    which then get dispatched, by the logging system, to the handlers
    configured for those loggers.
    """

    def handle(self, record):
        if record.name == "root":
            logger = logging.getLogger()
        else:
            logger = logging.getLogger(record.name)

        record.processName = '%s (for %s)' % (current_process().name, record.processName)
        logger.handle(record)
