from flask import Flask, jsonify, request, Response
import click, os, json, requests, logging
from repo_info_worker.worker import RepoInfoWorker
from workers.util import read_config, create_server, WorkerGunicornApplication

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51237, help='Port')
def main(augur_url, host, port):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    worker_type = "repo_info_worker"
    worker_info = read_config('Workers', 'repo_info_worker', None, None)

    worker_port = worker_info['port'] if 'port' in worker_info else port
    while True:
        try:
            r = requests.get("http://{}:{}/AUGWOP/heartbeat".format(host, worker_port)).json()
            if 'status' in r:
                if r['status'] == 'alive':
                    worker_port += 1
        except:
            break

    config = { 
            "worker_type": worker_type,
            "worker_port": worker_port,
            "server_logfile": "{}_{}_server.log".format(worker_type, worker_port),
            "collection_logfile": "{}_{}_collection.log".format(worker_type, worker_port),
            "log_level": "INFO",
            "verbose": False,
            "id": "com.augurlabs.core.{}.{}".format(worker_port, worker_type),
            'location': 'http://{}:{}'.format(read_config('Server', 'host', 'AUGUR_HOST', 'localhost'), worker_port),
            'gh_api_key': read_config('Database', 'key', 'AUGUR_GITHUB_API_KEY', 'key')
        }

    app = Flask(f"{worker_type}.{worker_port}")
    app.worker = RepoInfoWorker(config)

    create_server(app)
    WorkerGunicornApplication(app, worker_port).run()

    if app.worker._child is not None:
        app.worker._child.terminate()
    try:
        requests.post('http://{}:{}/api/unstable/workers/remove'.format(server['host'],server['port']), json={"id": config['id']})
    except:
        pass

    os.kill(os.getpid(), 9)
