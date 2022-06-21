from augur_new.worker_base import *
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from random import choice

"""
    Should be designed on a per entity basis that has attributes that call 
    defined graphql queries.

    e.g. create a GHContributor graphql class that represents a contributor in github
    then various attributes call queries on the fly.

    Base level class will be a github repo.
"""


class GitHubRepo():
    def __init__(self, session: TaskSession):

        self.list_of_keys = get_list_of_oauth_keys(session.engine, session.config["Database"]["key"])
    
        self.url = "https://api.github.com/graphql"
    
    @property
    def headers(self):
        key_value = choice(self.list_of_keys)

        return {"Authorization": f"Bearer {key_value}"}
    

    @property
    def gqlClient(self):
        #Create objects to execute graphql queries on the endpoint
        #Use random key defined earlier.
        
        transport = AIOHTTPTransport(url=self.url,headers=self.headers)
        client = Client(transport=transport)
        return client
