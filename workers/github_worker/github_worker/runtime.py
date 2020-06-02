from flask import Flask, jsonify, request, Response
import click, os, json, requests, logging
from github_worker.worker import GitHubWorker
from workers.util import read_config, create_server

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51236, help='Port')
def main(augur_url, host, port):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    app = Flask(__name__)

    #load credentials
    worker_info = read_config('Workers', 'github_worker', None, None)
    worker_port = worker_info['port'] if 'port' in worker_info else port

    while True: # for multiple instances of workers
        try: # trying each port for an already-alive worker until a free port is found
            print("New github worker trying port: {}\n".format(worker_port))
            r = requests.get("http://{}:{}/AUGWOP/heartbeat".format(host, worker_port)).json()
            if 'status' in r:
                if r['status'] == 'alive':
                    worker_port += 1
        except:
            break

    # Format the port the worker is running on to the name of the 
    #   log file so we can tell multiple instances apart
    logging.basicConfig(filename='worker_{}.log'.format(worker_port), filemode='w', level=logging.INFO)

    config = { 
            'id': 'com.augurlabs.core.github_worker.{}'.format(worker_port),
            'location': 'http://{}:{}'.format(read_config('Server', 'host', 'AUGUR_HOST', 'localhost'),worker_port),
            'gh_api_key': read_config('Database', 'key', 'AUGUR_GITHUB_API_KEY', 'key')
        }

    #create instance of the worker
    app.worker = GitHubWorker(config) # declares the worker that will be running on this server with specified config
    create_server(app, None)
    logging.info("Starting Flask App with pid: " + str(os.getpid()) + "...")

    app.run(debug=app.debug, host=host, port=worker_port)
    if app.worker._child is not None:
        app.worker._child.terminate()
    try:
        requests.post('http://{}:{}/api/unstable/workers/remove'.format(broker_host, broker_port), json={"id": config['id']})
    except:
        pass
    
    logging.info("Killing Flask App: " + str(os.getpid()))
    os.kill(os.getpid(), 9)
