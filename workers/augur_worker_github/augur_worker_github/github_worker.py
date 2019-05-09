class GitHubWorker:
    def __init__(self, config):
        self._task = None
        self.db = None
        self.API_KEY = self.config['github_api_key']
        self.update_config(self, config)

    def update_config(self, config):
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
        if not self.task: 
            self._task = value
            self.run()
        else:
            raise ValueError('Task is already set')

    def cancel(self):
        self._task = None

    def run(self):
        # go do github stuff
        pass