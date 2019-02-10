import click
import os
import sys
from augur.runtime import pass_application
from augur.util import logger
from augur.server import Server
import gunicorn.app.base
from gunicorn.six import iteritems
from gunicorn.arbiter import Arbiter
import multiprocessing as mp
import sched
import os
import time
import sys
import atexit
import click




class AugurGunicornApp(gunicorn.app.base.BaseApplication):
    """
    Loads configurations, initializes Gunicorn, loads server
    """

    def __init__(self, options=None):
        self.options = options or {}
        super(AugurGunicornApp, self).__init__()
        # self.cfg.pre_request.set(pre_request)

    def load_config(self):
        """
        Sets the values for configurations
        """
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """
        Returns the loaded server
        """
        server = Server()
        return server.app



@click.command('run', short_help='Run the Augur server')
@pass_application
def cli(app):
    mp.set_start_method('forkserver')
    logger.info('Loading...')
    # app.init_all()
    app.finalize_config()
    app.schedule_updates()
    master = None

    @atexit.register
    def exit():
        if master is not None:
            master.halt()
        app.shutdown_updates()
        # Prevent multiprocessing's atexit from conflicting with gunicorn
        os._exit(0)


    host = app.read_config('Server', 'host', 'AUGUR_HOST', '0.0.0.0')
    port = app.read_config('Server', 'port', 'AUGUR_PORT', '5000')
    workers = int(app.read_config('Server', 'workers', 'AUGUR_WORKERS', mp.cpu_count()))
    options = {
        'bind': '%s:%s' % (host, port),
        'workers': workers,
        'accesslog': '-',
        'access_log_format': '%(h)s - %(t)s - %(r)s',
    }
    logger.info('Starting server...')
    master = Arbiter(AugurGunicornApp(options)).run()

