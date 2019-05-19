
from flask import request, jsonify

def create_routes(server):

    @server.app.route('{}/workers'.format(server.API_VERSION), methods=['POST'])
    def worker():
        # responsible for interpreting HELLO messages
        worker = request.json
        server.broker.add_new_worker(worker)
        return jsonify({"status": "success"})