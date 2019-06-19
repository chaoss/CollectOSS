from flask import Flask, jsonify, request
import click
from linux_badge_worker.worker import BadgeWorker
import os
import json

def create_server(app, gw):
    """ Consists of AUGWOP endpoints for the broker to communicate to this worker
    Can post a new task to be added to the workers queue
    Can retrieve current status of the worker
    Can retrieve the workers config object
    """
    
    @app.route("/AUGWOP/task", methods=['POST', 'GET'])
    def augwop_task():
        """ AUGWOP endpoint that gets hit to add a task to the workers queue or is used to get the heartbeat/status of worker
        """
        if request.method == 'POST': #will post a task to be added to the queue
            print(request.json)
            app.gh_worker.task = request.json
            #set task
            return jsonify({"success": "sucess"})
        if request.method == 'GET': #will retrieve the current tasks/status of the worker
            return jsonify({
                "status": gh_worker._queue if condition else condition_if_false,
                "tasks": [{
                    "given": list(gh_worker._queue)
                }]
            })

    @app.route("/AUGWOP/config")
    def augwop_config():
        """ Retrieve worker's config
        """
        return app.gh_worker.config

@click.command()
@click.option('--augur-url', default='http://localhost:5000/', help='Augur URL')
@click.option('--host', default='localhost', help='Host')
@click.option('--port', default=51235, help='Port')
def main(augur_url, host, port):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    app = Flask(__name__)

    #load credentials
    credentials = read_config("Database")

    config = { 
            "id": "com.augurlabs.core.badge_worker",
            "host": credentials["host"],
            "password": credentials["password"],
            "port": credentials["port"],
            "user": credentials["user"],
            "database": credentials["database"],
            "table": "repo_badging",
            "endpoint": "https://bestpractices.coreinfrastructure.org/projects.json",
            "display_name": "",
            "description": "",
            "required": 1,
            "type": "string"
        }
    
    #create instance of the worker
    app.gh_worker = BadgeWorker(config) # declares the worker that will be running on this server with specified config
    
    create_server(app, None)
    app.run(debug=app.debug, host=host, port=port)


def read_config(section, name=None, environment_variable=None, default=None, config_file='augur.config.json', no_config_file=0):
        """
        Read a variable in specified section of the config file, unless provided an environment variable

        :param section: location of given variable
        :param name: name of variable
        """

        __config_bad = False
        __config_file_path = os.path.abspath(os.getenv('AUGUR_CONFIG_FILE', config_file))
        __config_location = os.path.dirname(__config_file_path)
        __export_env = os.getenv('AUGUR_ENV_EXPORT', '0') == '1'
        __default_config = { 'Database': {"host": "nekocase.augurlabs.io"} }

        if os.getenv('AUGUR_ENV_ONLY', '0') != '1' and no_config_file == 0:
            try:
                __config_file = open(__config_file_path, 'r+')
            except:
                # logger.info('Couldn\'t open {}, attempting to create. If you have a augur.cfg, you can convert it to a json file using "make to-json"'.format(config_file))
                if not os.path.exists(__config_location):
                    os.makedirs(__config_location)
                __config_file = open(__config_file_path, 'w+')
                __config_bad = True


            # Options to export the loaded configuration as environment variables for Docker
           
            if __export_env:
                
                export_filename = os.getenv('AUGUR_ENV_EXPORT_FILE', 'augur.cfg.sh')
                __export_file = open(export_filename, 'w+')
                # logger.info('Exporting {} to environment variable export statements in {}'.format(config_file, export_filename))
                __export_file.write('#!/bin/bash\n')

            # Load the config file and return [section][name]
            try:
                config_text = __config_file.read()
                __config = json.loads(config_text)
                if name is not None:
                    return(__config[section][name])
                else:
                    return(__config[section])

            except json.decoder.JSONDecodeError as e:
                if not __config_bad:
                    __using_config_file = False
                    # logger.error('%s could not be parsed, using defaults. Fix that file, or delete it and run this again to regenerate it. Error: %s', __config_file_path, str(e))

                __config = __default_config
                return(__config[section][name])

