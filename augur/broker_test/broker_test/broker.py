
class Worker(object):
    """docstring for Worker"""
    def __init__(self, ID, location, qualifications):
        self.ID = ID
        self.location = location
        self.qualifications = qualifications
        print(self.ID, self.location, self.qualifications)

class Broker(object):
    """docstring for Broker"""
    def __init__(self):
        print("Broker is alive!")
        self.connected_workers = []

    def add_new_worker(self, worker):
        self.connected_workers.append(Worker(worker['id'], worker['location'], worker['qualifications']))
        print(self.connected_workers)
