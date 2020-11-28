#SPDX-License-Identifier: MIT
from flask import Flask, jsonify, request, Response
import click, os, json, requests, logging
from workers.library_experience_worker.library_experience_worker import LibraryExperienceWorker # update corresponding name(s)
from workers.util import create_server, WorkerGunicornApplication

def main():
    """
    Creates the Flask app and data collection worker, then starts the Gunicorn server
    """
    # worker = LibraryExperienceWorker(config={"offline_mode": True}) # update corresponding name
    app = Flask(__name__)
    app.worker = LibraryExperienceWorker() # update corresponding name

    create_server(app)
    WorkerGunicornApplication(app).run()

    if app.worker._child is not None:
        app.worker._child.terminate()
    try:
        requests.post('http://{}:{}/api/unstable/workers/remove'.format(broker_host, broker_port), json={"id": config['id']})
    except:
        pass

    os.kill(os.getpid(), 9)
