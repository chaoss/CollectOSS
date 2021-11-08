import pytest
import docker
import subprocess
import json
import os
from workers.worker_persistance import *

#Define a dummy worker class that gets the methods we need without running super().__init__
class Dummy(Persistant):
    def __init__(self,database_connection):
        self.db = database_connection
        self.logger = logging.getLogger()


#utility functions
def poll_database_connection(database_string):
    print("Attempting to create db engine")
    
    db = s.create_engine(database_string, poolclass=s.pool.NullPool,
      connect_args={'options': '-csearch_path={}'.format('augur_data')})
    
    return db
    

#database connection 
@pytest.fixture
def database_connection():
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
    #Remove the name 
    databaseContainer.remove()
    
