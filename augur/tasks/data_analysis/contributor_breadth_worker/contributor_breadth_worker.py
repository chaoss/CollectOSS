#SPDX-License-Identifier: MIT
import logging, json
import pandas as pd
import sqlalchemy as s
from datetime import datetime

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.github.util.github_task_session import GithubTaskManifest
from augur.tasks.github.util.github_paginator import GithubPaginator
from augur.application.db.models import ContributorRepo

### This worker scans all the platform users in Augur, and pulls their platform activity 
### logs. Those are then used to analyze what repos each is working in (which will include repos not
### tracked in the Augur instance.)
### Logic: For each unique platform contributor, gather non duplicate events, using the GitHub "id"
### for the event API (GitLab coming!)

@celery.task
def contributor_breadth_model() -> None:

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(contributor_breadth_model.__name__)

    tool_source = 'Contributor Breadth Worker'
    tool_version = '0.0.1'
    data_source = 'GitHub API'


    cntrb_login_query = s.sql.text("""
        SELECT DISTINCT gh_login, cntrb_id 
        FROM augur_data.contributors 
        WHERE gh_login IS NOT NULL
    """)

    with engine.connect() as connection:
        result = connection.execute(cntrb_login_query)

    current_cntrb_logins = [dict(row) for row in result.mappings()]


    cntrb_newest_events_query = s.sql.text("""
        SELECT c.gh_login, MAX(cr.created_at) as newest_event_date
        FROM contributor_repo AS cr
        JOIN contributors AS c ON cr.cntrb_id = c.cntrb_id
        GROUP BY c.gh_login;
    """)

    with engine.connect() as connection:
        cntrb_newest_events_list = connection.execute(cntrb_newest_events_query)
    
    cntrb_newest_events_list = [dict(row) for row in cntrb_newest_events_list.mappings()]

    cntrb_newest_events_map = {}
    for cntrb_event in cntrb_newest_events_list:

        gh_login = cntrb_event["gh_login"]
        newest_event_date = cntrb_event["newest_event_date"]
        
        cntrb_newest_events_map[gh_login] = newest_event_date


    with GithubTaskManifest(logger) as manifest:

        index = 1
        total = len(current_cntrb_logins)
        for cntrb in current_cntrb_logins:

            print(f"Processing cntrb {index} of {total}")
            index += 1

            repo_cntrb_url = f"https://api.github.com/users/{cntrb['gh_login']}/events"

            newest_event_in_db = datetime(1970, 1, 1)
            if cntrb["gh_login"] in cntrb_newest_events_map:
                newest_event_in_db = cntrb_newest_events_map[cntrb["gh_login"]]
                

            cntrb_events = []
            for page_data, page in GithubPaginator(repo_cntrb_url, manifest.key_auth, logger).iter_pages():

                if page_data: 
                    cntrb_events += page_data

                    oldest_event_on_page = datetime.strptime(page_data[-1]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                    if oldest_event_on_page < newest_event_in_db:
                        print("Found cntrb events we already have...skipping the rest")
                        break

            if len(cntrb_events) == 0:
                logger.info("There are no cntrb events, or new events for this user.\n")
                continue

            events = process_contributor_events(cntrb, cntrb_events, logger, tool_source, tool_version, data_source)

            logger.info(f"Inserting {len(events)} events")
            natural_keys = ["event_id", "tool_version"]
            manifest.augur_db.insert_data(events, ContributorRepo, natural_keys)  


def process_contributor_events(cntrb, cntrb_events, logger, tool_source, tool_version, data_source):

    cntrb_repos_insert = []
    for event_id_api in cntrb_events:

        cntrb_repos_insert.append({
            "cntrb_id": cntrb['cntrb_id'],
            "repo_git": event_id_api['repo']['url'],
            "tool_source": tool_source,
            "tool_version": tool_version,
            "data_source": data_source,
            "repo_name": event_id_api['repo']['name'],
            "gh_repo_id": event_id_api['repo']['id'],
            "cntrb_category": event_id_api['type'],
            "event_id": int(event_id_api['id']),
            "created_at": event_id_api['created_at']
        })

    return cntrb_repos_insert
