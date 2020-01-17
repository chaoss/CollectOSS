import json
import logging
import os
import click
import requests
from flask import Flask, Response, jsonify, request
from pull_request_worker.worker import GHPullRequestWorker

def create_server(app, gw):
    """ Consists of AUGWOP endpoints for the broker to communicate to this worker
    Can post a new task to be added to the workers queue
    Can retrieve current status of the worker
    Can retrieve the workers config object
    """

    @app.route("/AUGWOP/task", methods=['POST', 'GET'])
    def augwop_task():
        """ AUGWOP endpoint that gets hit to add a task to the workers queue or is used to get the heartbeat/status of worker
        """
        # POST a task to be added to the queue
        if request.method == 'POST':
            logging.info("Sending to work on task: {}".format(str(request.json)))
            app.gh_pr_worker.task = request.json
            return Response(response=request.json,
                        status=200,
                        mimetype="application/json")
        if request.method == 'GET': #will retrieve the current tasks/status of the worker
            return jsonify({
                "status": "not implemented"
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
        return app.gh_pr_worker.config

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51239, help='Port')
def main(augur_url, host, port):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    app = Flask(__name__)

    #load credentials
    credentials = read_config("Database", use_main_config=1)
    server = read_config("Server", use_main_config=1)
    worker_info = read_config("Workers", use_main_config=1)['pull_request_worker']

    worker_port = worker_info['port'] if 'port' in worker_info else port

    while True:
        try:
            print("Trying port: {}\n".format(worker_port))
            r = requests.get("http://{}:{}/AUGWOP/heartbeat".format(server['host'],worker_port)).json()
            if 'status' in r:
                if r['status'] == 'alive':
                    worker_port += 1
        except:
            break

    logging.basicConfig(filename='worker_{}.log'.format(worker_port), filemode='w', level=logging.INFO)

    config = {
            "id": "com.augurlabs.core.pull_request_worker.{}".format(worker_port),
            "broker_port": server['port'],
            "broker_host": server['host'],
            "location": "http://{}:{}".format(server['host'],worker_port),
            "zombie_id": 22,
            "host": credentials["host"],
            "key": credentials["key"],
            "password": credentials["password"],
            "port": credentials["port"],
            "user": credentials["user"],
            "database": credentials["database"],
            "table": "pull_requests",
            "endpoint": "api.github.com",
            "display_name": "Pull Request Worker",
            "description": "A GitHub worker to fetch PR data",
            "required": 1,
            "type": "string"
        }

    #create instance of the worker

    app.gh_pr_worker = GHPullRequestWorker(config) # declares the worker that will be running on this server with specified config

    create_server(app, None)
    logging.info("Starting Flask App with pid: " + str(os.getpid()) + "...")

    app.run(debug=app.debug, host=server['host'], port=worker_port)
    if app.gh_pr_worker._child is not None:
        app.gh_pr_worker._child.terminate()
    try:
        requests.post('http://{}:{}/api/unstable/workers/remove'.format(server['host'],server['port']), json={"id": config['id']})
    except:
        pass

    logging.info("Killing Flask App: " + str(os.getpid()))
    os.kill(os.getpid(), 9)



def read_config(section, name=None, environment_variable=None, default=None, config_file='augur.config.json', no_config_file=0, use_main_config=0):
    """
    Read a variable in specified section of the config file, unless provided an environment variable

    :param section: location of given variable
    :param name: name of variable
    """


    __config_bad = False
    if use_main_config == 0:
        __config_file_path = os.path.abspath(os.getenv('AUGUR_CONFIG_FILE', config_file))
    else:
        __config_file_path = os.path.abspath(os.path.dirname(os.path.dirname(os.getcwd())) + '/augur.config.json')

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
