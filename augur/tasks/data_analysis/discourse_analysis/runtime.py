from flask import Flask, jsonify, request, Response
import click, os, json, requests, logging
from workers.discourse_analysis_worker.discourse_analysis_worker import DiscourseAnalysisWorker
from workers.util import create_server, WorkerGunicornApplication


def main():
    """
    Creates the Flask app and data collection worker, then starts the Gunicorn server
    """
    app = Flask(__name__)
    app.worker = DiscourseAnalysisWorker()

    create_server(app)
    WorkerGunicornApplication(app).run()

    if app.worker._child is not None:
        app.worker._child.terminate()
    try:
        requests.post('http://{}:{}/api/unstable/workers/remove'.format(broker_host, broker_port), json={"id": config['id']})
    except:
        pass

    os.kill(os.getpid(), 9)
main()    
