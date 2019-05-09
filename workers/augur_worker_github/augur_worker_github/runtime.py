from flask import Flask, jsonify
import click

def create_server(app, gw):
    @app.route("/")
    def hello():
        return "Hello World!"

    @app.route("/AUGWOP/task")
    def augwop_task():
        return jsonify({
            "status": "IDLE",
            "tasks": [{
                "given": []
            }]
        })

    @app.route("/AUGWOP/config")
    def augwop_config():
        return "Hey!"

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default='51232', help='Port')
def main(augur_url, host, port):
    app = Flask(__name__)
    create_server(app, None)
    app.run(debug=app.debug, host=host, port=port)