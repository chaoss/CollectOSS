# from augur import ROOT_AUGUR_DIRECTORY
import multiprocessing
import logging
import os
from pathlib import Path
import shutil

from augur.application.config import ReadAugurConfig
from augur.application.db.session import DatabaseSession

augur_config = ReadAugurConfig()

# ROOT_AUGUR_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# base_log_dir = ROOT_AUGUR_DIRECTORY + "/logs/"

# Path(base_log_dir).mkdir(exist_ok=True)



workers = multiprocessing.cpu_count() * 2 + 1
umask = 0o007
reload = True
#logging
accesslog = "augur/logs/gunicorn.log"
errorlog = "augur/logs/gunicorn.log"

ssl_bool = augur_config.get_value('Server', 'ssl')

if ssl_bool is True: 

    workers = int(augur_config.get_value('Server', 'workers'))
    bind = '%s:%s' % (augur_config.get_value("Server", "host"), augur_config.get_value("Server", "port"))
    timeout = int(augur_config.get_value('Server', 'timeout'))
    certfile = str(augur_config.get_value('Server', 'ssl_cert_file'))
    keyfile = str(augur_config.get_value('Server', 'ssl_key_file'))
    
else: 
    workers = int(augur_config.get_value('Server', 'workers'))
    bind = '%s:%s' % (augur_config.get_value("Server", "host"), augur_config.get_value("Server", "port"))
    timeout = int(augur_config.get_value('Server', 'timeout'))
