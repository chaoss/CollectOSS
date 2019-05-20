from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests

class CollectorTask:
    """ Worker's perception of a task in its queue
    Holds a message type (EXIT, TASK, etc) so the worker knows how to process the queue entry
    and the github_url given that it will be collecting data for
    """
    def __init__(self, message_type='TASK', github_url=None):
        self.type = message_type
        self.github_url = github_url


def collect(queue, config):
    """ Function to process each entry in the worker's task queue
    Determines what action to take based off the message type
    """
    while True:
        try:
            message = queue.get()
        except Queue.Empty:
            break

        if message.type == 'EXIT':
            break
        if message.type != 'TASK':
            raise ValueError(f'{message.type} is not a recognized task type')
        print(message.github_url)

        if message.type == 'TASK':
            query(message.github_url)

def query(git_url):
    """ Data collection function
    Query the github api for contributors and issues (not yet implemented)
    """
    path = urlparse(url)
    split = path[2].split('/')

    owner = split[1]
    name = split[2]

    url = ("https://api.github.com/repos/" + owner + "/" + name + "/contributors")

    request = requests.get(url)
    if request.status_code == 200:
        print(request.json())
        return request.json()
    else:
        raise Exception("ERROR {}".format(request.status_code)) 
    #call method that starting



class BadgeWorker:
    """ Worker that collects data from the Github API and stores it in our database
    task: current task being worked on
    child: current process of the queue being ran
    queue: queue of tasks to be fulfilled
    config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config, task=None):
        self._task = task
        self._child = None
        self._queue = Queue()
        self.config = config
        # self.update_config(self, config)
        self.API_KEY = self.config['key']
        
        specs = {
            "id": "com.augurlabs.core.badge_worker",
            "location": "http://localhost:51232",
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["issues"]
                }
            ],
            "config": [self.config]
        }

        requests.post('http://localhost:5000/api/workers', json=specs) #hello message
        

    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            'database_connection_string': 'psql://localhost:5432/augur',
            "key": "",
            "display_name": "",
            "description": "",
            "required": 1,
            "type": "string"
        }
        self.config.update(config)
        self.API_KEY = self.config['github_api_key']

    @property
    def task(self):
        """ Property that is returned when the worker's current task is referenced
        """
        return self._task
    
    @task.setter
    def task(self, value):
        """ Method to set or update the current task property's value
        Adds this task to the queue, and calls method to process queue
        """
        git_url = value[0]['given']['git_url']
        self._queue.put(CollectorTask(message_type='TASK', github_url=git_url))
        if self._queue.empty(): 
            if 'github.com' in git_url:
                self._task = value
                self.run()
        # else:
            # raise ValueError('Queue is already full')

    def cancel(self):
        """ Delete/cancel current task
        """
        self._task = None

    def run(self):
        """ Kicks off the processing of the queue if it is not already being processed
        Gets run whenever a new task is added
        """
        if not self._child:
            self._child = Process(target=collect, args=((self._queue, self.config),))