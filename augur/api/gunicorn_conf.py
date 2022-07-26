# from augur import ROOT_AUGUR_DIRECTORY
import multiprocessing
import logging

from augur.application.config import AugurConfig
from augur.tasks.util.task_session import TaskSession

logger = logging.getLogger(__name__)
session = TaskSession(logger)
augur_config = AugurConfig(session)


workers = multiprocessing.cpu_count() * 2 + 1
umask = 0o007
reload = True
#logging
accesslog = 'access.log'
errorlog = 'error.log'

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
