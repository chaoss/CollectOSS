#SPDX-License-Identifier: MIT
"""
Runs Augur with Gunicorn when called
"""

import multiprocessing as mp
import sched
import os
import time
import atexit
import gunicorn.app.base
import augur
from augur.util import logger
from augur.server import Server
from gunicorn.six import iteritems
from gunicorn.arbiter import Arbiter



class AugurGunicornApp(gunicorn.app.base.BaseApplication):

    def __init__(self, options=None):
        self.options = options or {}
        super(AugurGunicornApp, self).__init__()
        # self.cfg.pre_request.set(pre_request)

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        server = Server()
        return server.app

def run():
    mp.set_start_method('forkserver')
    app = augur.Application()
    app.arg_parser.add_argument("-u", "--updater",
        action="store_true",
        help="Do not start the Gunicorn server, only run update threads.")
    args, unknown_args = app.arg_parser.parse_known_args()
    logger.info('Loading...')
    app.init_all()
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


    if not args.updater:
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
    else:
        logger.info('Running in update mode...')
        try:
            app.join_updates()
        except KeyboardInterrupt:
            exit()

if __name__ == '__main__':
    run()
