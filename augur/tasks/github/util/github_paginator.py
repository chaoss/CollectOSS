"""Logic to paginate the Github API."""

import collections
import httpx
import time
import json
import asyncio
import datetime
import logging


from typing import List, Optional, Union, Generator, Tuple
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from enum import Enum


from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.tasks.github.util.util import parse_json_response

 
def hit_api(key_manager, url: str, logger: logging.Logger, timeout: float = 10, method: str = 'GET', ) -> Optional[httpx.Response]:
    """Ping the api and get the data back for the page.

    Returns:
        A httpx response that contains the data. None if a timeout occurs
    """
    # self.logger.info(f"Hitting endpoint with {method} request: {url}...\n")

    with httpx.Client() as client:

        try:
            response = client.request(
                method=method, url=url, auth=key_manager, timeout=timeout, follow_redirects=True)

        except TimeoutError:
            logger.info(f"Request timed out. Sleeping {round(timeout)} seconds and trying again...\n")
            time.sleep(round(timeout))
            return None
        except httpx.TimeoutException:
            logger.info(f"Request timed out. Sleeping {round(timeout)} seconds and trying again...\n")
            time.sleep(round(timeout))
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


def process_dict_response(logger: logging.Logger, response: httpx.Response, page_data: dict) -> Optional[str]:
    """Process dict response from the api and return the status.

    Args:
        logger: handles logging
        response: used to access the url of the request and the headers
        page_data: dict response from the api

    Returns:
        A string explaining what happened is returned if what happened is determined, otherwise None is returned.
    """
    #logger.info("Request returned a dict: {}\n".format(page_data))

    if 'message' not in page_data.keys():
        return GithubApiResult.SUCCESS

    if page_data['message'] == "Not Found":
        logger.error(
            "Github repo was not found or does not exist for endpoint: "
            f"{response.url}"
        )
        return GithubApiResult.REPO_NOT_FOUND

    if "You have exceeded a secondary rate limit. Please wait a few minutes before you try again" in page_data['message']:

        # sleeps for the specified amount of time that github says to retry after
        retry_after = int(response.headers["Retry-After"])
        logger.info(
            f'\n\n\n\nSleeping for {retry_after} seconds due to secondary rate limit issue.\n\n\n\n')
        time.sleep(retry_after)

        return GithubApiResult.SECONDARY_RATE_LIMIT
        # return "do_not_increase_attempts"
    
    if "API rate limit exceeded for user" in page_data['message']:

        current_epoch = int(time.time())
        epoch_when_key_resets = int(response.headers["X-RateLimit-Reset"])
        key_reset_time =  epoch_when_key_resets - current_epoch
        
        if key_reset_time < 0:
            logger.error(f"Key reset time was less than 0 setting it to 0.\nThe current epoch is {current_epoch} and the epoch that the key resets at is {epoch_when_key_resets}")
            key_reset_time = 0
            
        logger.info(f"\n\n\nAPI rate limit exceeded. Sleeping until the key resets ({key_reset_time} seconds)")
        time.sleep(key_reset_time)

        return GithubApiResult.RATE_LIMIT_EXCEEDED

    if "You have triggered an abuse detection mechanism." in page_data['message']:
        # self.update_rate_limit(response, temporarily_disable=True,platform=platform)
        

        # sleeps for the specified amount of time that github says to retry after
        retry_after = int(response.headers["Retry-After"])
        logger.info(f"Abuse mechanism detected sleeping for {retry_after} seconds")
        time.sleep(retry_after)

        return GithubApiResult.ABUSE_MECHANISM_TRIGGERED

    if page_data['message'] == "Bad credentials":
        logger.error("\n\n\n\n\n\n\n Bad Token Detected \n\n\n\n\n\n\n")
        # self.update_rate_limit(response, bad_credentials=True, platform=platform)
        return GithubApiResult.BAD_CREDENTIALS
    
    return GithubApiResult.NEW_RESULT

class GithubApiResult(Enum):
    """All the different results of querying the Github API."""

    NEW_RESULT = -1
    SUCCESS = 0
    TIMEOUT = 1
    NO_MORE_ATTEMPTS = 2
    REPO_NOT_FOUND = 3
    SECONDARY_RATE_LIMIT = 4
    RATE_LIMIT_EXCEEDED = 5
    ABUSE_MECHANISM_TRIGGERED = 6
    BAD_CREDENTIALS = 7
    HTML = 8
    EMPTY_STRING = 9
 

class GithubPaginator(collections.abc.Sequence):
    """This class is a sequence that handles paginating through data on the Github API.

    Attributes:
        url (str): The url that we are collecting data
        key_mangager (GithubRandomKeyAuth): Custom httpx auth class 
                that randomizes the github api key a request gets. 
                This is how the requests are getting their api keys
        logger (logging.Logger): Logger that handler printing information to files and stdout
    """

    def __init__(self, url: str, key_manager: GithubRandomKeyAuth, logger: logging.Logger, from_datetime=None, to_datetime=None):
        """Initialize the class GithubPaginator.

        Args:
            url: url that the data is being collected
            key_manager: class that randomly selects a Github API key for each request
            logger: handles logging
            from_datetime: collects data after this datatime (not yet implemented)
            to_datetime: collects data before this datatime (not yet implemented)
        """
        remove_fields = ["per_page", "page"]
        url = clean_url(url, remove_fields)

        # we need to add query params directly to the url, instead of passing the param to the httpx.Client.request
        # this is because github will only append specified params to the links in the headers if they are a part
        # of the url, and not the params with the request
        params = {"per_page": 100}
        url = add_query_params(url, params)

        self.url = url
        self.key_manager = key_manager
        self.logger = logger

        # get the logger from the key manager
        # self.logger = key_manager.logger

        self.from_datetime = from_datetime
        self.to_datetime = to_datetime

    def __getitem__(self, index: int) -> Optional[dict]:
        """Get the value at index of the Github API data returned from the url.

        Args:
            index: The index of the desired data from the Github API

        Returns:
            The value at the index
        """
        # if isinstance(index, slice) is True:

        #     data_slice = index
        #     start = data_slice.start
        #     stop = data_slice.stop
        #     step = data_slice.step

        #     first_item_page = (start // 100) + 1
        #     end_item_page = (stop // 100) + 1

        #     all_data: List[dict] = []

        #     for page_number in range(first_item_page, end_item_page+1):

        #         # create url to query
        #         params = {"page": items_page}
        #         url = add_query_params(self.url, params)

        #         data, _ = self.retrieve_data(url)

        #         all_data += data

        #     first_page_index = start % 100

        #     needed_data = []
        #     for index in range(start, stop, step):
        #         needed_data.append(all_data[index])

        #     return needed_data

                
        # get the page the item is on
        items_page = (index // 100) + 1

        # create url to query
        params = {"page": items_page}
        url = add_query_params(self.url, params)

        data, _, result = self.retrieve_data(url)

        if result != GithubApiResult.SUCCESS:
            self.logger.debug("Unable to get item from the api")
            return None

        # get the position of data on the page
        page_index = index % 100

        try:
            return data[page_index]
        except KeyError as e:
            raise KeyError("Data does not exists for that index") from e

    def __len__(self):
        """Get the length of the Github API data.

        Returns:
            The length of the Github API data at the url.
        
        Examples:
            This function is called when len() is called on the GithubPaginator class for example.

            issues = GithubPaginator(url, session.oauths, logger)
            issue_len = len(issues)
        """

        num_pages = self.get_num_pages()

        self.logger.info(f"Num pages: {num_pages}")

        params = {"page": num_pages}
        url = add_query_params(self.url, params)

        # get the amount of data on last page
        data, _, result = self.retrieve_data(url)

        if result == GithubApiResult.SUCCESS:  
            return (100 * (num_pages -1)) + len(data)

        self.logger.debug("Unable to retrieve data length from api")
        return 0

    def __iter__(self) -> Generator[Optional[dict], None, None]:
        """Provide data from Github API via a generator that yields one dict at a time.

        Yields:
            A piece of data from the github api as the specified url
        """
        data_list, response, result = self.retrieve_data(self.url)

        if result != GithubApiResult.SUCCESS:
            self.logger.debug("Failed to retrieve the data even though 10 attempts were given")
            yield None
            return

        # yield the first page data
        for data in data_list:
            yield data

        while 'next' in response.links.keys():
            next_page = response.links['next']['url']

            # Here we don't need to pass in params with the page, or the default params because the url from the headers already has those values
            data_list, response, result = self.retrieve_data(next_page)

            if result != GithubApiResult.SUCCESS:
                self.logger.debug("Failed to retrieve the data even though 10 attempts were given")
                return

            for data in data_list:
                yield data

    def iter_pages(self) -> Generator[Tuple[Optional[List[dict]], int], None, None]:
        """Provide data from Github API via a generator that yields a page of dicts at a time.

        Returns:
            A page of data from the Github API at the specified url
        """
        # retrieves the data for the given url
        data_list, response, result = self.retrieve_data(self.url)

        if result != GithubApiResult.SUCCESS:
            self.logger.debug("Failed to retrieve the data even though 10 attempts were given")
            yield None, None
            return

        # this retrieves the page for the given url
        page_number = get_url_page_number(self.url)

        # yields the first page of data and its page number
        yield data_list, page_number

        while 'next' in response.links.keys():

            # gets the next page from the last responses header
            next_page = response.links['next']['url']

            # Here we don't need to pass in params with the page, or the default params because the url from the headers already has those values
            data_list, response, result = self.retrieve_data(next_page)

            if result != GithubApiResult.SUCCESS:
                self.logger.debug(f"Failed to retrieve the data for even though 10 attempts were given. Url: {next_page}")
                return

            page_number = get_url_page_number(next_page)

            # if either the data or response is None then yield None and return
            if data_list is None or response is None:
                return

            # yield the data from the page and its number
            yield data_list, page_number

    def retrieve_data(self, url: str) -> Tuple[Optional[List[dict]], Optional[httpx.Response]]:
        """Attempt to retrieve data at given url.

        Args:
            url: The url to retrieve the data from

        Returns
            The response object from hitting the url and the data on the page
        """
        timeout = 30
        timeout_count = 0
        num_attempts = 1
        while num_attempts <= 10:

            response = hit_api(self.key_manager, url, self.logger, timeout)

            if response is None:
                if timeout_count == 10:
                    self.logger.error(f"Request timed out 10 times for {url}")
                    return None, None, GithubApiResult.TIMEOUT

                timeout = timeout * 1.1
                num_attempts += 1
                continue
            
            
            page_data = parse_json_response(self.logger, response)


            # if the data is a list, then return it and the response
            if isinstance(page_data, list) is True:
                return page_data, response, GithubApiResult.SUCCESS

            # if the data is a dict then call process_dict_response, and 
            if isinstance(page_data, dict) is True:
                dict_processing_result = process_dict_response(self.logger, response, page_data)

                if dict_processing_result == GithubApiResult.NEW_RESULT:
                    self.logger.info(f"Encountered new dict response from api on url: {url}. Response: {page_data}")
                    return None, None, GithubApiResult.NEW_RESULT

                if dict_processing_result == GithubApiResult.REPO_NOT_FOUND:
                    return None, response, GithubApiResult.REPO_NOT_FOUND

                if dict_processing_result in (GithubApiResult.SECONDARY_RATE_LIMIT, GithubApiResult.ABUSE_MECHANISM_TRIGGERED):
                    continue

                if dict_processing_result == GithubApiResult.RATE_LIMIT_EXCEEDED:
                    num_attempts = 0
                    continue                    

            if isinstance(page_data, str) is True:
                str_processing_result: Union[str, List[dict]] = self.process_str_response(page_data)

                if isinstance(str_processing_result, list):
                    return str_processing_result, response, GithubApiResult.SUCCESS

            num_attempts += 1

        self.logger.error("Unable to collect data in 10 attempts")
        return None, None, GithubApiResult.NO_MORE_ATTEMPTS

    def get_num_pages(self) -> Optional[int]:
        """Get the number of pages of data that a url can paginate through.

        Returns:
            The number of pages a url can access
        """
        timeout: float = 5
        num_attempts = 0
        while num_attempts < 10:
            r = hit_api(self.key_manager, self.url, self.logger, timeout=timeout, method="HEAD")

            if r:
                break

            timeout = timeout * 1.2
        else:
            raise RuntimeError("Unable to get the number of pages of data in 10 attempts")

        if 'last' not in r.links.keys():
            return 1
        
        # get the last url from header
        last_page_url = r.links['last']['url']

        parsed_url = urlparse(last_page_url)
        try:
            num_pages = int(parse_qs(parsed_url.query)['page'][0])
        except (KeyError, ValueError):
            return None

        return num_pages

    def hit_api(self, url, timeout):

        return hit_api(self.key_manager, url, self.logger, timeout) 


###################################################

    def process_str_response(self, page_data: str) -> Union[str, List[dict]]:
        """Process an api response of type string.

        Args:
            page_data: the string response from the api that is being processed

        Returns:
            html_response, empty_string, and failed_to_parse_jsonif the data is not processable. 
                Or a list of dicts if the json was parasable
        """
        self.logger.info(f"Warning! page_data was string: {page_data}\n")
        
        if "<!DOCTYPE html>" in page_data:
            self.logger.info("HTML was returned, trying again...\n")
            return GithubApiResult.HTML

        if not page_data:
            self.logger.info("Empty string, trying again...\n")
            return GithubApiResult.EMPTY_STRING

        try:
            list_of_dict_page_data = json.loads(page_data)
            return list_of_dict_page_data
        except TypeError:
            return "failed_to_parse_json"


################################################################################

# Url Helper Method to remove query paramaters from the url
def clean_url(url: str, keys: List[str]) -> str:
    """Remove query params from url.

    Args:
        url: the url that is being modified
        keys: the query params that are being removed
        
    Returns:
        A url with the params in keys removed
    """
    u = urlparse(url)
    query = parse_qs(u.query, keep_blank_values=True)

    for key in keys:
        query.pop(key, None)

    u = u._replace(query=urlencode(query, True))
    
    return urlunparse(u)


def add_query_params(url: str, additional_params: dict) -> str:
    """Add query params to a url.

    Args:
        url: the url that is being modified
        additional_params: key value pairs specififying the paramaters to be added

    Returns:
        The url with the key value pairs in additional_params added as query params
    """
    url_components = urlparse(url)
    original_params = parse_qs(url_components.query)
    # Before Python 3.5 you could update original_params with
    # additional_params, but here all the variables are immutable.
    merged_params = {**original_params, **additional_params}
    updated_query = urlencode(merged_params, doseq=True)
    # _replace() is how you can create a new NamedTuple with a changed field
    return url_components._replace(query=updated_query).geturl()



################################################################################


def get_url_page_number(url: str) -> int:
    """Parse the page number from the url.

    Note:
        If the url does not contain a page number the function returns 1
    
    Args:
        url: url to get the page number from 
    
    Returns:
        The page number that the url contains
    """
    parsed_url = urlparse(url)
    try:
        # if page is not a url query param then this is page 1
        page_number = int(parse_qs(parsed_url.query)['page'][0])
    
    except KeyError:
        return 1

    return page_number