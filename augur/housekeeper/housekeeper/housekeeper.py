import logging
import requests
from multiprocessing import Process, Queue
import time
import schedule
import sqlalchemy as s
import pandas as pd

logging.basicConfig(filename='logs/server.log')
logger = logging.getLogger(name="housekeeper_logger")


UPDATE_DELAY = 5 #5 sec for testing # 86400 (1 day)

class HouseKeeper:

    def __init__(self, config):

        self.config = config
        DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['database']
        )

        dbschema='augur_data'
        self.db = s.create_engine(DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})
        repoUrlSQL = s.sql.text("""
            SELECT repo_git FROM repo
        """)

        rs = pd.read_sql(repoUrlSQL, self.db, params={})

        self.care_about = rs['repo_git'].values.tolist()

        self.run()


    def run(self):


        # schedule.every(30).days.at("10:30").do(job) #BADGING
        # schedule.every().day.at("10:30").do(job) #FACADE?
        # schedule.every(7).days.at("10:30").do(job) #ISSUES?

        #testing
        # schedule.every(2).seconds.do(self.update_model, model="issues")
        schedule.every(15).seconds.do(self.update_model, model="badges")

        while True:
            schedule.run_pending()
            time.sleep(1)

    def update_model(self, model=None):
        print("updating model: " + model)

        for repo in self.care_about:

            job = {
                "job_type": "MAINTAIN", 
                "models": [model], 
                "given": {
                    "git_url": repo
                }
            }

            requests.post('http://localhost:5000/api/job', json=job)



