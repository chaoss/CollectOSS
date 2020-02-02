import json
import logging
import os
import subprocess
import sys

import click
import requests
from flask import Flask, Response, jsonify, request

from value_worker.worker import ValueWorker

from workers.standard_methods import read_config

logging.basicConfig(filename='worker.log', filemode='w', level=logging.INFO)


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
            app.value_worker.task = request.json
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
        return app.value_worker.config

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51239, help='Port')
@click.option('--scc-bin', default=f'{os.environ["HOME"]}/go/bin/scc', help='scc binary')
def main(augur_url, host, port, scc_bin):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """

    app = Flask(__name__)

    #load credentials
    credentials = read_config("Database", use_main_config=1)
    server = read_config("Server", use_main_config=1)
    worker_info = read_config("Workers", use_main_config=1)['value_worker']

    worker_port = worker_info['port'] if 'port' in worker_info else port
    scc_bin = worker_info['scc_bin'] if 'scc_bin' in worker_info else scc_bin

    # Check if scc is installed, if not quit
    try:
        subprocess.call([scc_bin, '--version'])
    except Exception as e:
        logging.error(f"Couldn't run {scc_bin}: {e}")
        sys.exit('Exiting')

    while True:
        try:
            r = requests.get(f'http://{server["host"]}:{worker_port}/AUGWOP/task')
            if r.status == 200:
                worker_port += 1
        except:
            break

    config = {
            'id': f'com.augurlabs.core.value_worker.{worker_port}',
            'broker_port': server['port'],
            'broker_host': server['host'],
            'location': f'http://{server["host"]}:{worker_port}',
            'zombie_id': 22,
            'host': credentials['host'],
            'key': credentials['key'],
            'password': credentials['password'],
            'port': credentials['port'],
            'user': credentials['user'],
            'database': credentials['database'],
            'table': 'repo_labor',
            'endpoint': 'scc',
            'display_name': 'Value Worker',
            'description': 'A worker that calculates value data.',
            'required': 1,
            'type': 'string',
            'scc_bin': scc_bin
        }

    # Create the worker that will be running on this server with specified config
    app.value_worker = ValueWorker(config)

    create_server(app, None)
    logging.info("Starting Flask App with pid: " + str(os.getpid()) + "...")


    app.run(debug=app.debug, host=server['host'], port=worker_port)
    if app.value_worker._child is not None:
        app.value_worker._child.terminate()
    try:
        requests.post(f'http://{server["host"]}:{server["port"]}/api/unstable/workers/remove', json={"id": config['id']})
    except:
        pass

    logging.info("Killing Flask App: " + str(os.getpid()))
    os.kill(os.getpid(), 9)

