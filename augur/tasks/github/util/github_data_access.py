import logging
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception, RetryError
from urllib.parse import urlparse, parse_qs


class RatelimitException(Exception):
    pass

class UrlNotFoundException(Exception):
    pass

class GithubDataAccess:

    def __init__(self, key_manager, logger: logging.Logger):
    
        self.logger = logger
        self.key_manager = key_manager

    def paginate_resource(self, url):

        response = self.make_request_with_retries(url)
        data = response.json()
        if not isinstance(data, list):
            raise Exception(f"GithubApiHandler.paginate_resource must be used with url that returns a list. Use GithubApiHandler.get_resource to retrieve data that is not paginated. The url of {url} returned a {type(data)}.")

        yield data

        while 'next' in response.links.keys():

            next_page = response.links['next']['url']

            response = self.make_request_with_retries(next_page)
            data = response.json()
            if not isinstance(data, list):
                raise Exception(f"GithubApiHandler.paginate_resource must be used with url that returns a list. Use GithubApiHandler.get_resource to retrieve data that is not paginated. The url of {url} returned a {type(data)}. ")

            yield data

        return 
    
    def is_pagination_limited_by_max_github_pages(self, url):
        
        page_count = self.get_resource_page_count(url)

        return page_count <= 299
    
    def get_resource_page_count(self, url):

        response = self.make_request_with_retries(url, method="HEAD")

        if 'last' not in response.links.keys():
            return 1
        
        try:
            last_page_url = response.links['last']['url']

            parsed_url = urlparse(last_page_url)
        
            return int(parse_qs(parsed_url.query)['page'][0])
        except (KeyError, ValueError):
            raise Exception(f"Unable to parse 'last' url from response: {response.links['last']}")

    def get_resource(self, url):

        response = self.make_request_with_retries(url)

        return response.json()  
    
    # TODO: Handle timeout exceptions better
    def make_request(self, url, method="GET", timeout=100):

        with httpx.Client() as client:

            response = client.request(method=method, url=url, timeout=timeout, follow_redirects=True)

            if response.status_code in [403, 429]:
                raise RatelimitException()

            elif response.status_code == 404:
                raise UrlNotFoundException(f"Could not find {url}")
            
            response.raise_for_status()

            return response
        
    def make_request_with_retries(self, url, method="GET", timeout=100):
        """ What method does?
            1. Catches RetryError and rethrows a nicely formatted OutOfRetriesException that includes that last exception thrown
        """

        try:
            return self.__make_request_with_retries(url, method, timeout)
        except RetryError as e:
            raise e.last_attempt.exception()
        
    @retry(stop=stop_after_attempt(10), wait=wait_fixed(5), retry=retry_if_exception(lambda exc: not isinstance(exc, UrlNotFoundException)))
    def __make_request_with_retries(self, url, method="GET", timeout=100):
        """ What method does?
            1. Retires 10 times
            2. Waits 5 seconds between retires
            3. Does not rety UrlNotFoundException
            4. Catches RatelimitException and waits before raising exception
        """

        try:
            return self.make_request(url, method, timeout)
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

        








