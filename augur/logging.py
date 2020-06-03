import logging
from logging import FileHandler, StreamHandler, Formatter
import os
from pathlib import Path
import coloredlogs

verbose_formatter = Formatter(fmt='%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s')
generic_formatter = Formatter(fmt='%(asctime)s [%(process)d] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

FORMATTER = generic_formatter
LOG_LEVEL = "INFO"
VERBOSE = False
QUIET = False

ROOT_AUGUR_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

Path(ROOT_AUGUR_DIRECTORY + "/logs/").mkdir(exist_ok=True)
Path(ROOT_AUGUR_DIRECTORY + "/logs/housekeeper/").mkdir(exist_ok=True)

housekeeper_log_file_handler = FileHandler(ROOT_AUGUR_DIRECTORY + "/logs/housekeeper/housekeeper.log", mode="a")
housekeeper_log_file_handler.setFormatter(FORMATTER)

console_handler = StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(FORMATTER)

log_file_handler = FileHandler(ROOT_AUGUR_DIRECTORY + "/logs/augur.log", mode="a")
log_file_handler.setLevel(LOG_LEVEL)
log_file_handler.setFormatter(FORMATTER)

def initialize_logging(logging_config, jobs):
    LOG_LEVEL = logging_config["log_level"]
    VERBOSE = True if logging_config["verbose"] else False
    QUIET = True if logging_config["quiet"] else False

    if VERBOSE is True:
        FORMATTER = verbose_formatter
    else:
        FORMATTER = generic_formatter

    housekeeper_log_file_handler.setFormatter(FORMATTER)

    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(FORMATTER)

    log_file_handler.setLevel(LOG_LEVEL)
    log_file_handler.setFormatter(FORMATTER)

    augur_logger = logging.getLogger('augur')
    augur_logger.handlers = []
    augur_logger.addHandler(log_file_handler)
    augur_logger.addHandler(console_handler)
    augur_logger.setLevel(LOG_LEVEL)
    coloredlogs.install(logger=augur_logger)

    cli_logger = logging.getLogger('augur.cli')
    cli_logger.handlers = []
    cli_logger.addHandler(console_handler)
    cli_logger.setLevel(LOG_LEVEL)
    cli_logger.propagate = False
    coloredlogs.install(logger=cli_logger)

    if QUIET is True:
        augur_logger.disabled = True

def create_job_logger(model):
    open(f"logs/housekeeper/{model}.log", "w").close()
    job_handler = FileHandler(f"logs/housekeeper/{model}.log")
    job_handler.setLevel(LOG_LEVEL)
    job_handler.setFormatter(FORMATTER)

    job_logger = logging.getLogger(f"augur.housekeeper.{model}")
    job_logger.handlers = []
    job_logger.addHandler(housekeeper_log_file_handler)
    job_logger.addHandler(job_handler)
    job_logger.addHandler(console_handler)
    job_logger.setLevel(LOG_LEVEL)
    coloredlogs.install(logger=job_logger)

    return job_logger

def reset_logfiles():
    open("logs/augur.log", "w").close()
    open("logs/gunicorn.log", "w").close()
    open("logs/housekeeper/housekeeper.log", "w").close()
