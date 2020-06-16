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

from augur import ROOT_AUGUR_DIRECTORY

logger = logging.getLogger(__name__)

class AugurLogging():

    simple_format_string = "[%(process)d] %(name)s [%(levelname)s] %(message)s"
    verbose_format_string = "%(asctime)s [%(process)d] %(name)s.%(funcName)s() [%(levelname)s] %(message)s"

    @staticmethod
    def get_log_directories(augur_config):
        LOGS_DIRECTORY = augur_config.get_value("Logging", "logs_directory")

        if LOGS_DIRECTORY[0] != "/":
            LOGS_DIRECTORY = ROOT_AUGUR_DIRECTORY + "/" + LOGS_DIRECTORY

        if LOGS_DIRECTORY[-1] != "/":
            LOGS_DIRECTORY += "/"

        WORKER_LOGS_DIRECTORY = LOGS_DIRECTORY + "/workers/"

        return LOGS_DIRECTORY, WORKER_LOGS_DIRECTORY

    def __init__(self, augur_config, reset_logfiles=True):
        self.stop_event = None
        self.LOGS_DIRECTORY, self.WORKER_LOGS_DIRECTORY = AugurLogging.get_log_directories(augur_config)

        if reset_logfiles is True:
            try:
                shutil.rmtree(self.LOGS_DIRECTORY)
            except FileNotFoundError as e:
                pass

        Path(self.LOGS_DIRECTORY).mkdir(exist_ok=True)
        Path(self.WORKER_LOGS_DIRECTORY).mkdir(exist_ok=True)

        self.LOG_LEVEL = augur_config.get_value("Logging", "log_level")
        self.QUIET = augur_config.get_value("Logging", "quiet")
        self.DEBUG = augur_config.get_value("Logging", "debug")
        self.VERBOSE = augur_config.get_value("Logging", "verbose")

        if self.VERBOSE:
            self.FORMATTER = "verbose"
        else:
            self.FORMATTER = "simple"

        if self.DEBUG:
            self.LOG_LEVEL = "DEBUG"
            self.FORMATTER = "verbose"

        self.formatters = {
            "simple": {
                "class": "logging.Formatter",
                "format": AugurLogging.simple_format_string
            },
            "verbose": {
                "class": "logging.Formatter",
                "format": AugurLogging.verbose_format_string
            }
        }
        self.format_string = self.formatters[self.FORMATTER]["format"]

        self._initial_config = {
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
                    "formatter": self.FORMATTER,
                    "level": self.LOG_LEVEL
                },
                "errorfile": {
                    "class": "logging.FileHandler",
                    "filename": self.LOGS_DIRECTORY + "augur.err",
                    "mode": "a",
                    "level": logging.ERROR,
                    "formatter": self.FORMATTER
                },
                "server_log": {
                    "class": "logging.FileHandler",
                    "filename": self.LOGS_DIRECTORY + "gunicorn.log",
                    "level": self.LOG_LEVEL,
                    "mode": "a",
                    "formatter": self.FORMATTER
                },
                "housekeeper_jobs": {
                    "class": "logging.FileHandler",
                    "filename": self.LOGS_DIRECTORY + "housekeeper.log",
                    "level": self.LOG_LEVEL,
                    "mode": "a",
                    "formatter": self.FORMATTER
                },
                "housekeeper_errors": {
                    "class": "logging.FileHandler",
                    "filename": self.LOGS_DIRECTORY + "housekeeper.err",
                    "mode": "a",
                    "formatter": self.FORMATTER,
                    "level": logging.ERROR
                },
            },
            "loggers": {
                "augur": {
                    "handlers": ["logfile", "errorfile"],
                    "level": self.LOG_LEVEL
                },
                "augur.server": {
                    "handlers": ["errorfile", "server_log"],
                    "level": self.LOG_LEVEL,
                    "propagate": False
                },
                "augur.cli": {
                    "handlers": ["console"],
                    "level": self.LOG_LEVEL,
                    "propagate": False
                },
                "augur.housekeeper": {
                    "handlers": ["housekeeper_jobs", "housekeeper_errors", "errorfile"],
                    "level": self.LOG_LEVEL,
                }
            },
            "root": {
                "handlers": [],
                "level": self.LOG_LEVEL
            }
        }

        logging.config.dictConfig(self._initial_config)
        for logger_name in [name for name in self._initial_config["loggers"] if name not in ["augur.server"]]:
            coloredlogs.install(logger=logging.getLogger(logger_name), level=self.LOG_LEVEL, fmt=self.format_string)

        if self.QUIET:
            for logger in ["augur", "augur.housekeeper", "augur.server", "augur.cli"]:
                lg = logging.getLogger(logger)
                lg.disabled = True

        logger = logging.getLogger(__name__)
        logger.debug("Logging initialized")
        logger.debug("Logs will be written to: " + self.LOGS_DIRECTORY)

    def init_housekeeper_logging(self):
            queue = Queue()
            self._housekeeper_job_config = {
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

            logger.debug("Initializing housekeeper listener")
            stop_event = Event()
            self.lp = Process(target=listener_process, name='listener',
                 args=(queue, stop_event, self._initial_config))
            self.lp.start()
            sleep(2) # just to let it fully start up
            logger.debug("Houseekeeper listener started")

            def stop_listener(listener_process):
                listener_process.terminate()
            atexit.register(stop_listener, self.lp)

            self.stop_event = stop_event

    def get_housekeeper_job_config(self):
        return self._housekeeper_job_config

    def _get_settings(self):
        return {
            "log_level": self.LOG_LEVEL,
            "quiet": self.QUIET,
            "verbose": self.VERBOSE,
            "debug": self.DEBUG,
            "format_string": self.format_string
        }

    def set_gunicorn_log_options(self):
        gunicorn_log_file = self.LOGS_DIRECTORY + "gunicorn.log"
        options = {
            "errorlog": gunicorn_log_file,
            "accesslog": gunicorn_log_file,
            "loglevel": self.LOG_LEVEL,
            "capture_output": False
        }
        return options

def listener_process(q, stop_event, config):
    """
    This could be done in the main process, but is just done in a separate
    process for illustrative purposes.

    This initialises logging according to the specified configuration,
    starts the listener and waits for the main process to signal completion
    via the event. The listener is then stopped, and the process exits.
    """
    logging.config.dictConfig(config)
    listener = logging.handlers.QueueListener(q, MyHandler())
    listener.start()
    try:
        stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()

class MyHandler:
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
