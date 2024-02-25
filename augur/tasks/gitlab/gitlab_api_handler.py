"""
Defines a GitlabApiHandler class to paginate and handle interaction with GitLab's
api through automatic use of relevant key auth and pagination tools. 
"""
import httpx
import time
import logging

from typing import List, Optional, Generator, Tuple
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from enum import Enum

from augur.tasks.gitlab.gitlab_random_key_auth import GitlabRandomKeyAuth
from augur.tasks.github.util.util import parse_json_response

class GitlabApiResult(Enum):
    """All the different results of querying the Gitlab API."""

    SUCCESS = 0
    TIMEOUT = 1
    NO_MORE_ATTEMPTS = 2
    NOT_FOUND = 3
    SECONDARY_RATE_LIMIT = 4
    RATE_LIMIT_EXCEEDED = 5
    ABUSE_MECHANISM_TRIGGERED = 6
    # TODO: Add bad credentials detection that removes key 
    # from redis if bad credentials are detected
    BAD_CREDENTIALS = 7

class GitlabApiHandler():
    """This class is a sequence that handles retrieving data from the Gitlab API.

    Attributes:
        url (str): The url that we are collecting data
        key_mangager (GitlabRandomKeyAuth): Custom httpx auth class 
                that randomizes the github api key a request gets. 
                This is how the requests are getting their api keys
        logger (logging.Logger): Logger that handler printing information to files and stdout
    """

    def __init__(self, key_manager: GitlabRandomKeyAuth, logger: logging.Logger):
        """Initialize the class GitlabPaginator.

        Args:
            url: url that the data is being collected
            key_manager: class that randomly selects a Gitlab API key for each request
            logger: handles logging
            from_datetime: collects data after this datatime (not yet implemented)
            to_datetime: collects data before this datatime (not yet implemented)
        """
        self.key_manager = key_manager
        self.logger = logger

    def get_length(self, url):
        """Get the length of the Gitlab API data.

        Returns:
            The length of the Gitlab API data at the url.
        
        Examples:
            This function is called when len() is called on the GitlabPaginator class for example.

            issues = GitlabPaginator(url, session.oauths, logger)
            issue_len = len(issues)
        """

        num_pages = self.get_num_pages(url)

        self.logger.info(f"Num pages: {num_pages}")

        params = {"page": num_pages}
        url = add_query_params(url, params)

        # get the amount of data on last page
        data, _, result = self.retrieve_data(url)

        if result == GitlabApiResult.SUCCESS:  
            return (100 * (num_pages -1)) + len(data)

        self.logger.debug("Unable to retrieve data length from api")
        return 0

    def iter(self, url) -> Generator[Optional[dict], None, None]:
        """Provide data from Gitlab API via a generator that yields one dict at a time.

        Yields:
            A piece of data from the github api as the specified url
        """

        url = self._set_paginaton_query_params(url)

        data_list, response, result = self.retrieve_data(url)

        if result != GitlabApiResult.SUCCESS:
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

            if result != GitlabApiResult.SUCCESS:
                self.logger.debug("Failed to retrieve the data even though 10 attempts were given")
                return

            for data in data_list:
                yield data

    def iter_pages(self, url) -> Generator[Tuple[Optional[List[dict]], int], None, None]:
        """Provide data from Gitlab API via a generator that yields a page of dicts at a time.

        Returns:
            A page of data from the Gitlab API at the specified url
        """
        
        url = self._set_paginaton_query_params(url)
        
        # retrieves the data for the given url
        data_list, response, result = self.retrieve_data(url)

        if result != GitlabApiResult.SUCCESS:
            self.logger.debug("Failed to retrieve the data even though 10 attempts were given")
            yield None, None
            return

        # this retrieves the page for the given url
        page_number = get_url_page_number(url)

        # yields the first page of data and its page number
        yield data_list, page_number

        while 'next' in response.links.keys():

            # gets the next page from the last responses header
            next_page = response.links['next']['url']

            # Here we don't need to pass in params with the page, or the default params because the url from the headers already has those values
            data_list, response, result = self.retrieve_data(next_page)

            if result != GitlabApiResult.SUCCESS:
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

            num_attempts += 1

            if response is None:
                if timeout_count == 10:
                    self.logger.error(f"Request timed out 10 times for {url}")
                    return None, None, GitlabApiResult.TIMEOUT

                timeout = timeout * 1.1
                num_attempts += 1
                continue

            if response.status_code == 500:
                self.logger.error(f"Gitlab returned {response.status_code} error when fetching {url}. Message: {response.json()}")
                continue

            if response.status_code == 429:

                current_epoch = int(time.time())
                epoch_when_key_resets = int(response.headers["ratelimit-reset"])
                key_reset_time =  epoch_when_key_resets - current_epoch
                
                if key_reset_time < 0:
                    self.logger.error(f"Key reset time was less than 0 setting it to 0.\nThe current epoch is {current_epoch} and the epoch that the key resets at is {epoch_when_key_resets}")
                    key_reset_time = 0
                    
                self.logger.info(f"\n\n\nGitlab API rate limit exceeded. Sleeping until the key resets ({key_reset_time} seconds)")
                time.sleep(key_reset_time)
                continue

            if response.status_code == 404:
                self.logger.info(f"ERROR: 404 not found for {url}")
                return [], response, GitlabApiResult.NOT_FOUND

            if response.status_code == 204:
                return [], response, GitlabApiResult.SUCCESS
                
            if response.status_code >= 200 and response.status_code <=299:

                page_data = parse_json_response(self.logger, response)
                return page_data, response, GitlabApiResult.SUCCESS
            
            self.logger.warning(f"Unhandled gitlab response. Status code: {response.status_code}. Body: {response.json()}")

            

        self.logger.error("Unable to collect data in 10 attempts")
        return None, None, GitlabApiResult.NO_MORE_ATTEMPTS

    def get_num_pages(self, url) -> Optional[int]:
        """Get the number of pages of data that a url can paginate through.

        Returns:
            The number of pages a url can access
        """
        
        url = self._set_paginaton_query_params(url)
        
        timeout: float = 5
        num_attempts = 0
        while num_attempts < 10:
            r = self.hit_api(url=url, timeout=timeout, method="HEAD")

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

    def hit_api(self, url, timeout, method):
        """Attempt to retrieve data at given url.

        Args:
            url: The url to retrieve the data from
            timeout: time to wait until timeout
            method: GET, POST, etc. 

        Returns
            The response object from hitting the url and the data on the page
        """

        return hit_api(self.key_manager, url, self.logger, timeout, method=method) 

    def _set_paginaton_query_params(self, url):

        remove_fields = ["per_page", "page"]
        url = clean_url(url, remove_fields)

        # we need to add query params directly to the url, instead of passing the param to the httpx.Client.request
        # this is because github will only append specified params to the links in the headers if they are a part
        # of the url, and not the params with the request
        params = {"per_page": 100}
        url = add_query_params(url, params)

        return url

################################################################################

# Url Helper Method to remove query parameters from the url
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
        additional_params: key value pairs specifying the parameters to be added

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

################################################################################

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
