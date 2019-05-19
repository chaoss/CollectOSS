
from flask import request, jsonify

def create_routes(server):

    @server.app.route('{}/job'.format(server.API_VERSION), methods=['POST'])
    def job():
        job = request.json
        print(job['given'])
        server.broker.create_job(job)
        return jsonify({"job": job})
