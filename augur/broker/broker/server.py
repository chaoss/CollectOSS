import atexit
import sys
import random
import json

from broker.routes import create_all_routes
from broker.broker import Broker

from flask import Flask, jsonify, Response, redirect, url_for, request
from flask_cors import CORS

import logging
logging.basicConfig(filename='logs/server.log')
logger = logging.getLogger(name="broker_server_logger")

class Server():
    """ Initialization of the server/flask app that the broker is running on
    """
    def __init__(self):
        # create the Flask app
        self.app = Flask(__name__, instance_relative_config=True)
        app = self.app

        #enable CORS
        cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

        self.broker = Broker() #declare the app's broker

        self.API_VERSION = '/api' #string to precede any AUGWOP endpoints

        # create routes
        logger.info("Creating all routes")
        create_all_routes(self)
        

broker_server = Server() #declares our instance of the Server class the broker runs on
app = broker_server.app

if __name__ == "__main__":
    app.run()