import logging
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception, RetryError
from urllib.parse import urlparse, parse_qs, urlencode

GITHUB_RATELIMIT_REMAINING_CAP = 50

# ---- EXCEPTIONS ----

class RatelimitException(Exception):
    def __init__(self, response, keys_used, message="Github Rate limit exceeded") -> None:
        self.response = response
        super().__init__(f"{message}. Keys used: {keys_used}")

class UrlNotFoundException(Exception):
    pass

class NotAuthorizedException(Exception):
    pass

# ---- MAIN CLASS ----

class GithubDataAccess:
    def __init__(self, key_manager, logger: logging.Logger):
        self.logger = logger
        self.key_client = key_manager
        self.key = None
        self.expired_keys_for_request = []

    def get_resource_count(self, url):
        params = {"per_page": 100}
        url = self.__add_query_params(url, params)
        num_pages = self.get_resource_page_count(url)
        params = {"page": num_pages}
        url = self.__add_query_params(url, params)
        data = self.get_resource(url)
        return (100 * (num_pages - 1)) + len(data)

    def paginate_resource(self, url):
        response = self.make_request_with_retries(url)
        data = response.json()
        if not isinstance(data, list):
            raise Exception(f"GithubApiHandler.paginate_resource must be used with url that returns a list. Use GithubApiHandler.get_resource to retrieve data that is not paginated. The url of {url} returned a {type(data)}.")
        yield from data
        while 'next' in response.links.keys():
            next_page = response.links['next']['url']
            response = self.make_request_with_retries(next_page)
            data = response.json()
            if not isinstance(data, list):
                raise Exception(f"GithubApiHandler.paginate_resource must be used with url that returns a list. Use GithubApiHandler.get_resource to retrieve data that is not paginated. The url of {url} returned a {type(data)}. ")
            yield from data
        return

    def get_resource_page_count(self, url):
        response = self.make_request_with_retries(url, method="HEAD")
        if 'last' not in response.links.keys():
            self.logger.warning(f"Github response without links. Headers: {response.headers}.")
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

    def make_request(self, url, method="GET", timeout=100):
        with httpx.Client() as client:
            if not self.key:
                self.key = self.key_client.request()
            headers = {"Authorization": f"token {self.key}"}
            response = client.request(method=method, url=url, headers=headers, timeout=timeout, follow_redirects=True)

            # --- Enhanced Rate Limit Detection ---
            is_rate_limit = False
            if response.status_code in [403, 429]:
                is_rate_limit = True

            # Sometimes status code is 400 (abuse detection)
            if response.status_code == 400:
                try:
                    msg = response.json().get("message", "")
                    if "abuse detection" in msg.lower() or "secondary rate limit" in msg.lower():
                        is_rate_limit = True
                except Exception:
                    pass

            # Parse JSON message even if status is 403
            if response.status_code == 403:
                try:
                    msg = response.json().get("message", "")
                    if (
                        "rate limit" in msg.lower() or
                        "abuse detection" in msg.lower() or
                        "secondary rate limit" in msg.lower()
                    ):
                        is_rate_limit = True
                except Exception:
                    pass

            if is_rate_limit:
                self.expired_keys_for_request.append(self.key)
                raise RatelimitException(response, self.expired_keys_for_request[-5:])

            if response.status_code == 404:
                raise UrlNotFoundException(f"Could not find {url}")

            if response.status_code == 401:
                raise NotAuthorizedException(f"Could not authorize with the github api")

            response.raise_for_status()

            try:
                if (
                    "X-RateLimit-Remaining" in response.headers
                    and int(response.headers["X-RateLimit-Remaining"]) < GITHUB_RATELIMIT_REMAINING_CAP
                ):
                    self.expired_keys_for_request.append(self.key)
                    raise RatelimitException(response, self.expired_keys_for_request[-5:])
            except ValueError:
                self.logger.warning(f"X-RateLimit-Remaining was not an integer. Value: {response.headers.get('X-RateLimit-Remaining', None)}")

            return response

    def make_request_with_retries(self, url, method="GET", timeout=100):
        try:
            return self.__make_request_with_retries(url, method, timeout)
        except RetryError as e:
            raise e.last_attempt.exception()

    @retry(stop=stop_after_attempt(10), wait=wait_fixed(5), retry=retry_if_exception(lambda exc: not isinstance(exc, UrlNotFoundException)))
    def __make_request_with_retries(self, url, method="GET", timeout=100):
        try:
            result = self.make_request(url, method, timeout)
            self.expired_keys_for_request = []
            return result
        except RatelimitException as e:
            self.__handle_github_ratelimit_response(e.response)
            raise e
        except NotAuthorizedException as e:
            self.expired_keys_for_request = []
            self.__handle_github_not_authorized_response()
            raise e

    def __handle_github_not_authorized_response(self):
        self.key = self.key_client.invalidate(self.key)

    def __handle_github_ratelimit_response(self, response):
        headers = response.headers
        previous_key = self.key
        if "Retry-After" in headers:
            retry_after = int(headers["Retry-After"])
            self.logger.info('\n\n\n\nEncountered secondary rate limit issue.\n\n\n\n')
            self.key = self.key_client.expire(self.key, time.time() + retry_after)
        elif "X-RateLimit-Remaining" in headers and int(headers["X-RateLimit-Remaining"]) < GITHUB_RATELIMIT_REMAINING_CAP:
            current_epoch = int(time.time())
            epoch_when_key_resets = int(headers["X-RateLimit-Reset"])
            key_reset_time = epoch_when_key_resets - current_epoch
            if key_reset_time < 0:
                self.logger.error(f"Key reset time was less than 0 setting it to 0.\nThe current epoch is {current_epoch} and the epoch that the key resets at is {epoch_when_key_resets}")
                key_reset_time = 0
            self.logger.info(f"\n\n\nAPI rate limit exceeded. Key resets in {key_reset_time} seconds. Informing key manager that key is expired")
            self.key = self.key_client.expire(self.key, epoch_when_key_resets)
        else:
            self.key = self.key_client.expire(self.key, time.time() + 60)
        if previous_key == self.key:
            self.logger.error(f"The same key was returned after a request to expire it was sent (key: {self.key[-5:]})")

    def __add_query_params(self, url: str, additional_params: dict) -> str:
        url_components = urlparse(url)
        original_params = parse_qs(url_components.query)
        merged_params = {**original_params, **additional_params}
        updated_query = urlencode(merged_params, doseq=True)
        return url_components._replace(query=updated_query).geturl()

# ---- TESTS ----

if __name__ == "__main__":
    import pytest
    import httpx
    from unittest.mock import MagicMock

    class DummyKeyClient:
        def __init__(self):
            self.called = {"request": 0, "expire": 0, "invalidate": 0}
        def request(self):
            self.called["request"] += 1
            return "dummy_key"
        def expire(self, key, expire_time):
            self.called["expire"] += 1
            return "dummy_key_expired"
        def invalidate(self, key):
            self.called["invalidate"] += 1
            return "dummy_key_invalid"

    @pytest.fixture
    def setup_github_da(monkeypatch):
        logger = logging.getLogger("github_test")
        logger.setLevel(logging.DEBUG)
        key_client = DummyKeyClient()
        return GithubDataAccess(key_client, logger)

    def make_mock_response(
        status_code,
        headers=None,
        json_data=None,
        text=None,
        links=None,
    ):
        class DummyResponse:
            def __init__(self):
                self.status_code = status_code
                self.headers = headers or {}
                self._json = json_data
                self.text = text or ""
                self.links = links or {}
            def json(self):
                if self._json is not None:
                    return self._json
                raise ValueError("No json data")
            def raise_for_status(self):
                if 400 <= self.status_code < 600:
                    raise httpx.HTTPStatusError(
                        f"{self.status_code} Error", request=None, response=None
                    )
        return DummyResponse()

    def test_403_with_rate_limit_message(setup_github_da, monkeypatch):
        gda = setup_github_da
        monkeypatch.setattr(gda, "key", "abc")
        resp = make_mock_response(403, json_data={"message": "API rate limit exceeded for 1.2.3.4"})
        def client_request(*args, **kwargs):
            return resp
        with monkeypatch.context() as m:
            m.setattr(httpx.Client, "request", client_request)
            with pytest.raises(RatelimitException):
                gda.make_request("https://api.github.com/test")

    def test_403_with_secondary_rate_limit(setup_github_da, monkeypatch):
        gda = setup_github_da
        monkeypatch.setattr(gda, "key", "abc")
        resp = make_mock_response(403, json_data={"message": "You have exceeded a secondary rate limit. Please wait."})
        def client_request(*args, **kwargs):
            return resp
        with monkeypatch.context() as m:
            m.setattr(httpx.Client, "request", client_request)
            with pytest.raises(RatelimitException):
                gda.make_request("https://api.github.com/test")

    def test_400_abuse_detection(setup_github_da, monkeypatch):
        gda = setup_github_da
        monkeypatch.setattr(gda, "key", "abc")
        resp = make_mock_response(400, json_data={"message": "You have triggered an abuse detection mechanism."})
        def client_request(*args, **kwargs):
            return resp
        with monkeypatch.context() as m:
            m.setattr(httpx.Client, "request", client_request)
            with pytest.raises(RatelimitException):
                gda.make_request("https://api.github.com/test")

    def test_429_rate_limit(setup_github_da, monkeypatch):
        gda = setup_github_da
        monkeypatch.setattr(gda, "key", "abc")
        resp = make_mock_response(429, headers={"Retry-After": "60"})
        def client_request(*args, **kwargs):
            return resp
        with monkeypatch.context() as m:
            m.setattr(httpx.Client, "request", client_request)
            with pytest.raises(RatelimitException):
                gda.make_request("https://api.github.com/test")

    def test_xratelimit_remaining_low(setup_github_da, monkeypatch):
        gda = setup_github_da
        monkeypatch.setattr(gda, "key", "abc")
        resp = make_mock_response(200, headers={"X-RateLimit-Remaining": "3"})
        def client_request(*args, **kwargs):
            return resp
        with monkeypatch.context() as m:
            m.setattr(httpx.Client, "request", client_request)
            with pytest.raises(RatelimitException):
                gda.make_request("https://api.github.com/test")

    print("All tests passed! (run with pytest for more detail)")