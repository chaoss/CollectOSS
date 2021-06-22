#WORK IN PROGRESS NOT TO BE USED AT ALL IN PRESENT STATE

from workers.worker_base import Worker
from workers.worker_db_client_interface import WorkerDBInterfacable

class WorkerGitInterfaceable(Worker):
    def __init__(self, worker_type, config={}, given=[], models=[], data_tables=[], operations_tables=[], platform="github"):
        super().___init__(worker_type, config, given, models, data_tables, operations_tables)

        self.platform = platform
        self.given = given
        self.models = models

        self.specs = {
            'id': self.config['id'], # what the broker knows this worker as
            'location': self.config['location'], # host + port worker is running on (so broker can send tasks here)
            'qualifications':  [
                {
                    'given': self.given, # type of repo this worker can be given as a task
                    'models': self.models # models this worker can fill for a repo as a task
                }
            ],
            'config': self.config
        }

        # Send broker hello message
        if self.config['offline_mode'] is False:
            self.connect_to_broker()

        try:
            self.tool_source
            self.tool_version
            self.data_source
        except:
            self.tool_source = 'Augur Worker Testing'
            self.tool_version = '0.0.0'
            self.data_source = 'Augur Worker Testing'