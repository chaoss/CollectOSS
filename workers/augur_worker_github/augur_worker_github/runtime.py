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
            #set task
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
@click.option('--port', default=51235, help='Port') # Change default port #? Was 51232
def main(augur_url, host, port):
    """ Declares singular worker and creates the server and flask app that it will be running on
    """
    app = Flask(__name__)

    # # Create DB Session
    # self.db = None
    # self.session = None
    # db_str = self.read_config('Database', 'connection_string', 'AUGUR_DATABASE', 'sqlite:///:memory:')
    # self.db = create_engine(db_str)
    # self.__Session = scoped_session(sessionmaker(bind=self.db))
    # self.session = self.__Session()
    # Base.query = self.__Session.query_property()

    # config = { 
    #         'database_connection_string': 'psql://localhost:5432/augur',
    #         "key": "2759b561575060cce0d87c0f8d7f72f53fe35e14",
    #         "display_name": "GitHub API Key",
    #         "description": "API Token for the GitHub API v3",
    #         "required": 1,
    #         "type": "string"
    #     }

    config = { 
            "connection_string": "postgresql://localhost:5432/augur",
            "key": "2759b561575060cce0d87c0f8d7f72f53fe35e14",
            "host": "nekocase.augurlabs.io",
            "password": "avengers22",
            "port": "5433",
            "user": "augur",
            "database": "augur",
            "table": "contributors",
            "endpoint": "https://bestpractices.coreinfrastructure.org/projects.json",
            "display_name": "",
            "description": "",
            "required": 1,
            "type": "string"
        }

    app.gh_worker = GitHubWorker(config) # declares the worker that will be running on this server with specified config

    create_server(app, None)
    app.run(debug=app.debug, host=host, port=port)

def read_config(self, section, name, environment_variable=None, default=None):
        """
        Read a variable in specified section of the config file, unless provided an environment variable

        :param section: location of given variable
        :param name: name of variable
        """
        value = None
        if environment_variable is not None:
            value = os.getenv(environment_variable)
        if value is None:
            try:
                value =  self.__config[section][name]
            except Exception as e:
                value = default
                if not section in self.__config:
                    self.__config[section] = {}
                if self.__using_config_file:
                    self.__config_bad = True
                    self.__config[section][name] = default
        if (environment_variable is not None
                and value is not None
                and self.__export_env
                and not hasattr(self.__already_exported, environment_variable)):
            self.__export_file.write('export ' + environment_variable + '="' + str(value) + '"\n')
            self.__already_exported[environment_variable] = True
        if os.getenv('AUGUR_DEBUG_LOG_ENV', '0') == '1':
            logger.debug('{}:{} = {}'.format(section, name, value))
        return value