from augur_new.tasks.task_session import *
import asyncio
#from gql import gql, Client
#from gql.transport.aiohttp import AIOHTTPTransport
import httpx
import json
from random import choice
import collections
import time

"""
    Should be designed on a per entity basis that has attributes that call 
    defined graphql queries.

    e.g. create a GHContributor graphql class that represents a contributor in github
    then various attributes call queries on the fly.

    Base level class will be a github repo.


    PR_reviews, events, messages, pr_commits, pr_files(already done convert it)
"""

#Get data extraction logic for nested nodes in return data.

#Should keep track of embedded data that is incomplete.
class GraphQlPageCollection(collections.abc.Sequence):
    #Bind is needed for things like query by repo. Contains bind variables for the graphql query
    def __init__(self,query,keyAuth,logger,bind={},numPerPage=100,url="https://api.github.com/graphql",repaginateIfIncomplete=[]):
        self.per_page = numPerPage
        self.query = query
        self.keyAuth = keyAuth
        self.logger = logger

        self.url = url

        self.page_cache = []

        self.bind = bind

        #things to mark as to repaginate if we can't get them in one query
        self.repaginate = repaginateIfIncomplete
        #dict of ids to query later.
        self.marked_records = {}

        for record in self.repaginate:
            #ids of records should be stored in a set
            self.marked_records[record] = set()

    def mark_for_repagination(self,records):
        #iterate through list of records and check against values specified.
        for record in records:
            for valueToCheck in self.repaginate:
                #get the ids of records that have incomplete sublists.
                if record[valueToCheck]['totalCount'] > len(record[valueToCheck]['edges']):
                    #Store number as most common value github graphql queries by
                    self.marked_records[valueToCheck].add(record['number'])

        

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

        response = responseObject.json()

        if "errors" in response: 
            print(response["errors"])
    
        result_dict = response['data']

        #print(result_dict)
        #extract the core keys that we want from our query
        #core = result_dict[self.bind['values'][0]][self.bind['values'][1]]
        core = result_dict

        for value in self.bind['values']:
            core = core[value]

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

            if self.repaginate:
                self.mark_for_repagination(content) 

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

        content = []
        
        #extract the content from the graphql query result 
        for data in coreData['edges']:
            yield data['node']
            if self.repaginate:
                content.append(data['node'])

        if self.repaginate:
                self.mark_for_repagination(content) 

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

            if self.repaginate:
                self.mark_for_repagination(data_list) 

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
    
    #Get pr reviews from here and mark the ones we can't get all at once.
    def get_pull_requests_collection(self):
        #Cursor and numRecords is handled by the collection internals
        #totalCount is needed to furfill container class
        #edges has the 'content' of the issues
        query = """

            query($repo: String!, $owner: String!, $numRecords: Int!, $cursor: String) {
                repository(name: $repo, owner: $owner) {
                    pullRequests(first: $numRecords, after: $cursor) {
                        totalCount
                        edges {
                            node {
                                body
                                id
                                number
                                title
                                closed
                                bodyHTML
                                bodyText
                                author {
                                    login
                                    url
                                }
                                reviews(first: 10) {
                                    edges {
                                        node {
                                            author {
                                                login
                                                url
                                            }
                                            bodyText
                                            body
                                            bodyHTML
                                            id
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
        #e.g. here we get the pullRequests of the specified repository.
        values = ("repository","pullRequests")
        params = {
            'owner' : self.owner,
            'repo' : self.repo,
            'values' : values
        }

        #specify values to be marked if we can't get them all at once due to rate limits
        #e.g. here we specify to go back and get reviews if we can't get them all at once.

        repaginateIfIncomplete = ['reviews']

        pull_request_collection = GraphQlPageCollection(query, self.keyAuth,self.logger,bind=params,repaginateIfIncomplete=repaginateIfIncomplete)

        return pull_request_collection



class PullRequest():
    def __init__(self, session, owner, repo, number):

        self.keyAuth = session.oauths
        self.url = "https://api.github.com/graphql"

        self.logger = session.logger

        self.owner = owner
        self.repo = repo
        self.number = number

    def get_reviews_collection(self):

        query = """
            query MyQuery($repo: String!, $owner: String!,$number: Int!, $numRecords: Int!, $cursor: String) {
                repository(name: $repo, owner: $owner) {
                    pullRequest(number: $number) {
                        reviews(first: $numRecords, after: $cursor) {
                            edges {
                                node {
                                    author {
                                        login
                                        url
                                    }
                                    body
                                    bodyHTML
                                    bodyText
                                    id
                                    createdAt
                                    url
                                }
                            }
                            totalCount
                            pageInfo {
                                hasNextPage
                                endCursor
                            }
                        }
                    }
                }
            }
            """

        #Values specifies the dictionary values we want to return as the issue collection.
        #e.g. here we get the reviews of the specified repository by pr.
        values = ("repository","pullRequest","reviews")

        params = {
            'owner' : self.owner,
            'repo' : self.repo,
            'number' : self.number,
            'values' : values
        }

        review_collection = GraphQlPageCollection(query, self.keyAuth, self.logger,bind=params)

        return review_collection