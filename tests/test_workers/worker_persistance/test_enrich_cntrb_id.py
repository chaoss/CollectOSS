#SPDX-License-Identifier: MIT
import pytest
import docker
import subprocess
import json
import os
from workers.worker_persistance import *
#from tests.test_workers.test_data import *

#utility functions
def poll_database_connection(database_string):
    print("Attempting to create db engine")
    
    db = s.create_engine(database_string, poolclass=s.pool.NullPool,
      connect_args={'options': '-csearch_path={}'.format('augur_data')})
    
    return db
    

#database connection 
@pytest.fixture
def set_up_database():
    #Create client to docker daemon
    client = docker.from_env()
    
    print("Building a container")
    
    cwd = os.getcwd()
    #Build the test database from the dockerfile and download
    #Postgres docker image if it doesn't exist.
    ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    ROOT_AUGUR_DIR = str(ROOT_AUGUR_DIR).replace("/tests/test_workers","/")
    
    buildString = ROOT_AUGUR_DIR
    
    #change to root augur directory
    os.chdir(ROOT_AUGUR_DIR)
    
    print(os.getcwd())
    
    image = client.images.build(path=buildString,dockerfile="util/docker/database/Dockerfile", pull=True)
    
    #Start a container and detatch
    #Wait until the database is ready to accept connections
    databaseContainer = client.containers.run(image[0].id, command=None, ports={'5432/tcp': 5400}, detach=True)
    
    databaseContainer.rename("Test_database")
    
    DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            "augur", "augur", "172.17.0.1", 5400, "test"
    )
    
    time.sleep(10)
    
    #Get a database connection object from postgres to test connection and pass to test when ready
    db = poll_database_connection(DB_STR)
        
    #Setup complete, return the database object
    yield db
    
    #Cleanup the docker container by killing it.
    databaseContainer.kill()
    
#Sample source data generation that pulls json data that has contributions listed
@pytest.fixture
def sample_source_data_enriched():
    jsonFile = open("tests/test_workers/worker_persistance/contributors.json")

    source_data = json.load(jsonFile)

    jsonFile.close()
    return source_data

#Sample source data generation that opens json data that doesn't have contributions listed
@pytest.fixture
def sample_source_data_unenriched():
    jsonFile = open("tests/test_workers/worker_persistance/contributors_un_enriched.json")

    source_data = json.load(jsonFile)

    jsonFile.close()
    return source_data


def test_enrich_data_primary_keys(set_up_database, sample_source_data_enriched, sample_source_data_unenriched):
    
    print(sample_source_data_enriched)
    print(sample_source_data_unenriched)
    
    data_tables = ['contributors', 'pull_requests', 'commits',
                            'pull_request_assignees', 'pull_request_events', 'pull_request_labels',
                            'pull_request_message_ref', 'pull_request_meta', 'pull_request_repo',
                            'pull_request_reviewers', 'pull_request_teams', 'message', 'pull_request_commits',
                            'pull_request_files', 'pull_request_reviews', 'pull_request_review_message_ref',
                            'contributors_aliases', 'unresolved_commit_emails']
    operations_tables = ['worker_history', 'worker_job']
    
    metadata = s.MetaData()
    # Reflect only the tables we will use for each schema's metadata object
    metadata.reflect(set_up_database,only=data_tables)
    Base = automap_base(metadata=metadata)
    Base.prepare()
    
    tableDict = {}
    
    for table in data_tables:
        print(f"Table: {table}")
        tableDict['{}_table'.format(table)] = Base.classes[table].__table__
        
    print(tableDict['contributors_table'])
    
    cntrb = [
        {
            "cntrb_login": test_data_not_enriched['login'],
            "gh_user_id": test_data_not_enriched['id'],
            "gh_login": test_data_not_enriched['login'],
            "gh_url": test_data_not_enriched['url'],
            "gh_html_url": test_data_not_enriched['html_url'],
            "gh_node_id": test_data_not_enriched['node_id'],
            "gh_avatar_url": test_data_not_enriched['avatar_url'],
            "gh_gravatar_id": test_data_not_enriched['gravatar_id'],
            "gh_followers_url": test_data_not_enriched['followers_url'],
            "gh_following_url": test_data_not_enriched['following_url'],
            "gh_gists_url": test_data_not_enriched['gists_url'],
            "gh_starred_url": test_data_not_enriched['starred_url'],
            "gh_subscriptions_url": test_data_not_enriched['subscriptions_url'],
            "gh_organizations_url": test_data_not_enriched['organizations_url'],
            "gh_repos_url": test_data_not_enriched['repos_url'],
            "gh_events_url": test_data_not_enriched['events_url'],
            "gh_received_events_url": test_data_not_enriched['received_events_url'],
            "gh_type": test_data_not_enriched['type'],
            "gh_site_admin": test_data_not_enriched['site_admin'],
            "tool_source": "Test",
            "tool_version": "test_enrich_data_primary_keys",
            "data_source":"test_enrich_data_primary_keys"
    } for test_data_not_enriched in sample_source_data_unenriched
    ]
    
    
    set_up_database.execute(tableDict['contributors_table'].insert().values(cntrb))
    
    return
