#WORK IN PROGRESS NOT TO BE USED AT ALL IN PRESENT STATE

from workers.worker_base import Worker

class WorkerDBInterfacable(Worker):
    def __init__(self, worker_type, config={}, data_tables=[], operations_tables=[]):
        super().__init__(worker_type,config)

        # count of tuples inserted in the database (to store stats for each task in op tables)
        self.update_counter = 0
        self.insert_counter = 0
        self._results_counter = 0
        #TODO: finish sorting the previous constructor into thirds