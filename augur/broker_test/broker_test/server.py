
import atexit
import sys
import random
import json
# import ipdb

from broker_test.routes import create_all_routes
from broker_test.broker import Broker

from flask import Flask, jsonify, Response, redirect, url_for, request
from flask_cors import CORS

import logging
logging.basicConfig(filename='logs/server.log')
logger = logging.getLogger(name="chambers")

class Server():
    def __init__(self):
        # create the Flask app
        self.app = Flask(__name__, instance_relative_config=True)
        app = self.app

        #enable CORS
        cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

        # load config file

        self.broker = Broker()

        self.API_VERSION = '/api'

        # create routes
        logger.info("Creating all routes")
        create_all_routes(self)
        
        @app.route('/')
        def default():
            return redirect(url_for('ping'))

        @app.route('{}/ping'.format(self.API_VERSION), methods=['GET'])
        def ping():
            return jsonify({"status": "It's alive!"})

broker_server = Server()
app = broker_server.app

if __name__ == "__main__":
    app.run()