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
            logging.info("Sending to work on task: {}\n".format(str(request.json)))
            app.insight_worker.task = request.json
            
            #set task
            return jsonify({"success": "sucess"})

        if request.method == 'GET': #will retrieve the current tasks/status of the worker
            return jsonify({
                "status": app.insight_worker._queue,
                "tasks": [{
                    "given": list(app.insight_worker._queue)
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
    broker_host = read_config("Server", "host", "AUGUR_HOST", "0.0.0.0")
    broker_port = read_config("Server", "port", "AUGUR_PORT", 5000)
    database_host = read_config('Database', 'host', 'AUGUR_DB_HOST', 'host')
    worker_info = read_config('Workers', 'insight_worker', None, {})

    worker_port = worker_info['port'] if 'port' in worker_info else port

    while True:
        try:
            r = requests.get("http://{}:{}/AUGWOP/heartbeat".format(host, worker_port)).json()
            if 'status' in r:
                if r['status'] == 'alive':
                    worker_port += 1
        except:
            break

    logging.basicConfig(filename='worker_{}.log'.format(worker_port), filemode='w', level=logging.INFO)

    config = { 
            "id": "com.augurlabs.core.insight_worker.{}".format(worker_port),
            "broker_port": broker_port,
            "broker_host": broker_host,
            "location": "http://{}:{}".format(read_config('Server', 'host', 'AUGUR_HOST', 'localhost'),worker_port),
            "host": database_host,
            "key": read_config("Database", "key", "AUGUR_GITHUB_API_KEY", "key"),
            "password": read_config('Database', 'password', 'AUGUR_DB_PASSWORD', 'password'),
            "port": read_config('Database', 'port', 'AUGUR_DB_PORT', 'port'),
            "user": read_config('Database', 'user', 'AUGUR_DB_USER', 'user'),
            "database": read_config('Database', 'name', 'AUGUR_DB_NAME', 'database'),
            "endpoint": "https://bestpractices.coreinfrastructure.org/projects.json",
            "anomaly_days": worker_info['anomaly_days'] if 'anomaly_days' in worker_info else 2,
            "training_days": worker_info['training_days'] if 'training_days' in worker_info else 365,
            "confidence_interval": worker_info['confidence_interval'] if 'confidence_interval' in worker_info else .95,
            "contamination": worker_info['contamination'] if 'contamination' in worker_info else 0.041,
            'metrics': worker_info['metrics'] if 'metrics' in worker_info else {"issues-new": "issues", 
                "code-changes": "commit_count", "code-changes-lines": "added", 
                "reviews": "pull_requests", "contributors-new": "new_contributors"}
        }

    #create instance of the worker
    app.insight_worker = InsightWorker(config) # declares the worker that will be running on this server with specified config
    
    create_server(app, None)
    print("Starting Flask App on host {} with port {} with pid: ".format(broker_host, worker_port) + str(os.getpid()) + "...")
    app.run(debug=app.debug, host=host, port=worker_port)
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
    
