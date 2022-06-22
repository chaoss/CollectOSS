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
    #Bind is needed for things like query by repo. Contains bind variables for the graphql query
    def __init__(self,query,client,bind={},numPerPage=100):
        self.per_page = numPerPage
        self.query = query
        self.client = client

        self.url = "https://api.github.com/graphql"

        self.page_cache = []

        self.bind = bind

    def __getitem__(self, index):# -> dict:
        #first try cache
        try:
            return self.page_cache[index]
        except KeyError:
            pass


        #borrowed from the default github paginator
        items_page = (index // self.per_page) + 1

        params = {
            "numRecords" : self.per_page,
            "cursor"    : None
        }

        params.update(self.bind)


        for page in range(items_page):
            result = self.client.execute(self.query,variable_values=params)

            self.page_cache.extend(result[params['values'][0]][params['values'][1]])
            
            #check if there is a next page to paginate. (graphql doesn't support random access)
            if result['pageInfo']['hasNextPage']:
                params['cursor'] = result['pageInfo']['endCursor']
            else:
                break
        

        return self.page_cache[index]


class GitHubRepo():
    def __init__(self, session, owner, repo):

        self.list_of_keys = get_list_of_oauth_keys(session.engine, session.config["Database"]["key"])
    
        self.url = "https://api.github.com/graphql"


        self.owner = owner
        self.repo = repo
    
    @property
    def headers(self):
        key_value = choice(self.list_of_keys)

        header = {'Authorization': f'Bearer {key_value}'}
        return header
    

    @property
    def gqlClient(self):
        #Create objects to execute graphql queries on the endpoint
        #Use random key defined earlier.

        transport = AIOHTTPTransport(url=self.url,headers=self.headers)
        client = Client(transport=transport)
        return client
    
    def get_issues_collection(self):

        #Cursor and numRecords is handled by the collection internals
        query = gql("""
            query($numRecords: Int!, $cursor: String) {
                repository(owner:$owner, name:$repo) {
                    issues(first: $numRecords, after:$cursor) {
                        edges {
                            node {
                                title
                                body
                                closed
                                url
                                labels(first:5) {
                                    edges {
                                        node {
                                            name
                                        }
                                    }
                                createdAt
                                databaseId
                                }
                        
                            }
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        """)

        #Values specifies the dictionary values we want to return as the issue collection.
        #e.g. here we get the issues of the specified repository.
        values = ("repository","issues")
        params = {
            'owner' : self.owner,
            'repo' : self.repo,
            'values' : values
        }

        

        issueCollection = GraphQlPageCollection(query, self.gqlClient,bind=params)

        return issueCollection
