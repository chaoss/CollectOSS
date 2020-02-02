from flask import Flask, jsonify, request, Response
import click, logging, requests, json
from metric_status_worker.worker import MetricStatusWorker
import os
import json
from workers.standard_methods import read_config

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
        if request.method == 'POST': #will post a task to be added to the queue
            logging.info("Sending to work on task: {}".format(str(request.json)))
            app.metric_status_worker.task = request.json

            #set task
            return Response(response=request.json,
                        status=200,
                        mimetype="application/json")
        if request.method == 'GET': #will retrieve the current tasks/status of the worker
            return jsonify({
                "status": "success"
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
        return app.metric_status_worker.config

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51263, help='Port')
def main(augur_url, host, port):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    app = Flask(__name__)
    #load credentials
    credentials = read_config("Database", use_main_config=1)
    server = read_config("Server", use_main_config=1)
    worker_info = read_config("Workers", use_main_config=1)['metric_status_worker']
    worker_port = worker_info['port'] if 'port' in worker_info else port

    while True:
        try:
            r = requests.get("http://{}:{}/AUGWOP/heartbeat".format(server['host'],worker_port)).json()
            if 'status' in r:
                if r['status'] == 'alive':
                    worker_port += 1
        except:
            break

    logging.basicConfig(filename='worker_{}.log'.format(worker_port), filemode='w', level=logging.INFO)

    config = { 
            "id": "com.augurlabs.core.metric_status_worker",
            "location": "http://{}:{}".format(server['host'],worker_port),
            "broker_host": server['host'],
            "broker_port": server['port'],
            "host": credentials["host"],
            "key": read_config("Database", "key", "AUGUR_GITHUB_API_KEY", "key"),
            "password": credentials["password"],
            "port": credentials["port"],
            "user": credentials["user"],
            "database": credentials["database"],
            "table": "chaoss_metric_status",
            "endpoint": "http://{}:{}/api/unstable/metrics/status".format(server['host'],server['port']),
            "type": "string"
        }

    #create instance of the worker
    app.metric_status_worker = MetricStatusWorker(config) # declares the worker that will be running on this server with specified config
    
    create_server(app, None)
    logging.info("Starting Flask App with pid: " + str(os.getpid()) + "...")
    app.run(debug=app.debug, host=host, port=port)
    if app.metric_status_worker._child is not None:
        app.metric_status_worker._child.terminate()
    try:
        requests.post('http://{}:{}/api/unstable/workers/remove'.format(server['host'],server['port']), json={"id": config['id']})
    except:
        pass
    logging.info("Killing Flask App: " + str(os.getpid()))
    os.kill(os.getpid(), 9)    

