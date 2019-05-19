from flask import Flask, jsonify, request
import click

def create_server(app, gw):
    tasks = []
    @app.route("/")
    def hello():
        return "Hello World!"

    @app.route("/AUGWOP/task", methods=['POST', 'GET'])
    def augwop_task():
        if request.method == 'POST':
            print(request.json)
            tasks.append(request.json)
            return jsonify({"success": "sucess"})
        if request.method == 'GET':
            return jsonify({
                "status": "IDLE",
                "tasks": [{
                    "given": []
                }],
                "test": tasks
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
    create_server(app, None)
    app.run(debug=app.debug, host=host, port=port)