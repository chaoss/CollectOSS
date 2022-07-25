import logging

import gunicorn.app.base
from gunicorn.arbiter import Arbiter

from augur.api.server import Server
from augur.application.logs import AugurLogger


logger = AugurLogger("gunicorn", base_log_dir="/Users/andrew_brain/Augur/augur/logs/").get_logger()

class AugurGunicornApp(gunicorn.app.base.BaseApplication):
    """
    Loads configurations, initializes Gunicorn, loads server
    """

    def __init__(self, options={}, augur_app=None):

        self.options = options
        self.augur_app = augur_app
        self.server = None
        logger.debug(f"Gunicorn will start {self.options['workers']} worker processes")
        super(AugurGunicornApp, self).__init__()

    def load_config(self):
        """
        Sets the values for configurations
        """
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def get_augur_app(self):
        """
        Returns the loaded server
        """
        self.load()
        return self.server.augur_app

    def load(self):
        """
        Returns the loaded server
        """
        if self.server is None:
            try:
                self.server = Server(augur_app=self.augur_app)
            except Exception as e:
                print(f"An error occured when Gunicorn tried to load the server: {e}")
        return self.server.app
