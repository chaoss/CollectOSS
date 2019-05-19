from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests

class CollectorTask:
    def __init__(self, message_type='TASK', github_url=None):
        self.type = message_type
        self.github_url = github_url


def collect(queue, config):
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



class GitHubWorker:
    def __init__(self, config, task=None):
        self._task = task
        self._child = None
        self._queue = Queue()
        self.config = config
        # self.update_config(self, config)
        self.API_KEY = self.config['key']
        print("initing")
        
        specs = {
            "id": "com.augurlabs.core.github_worker",
            "location": "http://localhost:51232",
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["issues"]
                }
            ],
            "config": [self.config]
        }


        requests.post('http://localhost:5000/api/workers', json=specs)
        

    def update_config(self, config):
        self.config = {
            'database_connection_string': 'psql://localhost:5432/augur',
            "key": "2759b561575060cce0d87c0f8d7f72f53fe35e14",
            "display_name": "GitHub API Key",
            "description": "API Token for the GitHub API v3",
            "required": 1,
            "type": "string"
        }
        self.config.update(config)
        self.API_KEY = self.config['github_api_key']

    @property
    def task(self):
        return self._task
    
    @task.setter
    def task(self, value):
        if not self._queue.empty(): 
            git_url = value[0]['given']['git_url']
            if 'github.com' in git_url:
                self._task = value
                self._queue.put(CollectorTask(message_type='TASK', github_url=git_url))
                self.run()
        else:
            raise ValueError('Queue is already full')

    def cancel(self):
        self._task = None

    def run(self):
        if not self._child:
            self._child = Process(target=collect, args=((self._queue, self.config),))