from flask import Flask, jsonify, request, Response
import click, os, json, requests, logging
from workers.gitlab_merge_request_worker.gitlab_merge_request_worker import GitlabMergeRequestWorker
from workers.util import WorkerGunicornApplication, create_server


def main():
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    app = Flask(__name__)
    app.worker = GitlabMergeRequestWorker() # declares the worker that will be running on this server with specified config

    create_server(app, None)
    WorkerGunicornApplication(app).run()

    if app.worker._child is not None:
        app.worker._child.terminate()
        
    try:
        requests.post('http://{}:{}/api/unstable/workers/remove'.format(broker_host, broker_port), json={"id": config['id']})
    except:
        pass

    logging.info("Killing Flask App: " + str(os.getpid()))
    os.kill(os.getpid(), 9)
