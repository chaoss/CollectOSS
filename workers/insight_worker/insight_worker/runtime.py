from flask import Flask, jsonify, request
from insight_worker.worker import InsightWorker
import click, os, json, logging, requests
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
            app.insight_worker.task = request.json
            
            #set task
            return jsonify({"success": "sucess"})

        if request.method == 'GET': #will retrieve the current tasks/status of the worker
            return jsonify({
                "status": insight_worker._queue if condition else condition_if_false,
                "tasks": [{
                    "given": list(insight_worker._queue)
                }]
            })

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
        return app.insight_worker.config

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51252, help='Port')
def main(augur_url, host, port):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    app = Flask(__name__)

    #load credentials
    credentials = read_config("Database", use_main_config=1)
    server = read_config("Server", use_main_config=1)
    worker_info = read_config("Workers", use_main_config=1)['insight_worker']
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
        "id": "com.augurlabs.core.insight_worker.{}".format(worker_port),
        "broker_port": server["port"],
        "broker_host": server["host"],
        "key": credentials["key"],
        "metrics": worker_info['metrics'] if 'metrics' in worker_info else {"issues-new": "issues", 
                    "code-changes": "commit_count", "code-changes-lines": "added", 
                    "reviews": "pull_requests", "contributors-new": "new_contributors"},
        "contamination": worker_info['contamination'] if 'contamination' in worker_info else 0.041,
        "training_days": worker_info['training_days'] if 'training_days' in worker_info else 365,
        "anomaly_days": worker_info['anomaly_days'] if 'anomaly_days' in worker_info else 90,
        "confidence_interval": worker_info['confidence_interval'] if 'confidence_interval' in worker_info else 95,
        "host": credentials["host"],
        "location": "http://{}:{}".format(server["host"],worker_port),
        "password": credentials["password"],
        "port": credentials["port"],
        "user": credentials["user"],
        "endpoint": "http://{}:{}/api/unstable/metrics/status".format(server["host"],server['port']),
        "database": credentials["database"],
        "type": "string"
    }

    #create instance of the worker
    app.insight_worker = InsightWorker(config) # declares the worker that will be running on this server with specified config
    
    create_server(app, None)
    host = server['host']
    print("Starting Flask App on host {} with port {} with pid: ".format(server['host'], worker_port) + str(os.getpid()) + "...")
    app.run(debug=app.debug, host=server['host'], port=worker_port)
    print("Killing Flask App: {} and telling broker that this worker is disconnected.".format(str(os.getpid())))
    try:
        logging.info("Sending disconnected message to broker... @ -> {} with info: {}\n".format('http://{}:{}/api/unstable/workers'.format(
            config['broker_host'], config['broker_port']), config))
        requests.post('http://{}:{}/api/unstable/workers/remove'.format(
            config['broker_host'], config['broker_port']), json=config) #hello message
    except Exception as e:
        logging.info("Ran into error: {}".format(e))
        logging.info("Broker's port is busy, worker will not be able to accept tasks, "
            "please restart Augur if you want this worker to attempt connection again.")
    
