from augur.tasks.github.util.github_task_session import *
from typing import List, Optional, Union, Generator, Tuple
#from gql import gql, Client
#from gql.transport.aiohttp import AIOHTTPTransport
import httpx
import json
from random import choice
import collections
import time
import traceback
from augur.tasks.github.util.github_paginator import GithubApiResult, process_dict_response

"""
    Should be designed on a per entity basis that has attributes that call 
    defined graphql queries.

    e.g. create a GHContributor graphql class that represents a contributor in github
    then various attributes call queries on the fly.

    Base level class will be a github repo.


    PR_reviews, events, messages, pr_commits, pr_files(already done convert it)
"""

def hit_api_graphql(keyAuth,url,logger,query,variables={},timeout=40):
    logger.debug(f"Sending query {query}  to github graphql")

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
                url=url,auth=keyAuth,json=json_dict
                )
        
        except TimeoutError:
            logger.info("Request timed out. Sleeping 10 seconds and trying again...\n")
            time.sleep(10)
            return None
        except httpx.TimeoutException:
            logger.info("httpx.ReadTimeout. Sleeping 10 seconds and trying again...\n")
            time.sleep(10)
            return None
        except httpx.NetworkError:
            logger.info(f"Network Error. Sleeping {round(timeout)} seconds and trying again...\n")
            time.sleep(round(timeout))
            return None
        except httpx.ProtocolError:
            logger.info(f"Protocol Error. Sleeping {round(timeout*1.5)} seconds and trying again...\n")
            time.sleep(round(timeout*1.5))
            return None
    
    return response

def request_graphql_dict(session,url,query,variables={},timeout_wait=10):
    attempts = 0
    response_data = None
    success = False
    while attempts < 10:
        #self.logger.info(f"{attempts}")
        try:
            result = hit_api_graphql(session.oauths, url, session.logger, query,variables=variables)
            #self.hit_api(query,variables=variables)
        except TimeoutError:
            session.logger.info(
                f"User data request for enriching contributor data failed with {attempts} attempts! Trying again...")
            time.sleep(timeout_wait)
            continue
        
        if not result:
            attempts += 1
            continue

        try:
            response_data = result.json()
        except:
            response_data = json.loads(json.dumps(result.text))
        
        #self.logger.info(f"api return: {response_data}")

        if type(response_data) == dict:
            err = process_dict_response(session.logger, result, response_data)

            if err and err != GithubApiResult.SUCCESS:
                attempts += 1
                session.logger.info(f"err: {err}")
                continue
            
            success = True
            break
        elif type(response_data) == list:
            session.logger.warning("Wrong type returned, trying again...")
            session.logger.info(f"Returned list: {response_data}")
        elif type(response_data) == str:
            logger.info(
                f"Warning! page_data was string: {response_data}")
            if "<!DOCTYPE html>" in response_data:
                session.logger.info("HTML was returned, trying again...\n")
            elif len(response_data) == 0:
                logger.warning("Empty string, trying again...\n")
            else:
                try:
                    # Sometimes raw text can be converted to a dict
                    response_data = json.loads(response_data)
                    session.logger.info(f"{response_data}")
                    err = process_graphql_dict_response(logger,result,response_data)

                    #If we get an error message that's not None
                    if err and err != GithubApiResult.SUCCESS:
                        continue
                    
                    success = True
                    break
                except:
                    pass
        attempts += 1

    if not success:
        return None

    return response_data



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

    def request_graphql_dict(self,variables={},timeout_wait=10):
        attempts = 0
        response_data = None
        success = False
        while attempts < 10:
            #self.logger.info(f"{attempts}")
            try:
                result = hit_api_graphql(self.keyAuth, self.url, self.logger, self.query,variables=variables)
                #self.hit_api(query,variables=variables)
            except TimeoutError:
                self.logger.info(
                    f"User data request for enriching contributor data failed with {attempts} attempts! Trying again...")
                time.sleep(timeout_wait)
                continue
            
            if not result:
                attempts += 1
                continue

            try:
                response_data = result.json()
            except:
                response_data = json.loads(json.dumps(result.text))
            
            #self.logger.info(f"api return: {response_data}")

            if type(response_data) == dict:
                err = process_dict_response(self.logger, result, response_data)

                if err and err != GithubApiResult.SUCCESS:
                    attempts += 1
                    self.logger.info(f"err: {err}")
                    continue
                
                success = True
                break
            elif type(response_data) == list:
                self.logger.warning("Wrong type returned, trying again...")
                self.logger.info(f"Returned list: {response_data}")
            elif type(response_data) == str:
                logger.info(
                    f"Warning! page_data was string: {response_data}")
                if "<!DOCTYPE html>" in response_data:
                    self.logger.info("HTML was returned, trying again...\n")
                elif len(response_data) == 0:
                    logger.warning("Empty string, trying again...\n")
                else:
                    try:
                        # Sometimes raw text can be converted to a dict
                        response_data = json.loads(response_data)
                        self.logger.info(f"{response_data}")
                        err = process_graphql_dict_response(logger,result,response_data)

                        #If we get an error message that's not None
                        if err and err != GithubApiResult.SUCCESS:
                            continue
                        
                        success = True
                        break
                    except:
                        pass
            attempts += 1

        if not success:
            return None

        return response_data

    def hit_api(self,query,variables={}):
        return hit_api_graphql(self.keyAuth, self.url, self.logger, query,variables=variables)
    

    def extract_paginate_result(self,responseDict):

        if not responseDict:
            raise TimeoutError("No data received from endpoint.")
        #err = process_graphql_dict_response(self.logger, responseObject, response)
        if 'data' not in responseDict:
            self.logger.error(responseDict)
            raise KeyError

        result_dict = responseDict['data']

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
            data = self.request_graphql_dict(variables=params)
            #extract the content from the graphql query result
            coreData = self.extract_paginate_result(data)

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

        #result = self.hit_api(self.query,variables=params)#self.client.execute(self.query,variable_values=params)
        data = self.request_graphql_dict(variables=params)
        coreData = self.extract_paginate_result(data)

        totalCount = int(coreData['totalCount'])

        return totalCount
    
    def __iter__(self):
        params = {
            "numRecords" : self.per_page,
            "cursor"    : None
        }
        params.update(self.bind)

        #result = self.hit_api(self.query,variables=params)#self.client.execute(self.query,variable_values=params)
        #self.logger.info(f"{params}")
        data = self.request_graphql_dict(variables=params)
        try:
            coreData = self.extract_paginate_result(data)
        except KeyError as e:
            self.logger.error("Could not extract paginate result because there was no data returned")
            self.logger.error(
                ''.join(traceback.format_exception(None, e, e.__traceback__)))
            
            data = self.request_graphql_dict(variables=params)
            coreData = self.extract_paginate_result(data)


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

            try:
                data = self.request_graphql_dict(variables=params)#self.client.execute(self.query,variable_values=params)
            except Exception as e:
                self.logger.error("Could not extract paginate result because there was no data returned")
                self.logger.error(
                    ''.join(traceback.format_exception(None, e, e.__traceback__)))
                
                self.logger.info(f"Trying again...")
                data = self.request_graphql_dict(variables=params)

            coreData = self.extract_paginate_result(data)

            #print(coreData)
            if len(coreData['edges']) == 0:
                return
            
            for data in coreData['edges']:
                yield data['node']


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