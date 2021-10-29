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
    
    DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            "augur", "augur", "172.17.0.1", 5400, "test"
    )
    
    #Get a database connection object from postgres to test connection and pass to test when ready
    db = poll_database_connection(DB_STR)
    
    attempts = 0
    
    while attempts < 15:
        result = subprocess.Popen(f"psql -d {DB_STR} -c \"select now()\"")
        text = result.communicate()[0]
        connectionStatus = result.returncode
        print(connectionStatus)
        if connectionStatus == 0:
            break
        
        attempts += 1
        
    #Setup complete, return the database object
    yield db
    
    #Cleanup the docker container by killing it.
    databaseContainer.kill()
    
#Sample source data generation that pulls json data that has contributions listed
@pytest.fixture
def sample_source_data_enriched():
    jsonFile = open("contributors.json")

    source_data = jsonFile.load(jsonFile)

    jsonFile.close()
    return source_data

#Sample source data generation that opens json data that doesn't have contributions listed
@pytest.fixture
def sample_source_data_unenriched():
    jsonFile = open("contributors_un_enriched.json")

    source_data = jsonFile.load(jsonFile)

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
    metadata.reflect(set_up_database,data_tables)
    Base = automap_base(metadata=metadata)
    Base.prepare()
    
    tableDict = {}
    
    for table in data_tables:
        tableDict['{}_table'.format(table)] = Base.classes[table].__table__
    
    
    set_up_database.execute(tableDict['contributors_table'].insert().values(committer))
    
    return
