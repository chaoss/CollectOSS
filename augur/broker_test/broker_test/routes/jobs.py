
from flask import request, jsonify

def create_routes(server):

    @server.app.route('{}/job'.format(server.API_VERSION), methods=['POST'])
    def job():
        pass
        # task = request.json
        # print(task['task'])
        # return jsonify({"task": task})
