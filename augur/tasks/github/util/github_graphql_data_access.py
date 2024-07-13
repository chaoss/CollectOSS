import logging
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception, RetryError

URL = "https://api.github.com/graphql"

class RatelimitException(Exception):

    def __init__(self, response, message="Github Rate limit exceeded") -> None:

        self.response = response

        super().__init__(message)

class UrlNotFoundException(Exception):
    pass

class GithubGraphQlDataAccess:
    

    def __init__(self, key_manager, logger: logging.Logger):
    
        self.logger = logger
        self.key_manager = key_manager

    def get_resource(self, query, variables, result_keys):

        result_json = self.make_request_with_retries(query, variables).json()

        data = self.__extract_data_section(result_keys, result_json)
        
        return self.__extract_raw_data_into_list(data)   
    

    def paginate_resource(self, query, variables, result_keys):

        params = {
            "numRecords" : 100,
            "cursor"    : None
        }
        params.update(variables)

        result_json = self.make_request_with_retries(query, params).json()

        data = self.__extract_data_section(result_keys, result_json)

        if self.__get_total_count(data) == 0:
            return
        
        yield from self.__extract_raw_data_into_list(data) 
                        
        while self.__has_next_page():
            params["cursor"] = self.__get_next_page_cursor(data)

            result_json = self.make_request_with_retries(query, params).json()
            
            data = self.__extract_data_section(result_keys, result_json)

            yield from self.__extract_raw_data_into_list(data)

    def make_request(self, query, variables, timeout=40):

        with httpx.Client() as client:

            json_dict = {
                'query' : query
            }

            if variables:
                json_dict['variables'] = variables
            
            response = client.post(url=URL,auth=self.key_manager,json=json_dict, timeout=timeout)

        if response.status_code in [403, 429]:
            raise RatelimitException(response)

        if response.status_code == 404:
            raise UrlNotFoundException(f"404 for {self.url} with query of {query}")

        response.raise_for_status()

        return response
        
        
    def make_request_with_retries(self, query, variables, timeout=100):
        """ What method does?
            1. Catches RetryError and rethrows a nicely formatted OutOfRetriesException that includes that last exception thrown
        """

        try:
            return self.__make_request_with_retries(query, variables, timeout)
        except RetryError as e:
            raise e.last_attempt.exception()
        
    @retry(stop=stop_after_attempt(10), wait=wait_fixed(5), retry=retry_if_exception(lambda exc: not isinstance(exc, UrlNotFoundException)))
    def __make_request_with_retries(self, query, variables, timeout=40):
        """ What method does?
            1. Retires 10 times
            2. Waits 5 seconds between retires
            3. Does not rety UrlNotFoundException
            4. Catches RatelimitException and waits before raising exception
        """

        try:
            return self.make_request(query, variables, timeout)
        except RatelimitException as e:
            self.__handle_github_ratelimit_response(e.response)
            raise e
        
    def __handle_github_ratelimit_response(self, response):

        headers = response.headers

        if "Retry-After" in headers:

            retry_after = int(headers["Retry-After"])
            self.logger.info(
                f'\n\n\n\nSleeping for {retry_after} seconds due to secondary rate limit issue.\n\n\n\n')
            time.sleep(retry_after)

        elif "X-RateLimit-Remaining" in headers and int(headers["X-RateLimit-Remaining"]) == 0:
            current_epoch = int(time.time())
            epoch_when_key_resets = int(headers["X-RateLimit-Reset"])
            key_reset_time =  epoch_when_key_resets - current_epoch
            
            if key_reset_time < 0:
                self.logger.error(f"Key reset time was less than 0 setting it to 0.\nThe current epoch is {current_epoch} and the epoch that the key resets at is {epoch_when_key_resets}")
                key_reset_time = 0
                
            self.logger.info(f"\n\n\nAPI rate limit exceeded. Sleeping until the key resets ({key_reset_time} seconds)")
            time.sleep(key_reset_time)
        else:
            time.sleep(60)
        
    def __extract_data_section(self, keys, json_response):

        if not json_response or not json_response.strip():
            raise Exception(f"Empty data returned. Data: {json_response}")
        
        if 'data' not in json_response:
            raise Exception(f"Error: 'data' key missing from response. Response: {json_response}")

        core = json_response['data']

        # iterate deeper into the json_response object until we get to the desired data
        for value in keys:
            core = core[value]

        return core

    def __extract_raw_data_into_list(self, data):

        if 'edges' not in data:
            raise Exception(f"Error: 'edges' key not present in data. Data {data}")
        
        data_list = []
        for edge in data['edges']:

            if 'node' not in edge:
                raise Exception(f"Error: 'node' key not present in data. Data {data}")
            
            data_list.append(data['node'])
            
        return data_list
    
    def __has_next_page(data):

        if 'pageInfo' not in data:
            raise Exception(f"Error: 'pageInfo' key not present in data. Data {data}")
        
        if 'hasNextPage' not in data['pageInfo']:
            raise Exception(f"Error: 'hasNextPage' key not present in data. Data {data}")
        
        if not isinstance(data['pageInfo']['hasNextPage'], bool):
            raise Exception(f"Error: pageInfo.hasNextPage is not a bool. Data {data}")

        return data['pageInfo']['hasNextPage']
    
    def __get_next_page_cursor(data):

        if 'pageInfo' not in data:
            raise Exception(f"Error: 'pageInfo' key not present in data. Data {data}")
        
        if 'endCursor' not in data['pageInfo']:
            raise Exception(f"Error: 'endCursor' key not present in data. Data {data}")

        return data['pageInfo']['endCursor']
    
    def __get_total_count(data):

        if 'totalCount' not in data:
            raise Exception(f"Error: totalCount key not found in data. Data: {data}")
        
        if not data["totalCount"]:
            raise Exception(f"Error: totalCount is null. Data: {data}")
        
        try:
            return int(data["totalCount"])
        except ValueError:
            raise Exception(f"Error: totalCount is not an integer. Data: {data}")



        








