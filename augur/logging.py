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
AUGUR_LOG_DIR = ROOT_AUGUR_DIRECTORY + "/logs/"
HOUSEKEEPER_LOG_DIR = AUGUR_LOG_DIR + "/housekeeper/"
WORKER_LOG_DIR = AUGUR_LOG_DIR + "/workers/"

Path(AUGUR_LOG_DIR).mkdir(exist_ok=True)
Path(HOUSEKEEPER_LOG_DIR).mkdir(exist_ok=True)
Path(WORKER_LOG_DIR).mkdir(exist_ok=True)

housekeeper_file_handler = FileHandler(HOUSEKEEPER_LOG_DIR + "all_jobs.log", mode="a")
housekeeper_file_handler.setFormatter(FORMATTER)

console_handler = StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(FORMATTER)

log_file_handler = FileHandler(AUGUR_LOG_DIR + "augur.log", mode="a")
log_file_handler.setLevel(LOG_LEVEL)
log_file_handler.setFormatter(FORMATTER)

gunicorn_log_file_handler = FileHandler(AUGUR_LOG_DIR + "gunicorn.log", mode="a")
gunicorn_log_file_handler.setLevel(LOG_LEVEL)
gunicorn_log_file_handler.setFormatter(FORMATTER)

def initialize_logging(augur_config):
    LOG_LEVEL = augur_config.get_value("Development", "log_level")
    VERBOSE = augur_config.get_value("Development", "verbose")
    QUIET = augur_config.get_value("Development", "quiet")

    if VERBOSE is True:
        FORMATTER = verbose_formatter
    else:
        FORMATTER = generic_formatter

    augur_logger = create_logger("augur", [log_file_handler,console_handler])
    cli_logger = create_logger("augur.cli", [console_handler])
    cli_logger.propagate = False

    if QUIET is True:
        augur_logger.disabled = True

def create_logger(name, handlers):
    logger = logging.getLogger(name)
    logger.handlers = []
    for handler in handlers:
        handler.setFormatter(FORMATTER)
        handler.setLevel(LOG_LEVEL)
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
    coloredlogs.install(logger=logger)
    return logger

def create_job_logger(model):
    job_log_file = HOUSEKEEPER_LOG_DIR + f"{model}_jobs.log"

    open(job_log_file, "w").close()
    job_handler = FileHandler(job_log_file)

    job_logger = create_logger(f"augur.housekeeper.{model}", [housekeeper_file_handler, job_handler, console_handler])
    job_logger.propagate = False

    if QUIET is True:
        job_logger.disabled = True

    return job_logger

def reset_logfiles():
    open(AUGUR_LOG_DIR + "augur.log", "w").close()
    open(AUGUR_LOG_DIR + "gunicorn.log", "w").close()
    open(HOUSEKEEPER_LOG_DIR + "all_jobs.log", "w").close()

def set_gunicorn_log_options():
    gunicorn_log_file = AUGUR_LOG_DIR + "gunicorn.log"
    options = {
        'errorlog': gunicorn_log_file,
        'accesslog': gunicorn_log_file,
        'loglevel': LOG_LEVEL,
        'capture_output': True if not QUIET else False
    }
    return options