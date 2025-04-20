import logging
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception, RetryError
from urllib.parse import urlparse, parse_qs, urlencode
from keyman.KeyClient import KeyClient

GITLAB_RATELIMIT_REMAINING_CAP = 50


class RatelimitException(Exception):

    def __init__(self, response, message="Gitlab Rate limit exceeded") -> None:

        self.response = response

        super().__init__(message)

class UrlNotFoundException(Exception):
    pass

class NotAuthorizedException(Exception):
    pass

class GitlabDataAccess:

    def __init__(self, logger: logging.Logger):
    
        self.logger = logger
        self.key_client = KeyClient("gitlab_rest", logger)
        self.key = None

    def get_resource_count(self, url):

        # set per_page to 100 explicitly so we know each page is 100 long
        params = {"per_page": 100}
        url = self.__add_query_params(url, params)

        num_pages = self.get_resource_page_count(url)

        # get data for last page
        params = {"page": num_pages}
        url = self.__add_query_params(url, params)

        data = self.get_resource(url)

        return (100 * (num_pages -1)) + len(data)

    def paginate_resource(self, url):

        response = self.make_request_with_retries(url)
        data = response.json()

        # need to ensure data is a list so yield from works properly
        if not isinstance(data, list):
            raise Exception(f"GitlabDataAccess.paginate_resource must be used with url that returns a list. Use GitlabDataAccess.get_resource to retrieve data that is not paginated. The url of {url} returned a {type(data)}.")

        yield from data

        while 'next' in response.links.keys():

            next_page = response.links['next']['url']

            response = self.make_request_with_retries(next_page)
            data = response.json()

            # need to ensure data is a list so yield from works properly
            if not isinstance(data, list):
                raise Exception(f"GitlabDataAccess.paginate_resource must be used with url that returns a list. Use GitlabDataAccess.get_resource to retrieve data that is not paginated. The url of {url} returned a {type(data)}. ")

            yield from data

        return 
    
    def get_resource_page_count(self, url):

        response = self.make_request_with_retries(url, method="HEAD")

        if 'last' not in response.links.keys():
            self.logger.warning(f"Gitlab response without links. Headers: {response.headers}.")
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

            if not self.key:
                self.key = self.key_client.request()

            headers = {"Authorization": f"token {self.key}"}

            response = client.request(method=method, url=url, headers=headers, timeout=timeout, follow_redirects=True)

            if response.status_code == 429:
                raise RatelimitException(response)

            if response.status_code == 404:
                raise UrlNotFoundException(f"Could not find {url}")
            
            if response.status_code == 401:
                raise NotAuthorizedException(f"Could not authorize with the gitlab api")
            
            response.raise_for_status()

            # TODO: Update this to check the correct ratelimit header for gitlab
            try:
                if "X-RateLimit-Remaining" in response.headers and int(response.headers["X-RateLimit-Remaining"]) < GITLAB_RATELIMIT_REMAINING_CAP:
                    raise RatelimitException(response)
            except ValueError:
                self.logger.warning(f"X-RateLimit-Remaining was not an integer. Value: {response.headers['X-RateLimit-Remaining']}")


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
            4. Catches RatelimitException and waits or expires key before raising exception
        """

        try:
            return self.make_request(url, method, timeout)
        except RatelimitException as e:
            self.__handle_gitlab_ratelimit_response(e.response)
            raise e
        except NotAuthorizedException as e:
            self.__handle_gitlab_not_authorized_response()

    def __handle_gitlab_not_authorized_response(self):

        self.key = self.key_client.invalidate(self.key)

        
    def __handle_gitlab_ratelimit_response(self, response):


        current_epoch = int(time.time())
        epoch_when_key_resets = int(response.headers["ratelimit-reset"])
        key_reset_time =  epoch_when_key_resets - current_epoch
        
        if key_reset_time < 0:
            self.logger.error(f"Key reset time was less than 0 setting it to 0.\nThe current epoch is {current_epoch} and the epoch that the key resets at is {epoch_when_key_resets}")
            key_reset_time = 0
            
        self.logger.info(f"\n\n\nGitlab API rate limit exceeded. Sleeping until the key resets ({key_reset_time} seconds)")
        self.key = self.key_client.expire(self.key, epoch_when_key_resets)

    def __add_query_params(self, url: str, additional_params: dict) -> str:
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

        








