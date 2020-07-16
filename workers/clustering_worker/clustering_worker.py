import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
from workers.worker_base import Worker

class ClusteringWorker(Worker):
	def __init__(self, config={}):
		self.logger.info("Clustering Worker init")
	
		worker_type = "clustering_worker"
		
		given = [['git_url']]
		models = ['clustering']

		data_tables = ['repo_cluster_messages']
		operations_tables = ['worker_history', 'worker_job']

		# Run the general worker initialization
		super().__init__(worker_type, config, given, models, data_tables, operations_tables)

		self.config.update({
			'api_host': self.augur_config.get_value('Server', 'host'),
			'api_port': self.augur_config.get_value('Server', 'port')
		})

		# Define data collection info
		self.tool_source = 'Clustering Worker'
		self.tool_version = '0.0.0'
		self.data_source = 'Non-existent API'

	def clustering_model(self, task, repo_id):
		logging.info("Clustering Worker init")
		
		'''
		repo_group_sql = s.sql.text("""
					SELECT repo_group_id
					FROM repo
					WHERE repo_id = :repo_id
				""")
		repo_group_id = self.db.execute(repo_group_sql, {'repo_id': repo_id}).fetchone()[1]
		'''
		
		
		# Collection and insertion of data happens here
		""" Collect Data """
		self.logger.info("Clustering Model Called")
		
		# base_url = 'http://{}:{}/api/unstable/repo-groups/9999/repos/{}/'.format(
			# self.config['api_host'], self.config['api_port'], repo_id)
		# ...

		# Register this task as completed.
		#	This is a method of the worker class that is required to be called upon completion
		#	of any data collection model, this lets the broker know that this worker is ready
		#	for another task
		
		
		#inserting data
		record = {
				  'repo_id': int(repo_id),
				  'cluster_content': 0,
				  'cluster_mechanism' : 0
				  }
		result = self.db.execute(self.repo_cluster_messages_table.insert().values(record))
		logging.info("Primary key inserted into the repo_insights_records table: {}".format(result.inserted_primary_key))
		self.register_task_completion(task, repo_id, 'clustering')

