import atexit
import sys
import random
import json
import os

from housekeeper.routes import create_all_routes
from housekeeper.housekeeper import HouseKeeper

from flask import Flask, jsonify, Response, redirect, url_for, request
from flask_cors import CORS

import logging
logging.basicConfig(filename='logs/server.log')
logger = logging.getLogger(name="housekeeper_server_logger")

class Server():
    """ Initialization of the server/flask app that the broker is running on
    """
    def __init__(self):
        # create the Flask app
        self.app = Flask(__name__, instance_relative_config=True)
        app = self.app

        #enable CORS
        cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

        #load credentials
        credentials = self.read_config("Database")

        config = { 
                "connection_string": credentials["connection_string"],
                "host": credentials["host"],
                "password": credentials["password"],
                "port": credentials["port"],
                "user": credentials["user"],
                "database": credentials["database"],
                "table": "repo_badging",
                "endpoint": "https://bestpractices.coreinfrastructure.org/projects.json",
                "display_name": "",
                "description": "",
                "required": 1,
                "type": "string"
            }

        self.housekeeper = HouseKeeper(config) #declare the app's broker

        self.API_VERSION = '/api' #string to precede any AUGWOP endpoints

        # create routes
        logger.info("Creating all routes")
        create_all_routes(self)

    def read_config(self, section, name=None, environment_variable=None, default=None, config_file='augur.config.json', no_config_file=0):
        """
        Read a variable in specified section of the config file, unless provided an environment variable

        :param section: location of given variable
        :param name: name of variable
        """

        __config_bad = False
        __config_file_path = os.path.abspath(os.getenv('AUGUR_CONFIG_FILE', config_file))
        __config_location = os.path.dirname(__config_file_path)
        __export_env = os.getenv('AUGUR_ENV_EXPORT', '0') == '1'
        __default_config = { 'Database': {"host": "nekocase.augurlabs.io"} }

        if os.getenv('AUGUR_ENV_ONLY', '0') != '1' and no_config_file == 0:
            try:
                __config_file = open(__config_file_path, 'r+')
            except:
                # logger.info('Couldn\'t open {}, attempting to create. If you have a augur.cfg, you can convert it to a json file using "make to-json"'.format(config_file))
                if not os.path.exists(__config_location):
                    os.makedirs(__config_location)
                __config_file = open(__config_file_path, 'w+')
                __config_bad = True


            # Options to export the loaded configuration as environment variables for Docker
           
            if __export_env:
                
                export_filename = os.getenv('AUGUR_ENV_EXPORT_FILE', 'augur.cfg.sh')
                __export_file = open(export_filename, 'w+')
                # logger.info('Exporting {} to environment variable export statements in {}'.format(config_file, export_filename))
                __export_file.write('#!/bin/bash\n')

            # Load the config file and return [section][name]
            try:
                config_text = __config_file.read()
                __config = json.loads(config_text)
                if name is not None:
                    return(__config[section][name])
                else:
                    return(__config[section])

            except json.decoder.JSONDecodeError as e:
                if not __config_bad:
                    __using_config_file = False
                    # logger.error('%s could not be parsed, using defaults. Fix that file, or delete it and run this again to regenerate it. Error: %s', __config_file_path, str(e))

                __config = __default_config
                return(__config[section][name])



housekeeper_server = Server() #declares our instance of the Server class the broker runs on
app = broker_server.app

if __name__ == "__main__":
    app.run(host='localhost', port=5002)

