from augur_new.worker_base import *
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from random import choice
import collections

"""
    Should be designed on a per entity basis that has attributes that call 
    defined graphql queries.

    e.g. create a GHContributor graphql class that represents a contributor in github
    then various attributes call queries on the fly.

    Base level class will be a github repo.
"""


#Should take the query and two page variables for pagination
class GraphQlPageCollection(collections.abc.Sequence):
    def __init__(self,query,client,numPerPage=100):
        self.per_page = numPerPage
        self.query = query
        self.client = client

        self.url = "https://api.github.com/graphql"

    def __getitem__(self, index: int) -> dict:
        #borrowed from the default github paginator
        items_page = (index // self.per_page) + 1

        params = {
            "numRecords" : self.per_page,
            "cursor"    : None
        }
        pass


class GitHubRepo():
    def __init__(self, session: TaskSession, owner: str, repo: str):

        self.list_of_keys = get_list_of_oauth_keys(session.engine, session.config["Database"]["key"])
    
        self.url = "https://api.github.com/graphql"


        self.owner = owner
        self.repo = repo
    
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
