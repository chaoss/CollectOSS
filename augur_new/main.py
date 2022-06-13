from celery import Celery

BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
app = Celery('tasks', broker=BROKER_URL,
             backend=BACKEND_URL, include=['augur_new.tasks'])

if __name__ == '__main__':
    app.start()
