#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
from workers.worker_git_integration import WorkerGitInterfaceable
import pandas as pd
import sqlalchemy as s
from workers.worker_base import Worker

### This worker scans all the platform users in Augur, and pulls their platform activity 
### logs. Those are then used to analyze what repos each is working in (which will include repos not
### tracked in the Augur instance.)
### Logic: For each unique platform contributor, gather non duplicate events, using the GitHub "id"
### for the event API (GitLab coming!)

class ContributorBreadthWorker(WorkerGitInterfaceable):
    def __init__(self, config={}):
        
    
        worker_type = "contributor_breadth_worker"

    
        given = [['github_url']]


        models = ['contributor_breadth']


        data_tables = ['contributor_repo']

        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        # Define data collection info
        self.tool_source = 'Contributor Breadth Worker'
        self.tool_version = '0.0.1'
        self.data_source = 'GitHub API'

        # Do any additional configuration after the general initialization has been run
        self.config.update(config)

    def contributor_breadth_model(self, task, repo_id):
        ## Get all the contributors currently in the database
        #!/usr/bin/env python3

        #cntrb_key = gh_login

        cntrb_login_query = s.sql.text("""
            SELECT DISTINCT gh_login, cntrb_id 
            FROM augur_data.contributors 
            WHERE gh_login IS NOT NULL
        """)

        current_cntrb_logins = json.loads(pd.read_sql(cntrb_login_query, self.db, \
            params={}).to_json(orient="records"))

        ## We need a list of all contributors so we can iterate through them to gather events
        ## We need a list of event ids to avoid insertion of duplicate events. We ignore the event
        ## If it already exists

        self.logger.info(f"Contributor Logins are: {current_cntrb_logins}")

        ########################################################
        #### List of existing contributor ids and their corresponding gh_login
        #### is contained in the `current_cntrb_logins` variable
        ########################################################


        ########################################################
        #### Define the action map for events to avoid duplicates
        #### Query event_ids so a list of existing events are 
        #### Available for duplicate checking
        ########################################################

        action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['event_id']
            }
        }

        # Eliminate any duplicate event_ids from what will be inserted
        # Because of Bulk Insert
        # keyVal = event_id

        ########################################################
        # Query for existing event ids to avoid duplication
        ########################################################

        dup_query = s.sql.text("""
            SELECT DISTINCT event_id 
            FROM augur_data.contributor_repo
            WHERE 1 = 1
        """)

        current_event_ids = json.loads(pd.read_sql(dup_query, self.db, \
            params={}).to_json(orient="records"))
        
        #Convert list of dictionaries to regular list of 'event_ids'. 
        #The only values that the sql query returns are event_ids so
        #it makes no sense to be a list of many dicts of one key.
        current_event_ids = [value for elem in current_event_ids for value in elem.values()]

        self.logger.info(f"current event ids are: {current_event_ids}")

        cntrb_repos_insert = []

        for cntrb in current_cntrb_logins:

            
            repo_cntrb_url = f"https://api.github.com/users/{cntrb['gh_login']}/events"
            # source_cntrb_repos seemed like not exactly what the variable is for; its a list of actions for
            # each Github gh_login value already in our database
            source_cntrb_events = self.paginate_endpoint(repo_cntrb_url, action_map=action_map,
                 table=self.contributor_repo_table)

            if len(source_cntrb_events['all']) == 0:
              self.logger.info("There are no events, or new events for this user.\n") 
              continue 
            else:  
              ## current_event_ids are the ones ALREADY IN THE AUGUR DB. SKIP THOSE.
              ## source_cntrb_events are the ones the API pulls. 
              for event_id_api in source_cntrb_events['all']:
                self.logger.info(f"Keys of event_id_api: {event_id_api.keys()}")
                #self.logger.info(f"Keys of current_event_ids: {current_event_ids.keys()}")
                if int(event_id_api['id']) in current_event_ids: 
                  continue 
                else: 
                #self.register_task_completion(task, repo_id, 'contributor_breadth')             
                  cntrb_repos_insert.append({
                          "cntrb_id": cntrb['cntrb_id'],
                          "repo_git": event_id_api['repo']['url'],
                          "tool_source": self.tool_source,
                          "tool_version": self.tool_version,
                          "data_source": self.data_source,
                          "repo_name": event_id_api['repo']['name'],
                          "gh_repo_id": event_id_api['repo']['id'],
                          "cntrb_category": event_id_api['type'],
                          "event_id": event_id_api['id'],
                          "created_at": event_id_api['created_at']

                    })
                  
                  #Use this instead of the bulk insert if that is needed in the future.
                  # (i.e., if an initial scan uses too much RAM on a large repo.)
                  """"
                  self.db.execute(self.contributor_repo_table.insert().values({
                          "cntrb_id": cntrb['cntrb_id'],
                          "repo_git": cntrb_repo['repo']['url'],
                          "tool_source": self.tool_source,
                          "tool_version": self.tool_version,
                          "data_source": self.data_source,
                          "repo_name": cntrb_repo['repo']['name'],
                          "gh_repo_id": cntrb_repo['repo']['id'],
                          "cntrb_category": cntrb_repo['type'],
                          "event_id": cntrb_repo['id'],
                          "created_at": cntrb_repo['created_at']

                    }))"""

            # else:
            #     # Print the message if the value does not exist
            #     self.logger.info(f"event_id is found in JSON data {current_event_ids[event_id]}.")

        ########################################################
        # Do the Inserts
        ########################################################

        #cntrb_repos_insert = []
        #cntrb_ids_idx = pd.Index(cntrb_ids, name=contributors)

        cntrb_repo_insert_result, cntrb_repo_update_result = self.bulk_insert(self.contributor_repo_table,
                     unique_columns='event_id', insert=cntrb_repos_insert)

        self.register_task_completion(task, '0', 'contributor_breadth')

