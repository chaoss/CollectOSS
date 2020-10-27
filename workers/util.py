#SPDX-License-Identifier: MIT
import os, json, requests, logging
from flask import Flask, Response, jsonify, request
import gunicorn.app.base

def read_config(section, name=None, environment_variable=None, default=None, config_file_path='../../augur.config.json', no_config_file=0, use_main_config=0):
    """
    Read a variable in specified section of the config file, unless provided an environment variable

    :param section: location of given variable
    :param name: name of variable
    """
    config_file_path = os.getenv("AUGUR_CONFIG_FILE", config_file_path)
    _config_file_name = 'augur.config.json'
    _config_bad = False
    _already_exported = {}
    _runtime_location = 'runtime/'
    _default_config = {}
    _config_file = None

    try:
        _config_file = open(config_file_path, 'r+')
    except:
        print('Couldn\'t open {}'.format(_config_file_name))

    # Load the config file
    try:
        config_text = _config_file.read()
        _config = json.loads(config_text)
    except json.decoder.JSONDecodeError as e:
        if not _config_bad:
            _using_config_file = False
            print('{} could not be parsed, using defaults. Fix that file, or delete it and run this again to regenerate it. Error: {}'.format(config_file_path, str(e)))
        _config = _default_config

    value = None
    if environment_variable is not None:
        value = os.getenv(environment_variable)
    if value is None:
        try:
            if name is not None:
                value = _config[section][name]
            else:
                value = _config[section]
        except Exception as e:
            value = default
            if not section in _config:
                _config[section] = {}

    return value

def create_server(app, worker=None):
    """ Consists of AUGWOP endpoints for the broker to communicate to this worker
    Can post a new task to be added to the workers queue
    Can retrieve current status of the worker
    Can retrieve the workers config object
    """

    @app.route("/AUGWOP/task", methods=['POST', 'GET'])
    def augwop_task():
        """ AUGWOP endpoint that gets hit to add a task to the workers queue or is used to get the heartbeat/status of worker
        """
        if request.method == 'POST': #will post a task to be added to the queue
            app.worker.logger.info("Sending to work on task: {}".format(str(request.json)))
            app.worker.task = request.json
            return Response(response=request.json,
                        status=200,
                        mimetype="application/json")
        if request.method == 'GET': #will retrieve the current tasks/status of the worker
            return jsonify({
                "status": "ALIVE",
                "results_counter": app.worker.results_counter,
                "task": app.worker.task,
            })
        return Response(response=request.json,
                        status=200,
                        mimetype="application/json")

    @app.route("/AUGWOP/heartbeat", methods=['GET'])
    def heartbeat():
        if request.method == 'GET':
            return jsonify({
                "status": "alive"
            })

    @app.route("/AUGWOP/config")
    def augwop_config():
        """ Retrieve worker's config
        """
        return app.worker.config

class WorkerGunicornApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app):
        self.options = {
            'bind': '%s:%s' % (app.worker.config["host"], app.worker.config["port"]),
            'workers': 1,
            'errorlog': app.worker.config['server_logfile'],
            'accesslog': app.worker.config['server_logfile'],
            'loglevel': app.worker.config['log_level'],
            'capture_output': app.worker.config['capture_output']
        }

        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
