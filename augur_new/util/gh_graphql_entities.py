from augur_new.tasks.task_session import *
import asyncio
#from gql import gql, Client
#from gql.transport.aiohttp import AIOHTTPTransport
import httpx
import json
from random import choice
import collections

"""
    Should be designed on a per entity basis that has attributes that call 
    defined graphql queries.

    e.g. create a GHContributor graphql class that represents a contributor in github
    then various attributes call queries on the fly.

    Base level class will be a github repo.


    PR_reviews, events, messages, pr_commits, pr_files(already done convert it)
"""


#Should take the query and two page variables for pagination
class GraphQlPageCollection(collections.abc.Sequence):
    #Bind is needed for things like query by repo. Contains bind variables for the graphql query
    def __init__(self,query,keyAuth,logger,bind={},numPerPage=100,url="https://api.github.com/graphql"):
        self.per_page = numPerPage
        self.query = query
        self.keyAuth = keyAuth
        self.logger = logger

        self.url = url

        self.page_cache = []

        self.bind = bind

    def hit_api(self,query,variables={}):
        self.logger.debug(f"Sending query {query}  to github graphql")

        response = None
        with httpx.Client() as client:

            try:
                json_dict = {
                    'query' : query
                }

                #If there are bind variables bind them to the query here.
                if variables:

                    json_dict['variables'] = variables
                    #Get rid of values tuple used to extract results so its not used in actual request.
                    json_dict['variables'].pop("values",None)
                    json_dict['variables'] = json_dict['variables']
                    #print(json_dict['variables'])
                
                #print(json.dumps(json_dict))
                response = client.post(
                    url=self.url,auth=self.keyAuth,json=json_dict
                    )
            
            except TimeoutError:
                self.logger.info("Request timed out. Sleeping 10 seconds and trying again...\n")
                time.sleep(10)
                return None
            except httpx.TimeoutException:
                self.logger.info("httpx.ReadTimeout. Sleeping 10 seconds and trying again...\n")
                time.sleep(10)
                return None
        
        return response
    
    async def async_hit_api(self,client,query,variables={}):
        self.logger.debug(f"Sending query {query}  to github graphql")

        response = None

        try:
            json_dict = {
                'query' : query
            }

            #If there are bind variables bind them to the query here.
            if variables:

                json_dict['variables'] = variables
                #Get rid of values tuple used to extract results so its not used in actual request.
                json_dict['variables'].pop("values",None)
                json_dict['variables'] = json_dict['variables']
                #print(json_dict['variables'])
            
            #print(json.dumps(json_dict))
            response = await client.post(
                url=self.url,auth=self.keyAuth,json=json_dict
                )
        
        except TimeoutError:
            self.logger.info("Request timed out. Sleeping 10 seconds and trying again...\n")
            time.sleep(10)
            return None
        
        return response


    def extract_paginate_result(self,responseObject):

        print(responseObject.json())
        
        result_dict = responseObject.json()['data']

        #print(result_dict)
        #extract the core keys that we want from our query
        core = result_dict[self.bind['values'][0]][self.bind['values'][1]]

        return core


    def __getitem__(self, index):# -> dict:
        #first try cache
        try:
            return self.page_cache[index]
        except:
            pass


        #borrowed from the default github paginator
        items_page = (index // self.per_page) + 1

        params = {
            "numRecords" : self.per_page,
            "cursor"    : None
        }

        params.update(self.bind)


        for page in range(items_page):
            result = self.hit_api(self.query,variables=params)#self.client.execute(self.query,variable_values=params)

            #print(result)

            coreData = self.extract_paginate_result(result)
            #extract the content from the graphql query result

            content = [data['node'] for data in list(coreData['edges'])]

            self.page_cache.extend(content)

            #extract the pageinfo
            pageInfo = coreData['pageInfo']
            
            #check if there is a next page to paginate. (graphql doesn't support random access)
            if pageInfo['hasNextPage']:
                params['cursor'] = pageInfo['endCursor']
            else:
                break
        

        return self.page_cache[index]
    
    def __len__(self):
        params = {
            "numRecords" : 2,
            "cursor"    : None
        }
        params.update(self.bind)

        result = self.hit_api(self.query,variables=params)#self.client.execute(self.query,variable_values=params)
        coreData = self.extract_paginate_result(result)

        totalCount = int(coreData['totalCount'])

        return totalCount
    
    def __iter__(self):
        params = {
            "numRecords" : self.per_page,
            "cursor"    : None
        }
        params.update(self.bind)

        result = self.hit_api(self.query,variables=params)#self.client.execute(self.query,variable_values=params)

        coreData = self.extract_paginate_result(result)


        if int(coreData['totalCount']) == 0:
            yield None
            return
        
        #extract the content from the graphql query result 
        for data in coreData['edges']:
            yield data['node']

        while coreData['pageInfo']['hasNextPage']:
            params['cursor'] = coreData['pageInfo']['endCursor']

            result = self.hit_api(self.query,variables=params)#self.client.execute(self.query,variable_values=params)

            coreData = self.extract_paginate_result(result)

            if len(coreData['edges']) == 0:
                return
            
            for data in coreData['edges']:
                yield data['node']

    #recursive function to paginate an endpoint's pages close to all at once.
    #Limited by graphql really only supporting cursor pagination as a reasonable option.
    async def get_next_page(self,gql_session,cursor=None):
        records = []

        params = {
            "numRecords" : self.per_page,
            "cursor"    : cursor
        }
        params.update(self.bind)

        result = self.async_hit_api(gql_session, self.query)#gql_session.execute(self.query,variable_values=params)
        coreData = self.extract_paginate_result(result)

        if coreData['pageInfo']['hasNextPage']:
            records.extend(self.get_next_page(gql_session=gql_session,cursor=coreData['pageInfo']['endCursor']))
    
        records.extend([data['node'] for data in coreData['edges']])

        yield records

        return


    async def __aiter__(self):
        params = {
            "numRecords" : self.per_page,
            "cursor"    : None
        }
        params.update(self.bind)

        result = self.hit_api(self.query,variables=params)#self.client.execute(self.query,variable_values=params)
        coreData = self.extract_paginate_result(result)

        #Check if one page is needed
        if int(coreData['totalCount']) <= self.per_page:
            
            for data in coreData['edges']:
                yield data['node']
            
            return
        
        # Using `async with` on the client will start a connection on the transport
        # and provide a `session` variable to execute queries on this connection
        async with httpx.AsyncClient() as gql_session:

            data_list = await self.get_next_page(gql_session=gql_session)

            yield data_list

            return


#use httpx and pass random_key_auth
class GitHubRepo():
    def __init__(self, session, owner, repo):

        self.keyAuth = session.oauths
        self.url = "https://api.github.com/graphql"

        self.logger = session.logger

        self.owner = owner
        self.repo = repo
    
    
    def get_issues_collection(self):

        #Cursor and numRecords is handled by the collection internals
        #totalCount is needed to furfill container class
        #edges has the 'content' of the issues
        query = """
            query($numRecords: Int!, $cursor: String, $owner: String!, $repo: String!) {
                repository(owner:$owner, name:$repo) {
                    issues(first: $numRecords, after:$cursor) {
                        totalCount
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
                                totalCount
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
        """

        #Values specifies the dictionary values we want to return as the issue collection.
        #e.g. here we get the issues of the specified repository.
        values = ("repository","issues")
        params = {
            'owner' : self.owner,
            'repo' : self.repo,
            'values' : values
        }

        

        issueCollection = GraphQlPageCollection(query, self.keyAuth,self.logger,bind=params)

        return issueCollection
    
    def get_pull_requests_collection(self):
        #Cursor and numRecords is handled by the collection internals
        #totalCount is needed to furfill container class
        #edges has the 'content' of the issues
        query = """
            query($numRecords: Int!, $cursor: String, $owner: String!, $repo: String!) {
                repository(owner:$owner, name:$repo) {
                    pullRequests(first: $numRecords, after:$cursor) {
                        totalCount
                        edges {
                            node {
                                title
                                body
                                closed
                                url
                        
                            }
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        """

        #Values specifies the dictionary values we want to return as the issue collection.
        #e.g. here we get the pullRequests of the specified repository.
        values = ("repository","pullRequests")
        params = {
            'owner' : self.owner,
            'repo' : self.repo,
            'values' : values
        }

        pull_request_collection = GraphQlPageCollection(query, self.keyAuth,self.logger,bind=params)

        return pull_request_collection

    def get_pull_requests_reviews_collection(self):
        #Cursor and numRecords is handled by the collection internals
        #totalCount is needed to furfill container class
        #edges has the 'content' of the issues
        query = """
            query($numRecords: Int!, $cursor: String, $owner: String!, $repo: String!) {
                repository(owner:$owner, name:$repo) {
                    pullRequestReviews (first: $numRecords, after:$cursor) {
                        totalCount
                        edges {
                            node {
                                title
                                body
                                closed
                                url
                        
                            }
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        """

        #Values specifies the dictionary values we want to return as the issue collection.
        #e.g. here we get the pullRequests of the specified repository.
        values = ("repository","pullRequests")
        params = {
            'owner' : self.owner,
            'repo' : self.repo,
            'values' : values
        }

        pull_request_collection = GraphQlPageCollection(query, self.keyAuth,self.logger,bind=params)

        return pull_request_collection


class PullRequest():
    def __init__(self, session, owner, repo):

        self.keyAuth = session.oauths
        self.url = "https://api.github.com/graphql"

        self.logger = session.logger

        self.owner = owner
        self.repo = repo