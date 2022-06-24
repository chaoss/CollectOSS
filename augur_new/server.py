import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis

from augur_new.config import AugurConfig
from augur_new.tasks.start_tasks import start


ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# initialize the flask app
config = AugurConfig(ROOT_AUGUR_DIR)

user = config.get_value('Database', 'user')
password = config.get_value('Database', 'password')
host = config.get_value('Database', 'host')
port = config.get_value('Database', 'port')
database = config.get_value('Database', 'database')

DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
    user, password, host, port, database)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_STR


# intialize the redis conn
# redis_conn = redis.from_url('redis://localhost:6379/2', decode_responses=True)

owner = "chaoss"
repo = "augur"

start.delay(owner, repo)

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# db = SQLAlchemy(app)
# migrate = Migrate(app, db, compare_type=True)

# from celery import Celery
# import redis

# print("Initializing Celery app")
# BROKER_URL = 'redis://localhost:6379/0'
# BACKEND_URL = 'redis://localhost:6379/1'
# app = Celery('tasks', broker=BROKER_URL,
#              backend=BACKEND_URL, include=['augur_new.tasks.facade_tasks', 'augur_new.tasks.issue_tasks', 'augur_new.tasks.start_tasks'])



if __name__ == '__main__':
    app.run()
