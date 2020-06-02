import os
from datetime import datetime
import logging
import requests
import json
from urllib.parse import quote
from multiprocessing import Process, Queue

from linux_badge_worker import __data_source__, __tool_source__, __tool_version__
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from workers.worker_base import Worker

class BadgeWorker(Worker):
    """ Worker that collects repo badging data from CII
    config: database credentials, broker information, and ID
    """
    def __init__(self, config, task=None):
        given = [['git_url']]
        models = ['badges']

        data_tables = ['repo_badging']
        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(config, given, models, data_tables, operations_tables)

    def badges_model(self, entry_info, repo_id):
        """ Data collection and storage method
        Query the CII API and store the result in the DB for the badges model
        """
        git_url = entry_info['given']['git_url']
        logging.info("Collecting data for {}".format(git_url))
        extension = quote(git_url[0:-4])

        url = self.config['endpoint'] + extension
        logging.info("Hitting CII endpoint: " + url + " ...")
        data = requests.get(url=url).json()

        if data != []:
            logging.info("Inserting badging data for " + git_url)
            self.db.execute(self.repo_badging_table.insert()\
                            .values(repo_id=repo_id,
                                    data=data,
                                    tool_source=__tool_source__,
                                    tool_version=__tool_version__,
                                    data_source=__data_source__))

            self.results_counter += 1
        else:
            logging.info("No CII data found for {}\n".format(git_url))

        self.register_task_completion(entry_info, repo_id, "badges")
