# from augur import ROOT_AUGUR_DIRECTORY
import multiprocessing
import logging
from pathlib import Path
from glob import glob

from augur.application.db.lib import get_value, get_section
from augur.application.db import dispose_database_engine

logger = logging.getLogger(__name__)


# ROOT_AUGUR_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# base_log_dir = ROOT_AUGUR_DIRECTORY + "/logs/"

# Path(base_log_dir).mkdir(exist_ok=True)

workers = multiprocessing.cpu_count() * 2 + 1
umask = 0o007
reload = True
reload_extra_files = glob(str(Path.cwd() / '**/*.j2'), recursive=True)

# set the log location for gunicorn    
logs_directory = get_value('Logging', 'logs_directory')
accesslog = f"{logs_directory}/gunicorn.log"
errorlog = f"{logs_directory}/gunicorn.log"

ssl_bool = get_value('Server', 'ssl')

if ssl_bool is True: 

    workers = int(get_value('Server', 'workers'))
    bind = '%s:%s' % (get_value("Server", "host"), get_value("Server", "port"))
    timeout = int(get_value('Server', 'timeout'))
    certfile = str(get_value('Server', 'ssl_cert_file'))
    keyfile = str(get_value('Server', 'ssl_key_file'))
    
else: 
    workers = int(get_value('Server', 'workers'))
    bind = '%s:%s' % (get_value("Server", "host"), get_value("Server", "port"))
    timeout = int(get_value('Server', 'timeout'))


def worker_exit(server, worker):
    print("Stopping gunicorn worker process")
    dispose_database_engine()

