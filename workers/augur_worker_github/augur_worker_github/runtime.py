from flask import Flask, jsonify, request
import click
from augur_worker_github.worker import GitHubWorker

def create_server(app, gw):
    
    @app.route("/")
    def hello():
        return "Hello World!"

    @app.route("/AUGWOP/task", methods=['POST', 'GET'])
    def augwop_task():
        if request.method == 'POST':
            print(request.json)
            app.gh_worker._queue.put(request.json)
            return jsonify({"success": "sucess"})
        if request.method == 'GET':
            return jsonify({
                "status": "IDLE",
                "tasks": [{
                    "given": []
                }],
                "test": gh_worker.tasks
            })

    @app.route("/AUGWOP/config")
    def augwop_config():
        return "Hey!"

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51232, help='Port')
def main(augur_url, host, port):
    app = Flask(__name__)

    config = {
            'database_connection_string': 'psql://localhost:5432/augur',
            "key": "2759b561575060cce0d87c0f8d7f72f53fe35e14",
            "display_name": "GitHub API Key",
            "description": "API Token for the GitHub API v3",
            "required": 1,
            "type": "string"
        }
    app.gh_worker = GitHubWorker(config)
    
    create_server(app, None)
    app.run(debug=app.debug, host=host, port=port)
    

