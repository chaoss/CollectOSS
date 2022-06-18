from celery import Celery
import redis

BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
app = Celery('tasks', broker=BROKER_URL,
             backend=BACKEND_URL, include=['augur_new.tasks.facade_tasks', 'augur_new.tasks.issue_tasks', 'augur_new.tasks.start_tasks'])


redis_conn = redis.from_url('redis://localhost:6379/2', decode_responses=True)


if __name__ == '__main__':
    app.start()
