from flask import Flask, jsonify, request
import click
from augur_worker_github.worker import GitHubWorker

def create_server(app, gw):
    """ Consists of AUGWOP endpoints for the broker to communicate to this worker
    Can post a new task to be added to the workers queue
    Can retrieve current status of the worker
    Can retrieve the workers config object
    """
    
    @app.route("/")
    def hello():
        return "Hello World!"

    @app.route("/AUGWOP/task", methods=['POST', 'GET'])
    def augwop_task():
        """ AUGWOP endpoint that gets hit to add a task to the workers queue
        """
        if request.method == 'POST': #will post a task to be added to the queue
            print(request.json)
            app.gh_worker._queue.put(request.json)
            return jsonify({"success": "sucess"})
        if request.method == 'GET': #will retrieve the current tasks/status of the worker
            return jsonify({
                "status": "IDLE",
                "tasks": [{
                    "given": []
                }],
                "test": gh_worker.tasks
            })

    @app.route("/AUGWOP/config")
    def augwop_config():
        """ Retrieve worker's config
        """
        return app.gh_worker.config

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51232, help='Port')
def main(augur_url, host, port):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    app = Flask(__name__)

    config = { 
            'database_connection_string': 'psql://localhost:5432/augur',
            "key": "2759b561575060cce0d87c0f8d7f72f53fe35e14",
            "display_name": "GitHub API Key",
            "description": "API Token for the GitHub API v3",
            "required": 1,
            "type": "string"
        }

    app.gh_worker = GitHubWorker(config) # declares the worker that will be running on this server with specified config
    
    create_server(app, None)
    app.run(debug=app.debug, host=host, port=port)
    

