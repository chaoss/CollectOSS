from multiprocessing import Process, Queue

class CollectorTask:
    def __init__(self, message_type='TASK', github_url=None):
        self.type = message_type
        self.github_url = github_url



def collect(queue, config):
    while True:
        message = queue.get()
        if message.type == 'EXIT':
            break;
        if message.type != 'TASK':
            raise ValueError(f'{message.type} is not a recognized task type')
        print(message.github_url)



class GitHubWorker:
    def __init__(self, config):
        self._task = task
        self._child = None
        self._queue = Queue()
        self.API_KEY = self.config['github_api_key']
        self.update_config(self, config)

    def update_config(self, config, queue):
        self.config = {
            'database_connection_string': 'psql://localhost:5432/augur',
            'github_api_key': None
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