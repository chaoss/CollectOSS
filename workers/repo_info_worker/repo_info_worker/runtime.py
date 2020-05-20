from flask import Flask, jsonify, request, Response
import click, os, json, requests, logging
from repo_info_worker.worker import RepoInfoWorker
from workers.util import read_config, create_server

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51237, help='Port')
def main(augur_url, host, port):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    app = Flask(__name__)

    #load credentials
    broker_host = read_config("Server", "host", "AUGUR_HOST", "0.0.0.0")
    broker_port = read_config("Server", "port", "AUGUR_PORT", 5000)
    worker_info = read_config('Workers', 'repo_info_worker', None, None)

    worker_port = worker_info['port'] if 'port' in worker_info else port

    while True:
        try:
            r = requests.get("http://{}:{}/AUGWOP/heartbeat".format(broker_port, worker_port)).json()
            if 'status' in r:
                if r['status'] == 'alive':
                    worker_port += 1
        except:
            break

    logging.basicConfig(filename='worker_{}.log'.format(worker_port), filemode='w', level=logging.INFO)

    config = { 
            "id": "com.augurlabs.core.repo_info_worker.{}".format(worker_port),
            'location': 'http://{}:{}'.format(read_config('Server', 'host', 'AUGUR_HOST', 'localhost'),worker_port),
            'gh_api_key': read_config('Database', 'key', 'AUGUR_GITHUB_API_KEY', 'key')
        }

    #create instance of the worker
    app.gh_repo_info_worker = RepoInfoWorker(config) # declares the worker that will be running on this server with specified config

    create_server(app, None)
    logging.info("Starting Flask App with pid: " + str(os.getpid()) + "...")
    app.run(debug=app.debug, host=host, port=worker_port)
    if app.gh_repo_info_worker._child is not None:
        app.gh_repo_info_worker._child.terminate()
    try:
        requests.post('http://{}:{}/api/unstable/workers/remove'.format(server['host'],server['port']), json={"id": config['id']})
    except:
        pass

    logging.info("Killing Flask App: " + str(os.getpid()))
    os.kill(os.getpid(), 9)

