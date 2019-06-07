from flask import request, jsonify

def create_routes(server):

    @server.app.route('{}/workers'.format(server.API_VERSION), methods=['POST'])
    def worker():
        """ AUGWOP route responsible for interpreting HELLO messages 
            and telling the broker to add this worker to the set it maintains
        """
        worker = request.json
        server.broker.add_new_worker(worker)
        return jsonify({"status": "success"})

    @server.app.route('{}/completed_task'.format(server.API_VERSION), methods=['POST'])
    def sync_queue():

        job = request.json
        print("Message recieved that worker ", job['worker_id'], " completed task: ", job)
        server.broker.completed_job(job)