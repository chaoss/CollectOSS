"""Logic to paginate the Github API."""

import collections
import httpx
import time
import json
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

    message = page_data.get('message')
    errors = page_data.get('errors')

    if not message and not errors:
        return GithubApiResult.SUCCESS

    if message == "Not Found":
        logger.error(
            "Github repo was not found or does not exist for endpoint: "
            f"{response.url}"
        )
        return GithubApiResult.REPO_NOT_FOUND

    if message and "You have exceeded a secondary rate limit. Please wait a few minutes before you try again" in message:

        # sleeps for the specified amount of time that github says to retry after
        retry_after = int(response.headers["Retry-After"])
        logger.info(
            f'\n\n\n\nSleeping for {retry_after} seconds due to secondary rate limit issue.\n\n\n\n')
        time.sleep(retry_after)

        return GithubApiResult.SECONDARY_RATE_LIMIT
        # return "do_not_increase_attempts"
    
    if message and "API rate limit exceeded for user" in message:

        current_epoch = int(time.time())
        epoch_when_key_resets = int(response.headers["X-RateLimit-Reset"])
        key_reset_time =  epoch_when_key_resets - current_epoch
        
        if key_reset_time < 0:
            logger.error(f"Key reset time was less than 0 setting it to 0.\nThe current epoch is {current_epoch} and the epoch that the key resets at is {epoch_when_key_resets}")
            key_reset_time = 0
            
        logger.info(f"\n\n\nAPI rate limit exceeded. Sleeping until the key resets ({key_reset_time} seconds)")
        time.sleep(key_reset_time)

        return GithubApiResult.RATE_LIMIT_EXCEEDED

    if message and "You have triggered an abuse detection mechanism." in message:
        # self.update_rate_limit(response, temporarily_disable=True,platform=platform)
        

        # sleeps for the specified amount of time that github says to retry after
        retry_after = int(response.headers["Retry-After"])
        logger.info(f"Abuse mechanism detected sleeping for {retry_after} seconds")
        time.sleep(retry_after)

        return GithubApiResult.ABUSE_MECHANISM_TRIGGERED

    if message == "Bad credentials":
        logger.error("\n\n\n\n\n\n\n Bad Token Detected \n\n\n\n\n\n\n")
        # self.update_rate_limit(response, bad_credentials=True, platform=platform)
        return GithubApiResult.BAD_CREDENTIALS
    
    if errors:
        for error in errors:
            if "API rate limit exceeded for user" in error['message']:
                current_epoch = int(time.time())
                epoch_when_key_resets = int(response.headers["X-RateLimit-Reset"])
                key_reset_time =  epoch_when_key_resets - current_epoch
                
                if key_reset_time < 0:
                    logger.error(f"Key reset time was less than 0 setting it to 0.\nThe current epoch is {current_epoch} and the epoch that the key resets at is {epoch_when_key_resets}")
                    key_reset_time = 0
                    
                logger.info(f"\n\n\nAPI rate limit exceeded. Sleeping until the key resets ({key_reset_time} seconds)")
                time.sleep(key_reset_time)
                return GithubApiResult.RATE_LIMIT_EXCEEDED
            
            err_type = error.get('type')

            if err_type and 'NOT_FOUND' in err_type:
                return GithubApiResult.REPO_NOT_FOUND


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
    # TODO: Add bad credentials detection that removes key 
    # from redis if bad credentials are detected
    BAD_CREDENTIALS = 7
    HTML = 8
    EMPTY_STRING = 9


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


def retrieve_dict_from_endpoint(logger, key_auth, url, timeout_wait=10) -> Tuple[Optional[dict], GithubApiResult]:
    timeout = timeout_wait
    timeout_count = 0
    num_attempts = 1

    while num_attempts <= 10:

        response = hit_api(key_auth, url, logger, timeout)

        if response is None:
            if timeout_count == 10:
                logger.error(f"Request timed out 10 times for {url}")
                return None, GithubApiResult.TIMEOUT

            timeout = timeout * 1.1
            num_attempts += 1
            continue
        
        
        page_data = parse_json_response(logger, response)

        if isinstance(page_data, str):
            # TODO: Define process_str_response as outside the class and fix this reference
            str_processing_result: Union[str, List[dict]] = process_str_response(logger,page_data)

            if isinstance(str_processing_result, dict):
                #return str_processing_result, response, GithubApiResult.SUCCESS
                page_data = str_processing_result
            else:
                num_attempts += 1
                continue

        # if the data is a list, then return it and the response
        if isinstance(page_data, list):
            logger.warning("Wrong type returned, trying again...")
            logger.info(f"Returned list: {page_data}")

        # if the data is a dict then call process_dict_response, and 
        elif isinstance(page_data, dict):
            dict_processing_result = process_dict_response(logger, response, page_data)

            if dict_processing_result == GithubApiResult.SUCCESS:
                return page_data, dict_processing_result
            if dict_processing_result == GithubApiResult.NEW_RESULT:
                logger.info(f"Encountered new dict response from api on url: {url}. Response: {page_data}")
                return None, GithubApiResult.NEW_RESULT

            if dict_processing_result == GithubApiResult.REPO_NOT_FOUND:
                return None, GithubApiResult.REPO_NOT_FOUND

            if dict_processing_result in (GithubApiResult.SECONDARY_RATE_LIMIT, GithubApiResult.ABUSE_MECHANISM_TRIGGERED):
                continue

            if dict_processing_result == GithubApiResult.RATE_LIMIT_EXCEEDED:
                num_attempts = 0
                continue                    

        

        num_attempts += 1

    logger.error("Unable to collect data in 10 attempts")
    return None, GithubApiResult.NO_MORE_ATTEMPTS
