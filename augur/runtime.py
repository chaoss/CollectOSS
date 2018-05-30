import multiprocessing as mp
import sched
import time
import gunicorn.app.base
import augur
from augur.util import logger
from gunicorn.six import iteritems

class AugurGunicornApp(gunicorn.app.base.BaseApplication):

    def __init__(self, options=None):
        self.options = options or {}
        super(AugurGunicornApp, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        server = augur.Server()
        return server.app

def run():
    mp.set_start_method('forkserver')
    app = augur.Application()
    logger.info('Initalizing background tasks...')
    app.init_all()
    app.schedule_updates()
    logger.info('Starting gunicorn workers...')
    host = app.read_config('Server', 'host', 'AUGUR_HOST', '0.0.0.0')
    port = app.read_config('Server', 'port', 'AUGUR_PORT', '5000')
    workers = int(app.read_config('Server', 'workers', 'AUGUR_WORKERS', mp.cpu_count()))
    options = {
        'bind': '%s:%s' % (host, port),
        'workers': workers,
        'accesslog': '-'
    }
    app.finalize_config()
    AugurGunicornApp(options).run()


if __name__ == '__main__':
    run()
