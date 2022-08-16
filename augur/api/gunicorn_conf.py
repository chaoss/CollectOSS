# from augur import ROOT_AUGUR_DIRECTORY
import multiprocessing
import logging
import os
from pathlib import Path
import shutil

from augur.application.db.session import DatabaseSession

logger = logging.getLogger(__name__)
with DatabaseSession(logger) as session:
        
    # ROOT_AUGUR_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    # base_log_dir = ROOT_AUGUR_DIRECTORY + "/logs/"

    # Path(base_log_dir).mkdir(exist_ok=True)

    workers = multiprocessing.cpu_count() * 2 + 1
    umask = 0o007
    reload = True

    # set the log location for gunicorn    
    logs_directory = session.config.get_value('Logging', 'logs_directory')
    accesslog = f"{logs_directory}/gunicorn.log"
    errorlog = f"{logs_directory}/gunicorn.log"

    ssl_bool = session.config.get_value('Server', 'ssl')

    if ssl_bool is True: 

        workers = int(session.config.get_value('Server', 'workers'))
        bind = '%s:%s' % (session.config.get_value("Server", "host"), session.config.get_value("Server", "port"))
        timeout = int(session.config.get_value('Server', 'timeout'))
        certfile = str(session.config.get_value('Server', 'ssl_cert_file'))
        keyfile = str(session.config.get_value('Server', 'ssl_key_file'))
        
    else: 
        workers = int(session.config.get_value('Server', 'workers'))
        bind = '%s:%s' % (session.config.get_value("Server", "host"), session.config.get_value("Server", "port"))
        timeout = int(session.config.get_value('Server', 'timeout'))
