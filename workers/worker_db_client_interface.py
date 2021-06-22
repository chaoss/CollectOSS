#WORK IN PROGRESS NOT TO BE USED AT ALL IN PRESENT STATE

from workers.worker_base import Worker

class WorkerDBInterfacable(Worker):
    def __init__(self, worker_type, config={},given=[], models=[], data_tables=[], operations_tables=[]):
        super().__init__(worker_type,config,given,models)

        #TODO: finish sorting the previous constructor into thirds
        self.data_tables = data_tables
        self.operations_tables = operations_tables

        # count of tuples inserted in the database (to store stats for each task in op tables)
        self.update_counter = 0
        self.insert_counter = 0
        self._results_counter = 0
        
        self.config.update({
            'port': worker_port,
            'id': "workers.{}.{}".format(self.worker_type, worker_port),
            'capture_output': False,
            'location': 'http://{}:{}'.format(self.config['host'], worker_port),
            'port_broker': self.augur_config.get_value('Server', 'port'),
            'host_broker': self.augur_config.get_value('Server', 'host'),
            'host_database': self.augur_config.get_value('Database', 'host'),
            'port_database': self.augur_config.get_value('Database', 'port'),
            'user_database': self.augur_config.get_value('Database', 'user'),
            'name_database': self.augur_config.get_value('Database', 'name'),
            'password_database': self.augur_config.get_value('Database', 'password')
        })
        self.config.update(config)
        