#SPDX-License-Identifier: MIT
import logging, json
import pandas as pd
import sqlalchemy as s

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.session import DatabaseSession
from augur.tasks.github.util.github_paginator import GithubPaginator
from augur.application.db.models import ContributorRepo
from augur.application.db.engine import create_database_engine

### This worker scans all the platform users in Augur, and pulls their platform activity 
### logs. Those are then used to analyze what repos each is working in (which will include repos not
### tracked in the Augur instance.)
### Logic: For each unique platform contributor, gather non duplicate events, using the GitHub "id"
### for the event API (GitLab coming!)


######################
#
# IN PROGRESS
#
######################

@celery.task
def contributor_breadth_model() -> None:

    logger = logging.getLogger(contributor_breadth_model.__name__)

    tool_source = 'Contributor Breadth Worker'
    tool_version = '0.0.1'
    data_source = 'GitHub API'


    ## Get all the contributors currently in the database
    #!/usr/bin/env python3

    #cntrb_key = gh_login

    cntrb_login_query = s.sql.text("""
        SELECT DISTINCT gh_login, cntrb_id 
        FROM augur_data.contributors 
        WHERE gh_login IS NOT NULL
    """)

    current_cntrb_logins = json.loads(pd.read_sql(cntrb_login_query, create_database_engine(), params={}).to_json(orient="records"))

    ## We need a list of all contributors so we can iterate through them to gather events
    ## We need a list of event ids to avoid insertion of duplicate events. We ignore the event
    ## If it already exists

    logger.info(f"Contributor Logins are: {current_cntrb_logins}")

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

    current_event_ids = json.loads(pd.read_sql(dup_query, create_database_engine(), params={}).to_json(orient="records"))

    #Convert list of dictionaries to regular list of 'event_ids'.
    #The only values that the sql query returns are event_ids so
    #it makes no sense to be a list of many dicts of one key.
    current_event_ids = [value for elem in current_event_ids for value in elem.values()]

    logger.info(f"current event ids are: {current_event_ids}")

    for cntrb in current_cntrb_logins:

        repo_cntrb_url = f"https://api.github.com/users/{cntrb['gh_login']}/events"
        # source_cntrb_repos seemed like not exactly what the variable is for; its a list of actions for
        # each Github gh_login value already in our database

        with DatabaseSession(logger) as session:
            cntrb_events = []
            for page_data, page in GithubPaginator(repo_cntrb_url, session.oauths, logger).iter_pages():

                if page_data:
                    cntrb_events += page_data

        process_contributor_events(cntrb, cntrb_events, current_event_ids, logger)

        # source_cntrb_events = self.paginate_endpoint(repo_cntrb_url, action_map=action_map,
        #      table=self.contributor_repo_table)

def process_contributor_events(cntrb, cntrb_events, current_event_ids, logger):

    if not cntrb_events:
        logger.info("There are no events, or new events for this user.\n")
        return

    ## current_event_ids are the ones ALREADY IN THE AUGUR DB. SKIP THOSE.
    ## source_cntrb_events are the ones the API pulls.
    cntrb_repos_insert = []
    for event_id_api in cntrb_events:
        logger.info(f"Keys of event_id_api: {event_id_api.keys()}")
        #logger.info(f"Keys of current_event_ids: {current_event_ids.keys()}")
        if int(event_id_api['id']) in current_event_ids:
            continue


        cntrb_repos_insert.append({
            "cntrb_id": cntrb['cntrb_id'],
            "repo_git": event_id_api['repo']['url'],
            "tool_source": tool_source,
            "tool_version": tool_version,
            "data_source": data_source,
            "repo_name": event_id_api['repo']['name'],
            "gh_repo_id": event_id_api['repo']['id'],
            "cntrb_category": event_id_api['type'],
            "event_id": event_id_api['id'],
            "created_at": event_id_api['created_at']
        })



        # else:
        #     # Print the message if the value does not exist
        #     logger.info(f"event_id is found in JSON data {current_event_ids[event_id]}.")

    ########################################################
    # Do the Inserts
    ########################################################

    #cntrb_repos_insert = []
    #cntrb_ids_idx = pd.Index(cntrb_ids, name=contributors)

    cntrb_repo_insert_result, cntrb_repo_update_result = self.bulk_insert(self.contributor_repo_table,
                 unique_columns='event_id', insert=cntrb_repos_insert)

