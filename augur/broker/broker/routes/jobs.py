
from flask import request, jsonify

def create_routes(server):

    @server.app.route('{}/job'.format(server.API_VERSION), methods=['POST'])
    def job():
    	""" AUGWOP route that is hit when data needs to be added to the database
		Retrieves a json consisting of job specifications that the broker will use to assign a worker
    	"""
        job = request.json
        print(job['given'])
        server.broker.create_job(job)
        return jsonify({"job": job})
