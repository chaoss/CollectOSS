import logging
from pathlib import Path

def init_logging(logger = logging.Logger("jumpstart") , errlog_file = Path("logs/jumpstart.error"), stdout_file = Path("logs/jumpstart.log")) -> logging.Logger:
    errlog = logging.FileHandler(errlog_file, "w")
    stdout = logging.FileHandler(stdout_file, "w")

    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(process)d]->[%(threadName)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S %z")

    errlog.setLevel(logging.WARN)
    stdout.setLevel(logging.INFO)
    stdout.addFilter(lambda entry: entry.levelno < logging.WARN)
    errlog.formatter = stdout.formatter = formatter

    logger.addHandler(errlog)
    logger.addHandler(stdout)
    logger.setLevel(logging.INFO)
    
    global console
    console = logger
    
    return logger

if "console" not in globals():
    init_logging()
