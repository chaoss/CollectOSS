import collections
import httpx
import time
import json
import asyncio

from oauth_key_manager import OauthKeyManager

from urllib.parse import *
from urllib.parse import parse_qs


class GithubPaginator(collections.abc.Sequence):
    def __init__(self, url, config_path, from_datetime=None, to_datetime=None):

        remove_fields = ["per_page", "page"]
        url = clean_url(url, remove_fields)

        self.url = url
        self.from_datetime = from_datetime
        self.to_datetime = to_datetime
        self.rate_limit = None
        self.default_params = {"per_page": 100}

        self.key_manager = OauthKeyManager(config_path)

        key = self.key_manager.get_key(first_key=True)

        self.headers = get_header(key)

    def __getitem__(self, index):

        # get the page the item is on
        items_page = (index // 100) + 1

        # create url to query
        params = {"page": items_page}.update(self.default_params)

        data, _ = self.retrieve_data(self.url, self.headers, query_params=params)

        if data is None:
            return None

        # get the position of data on the page
        page_index = index % 100

        try:
            return data[page_index]
        except KeyError:
            return None

    def __len__(self):

        num_pages = self.get_last_page_number(self.url, self.headers)

        print(f"Num pages: {num_pages}")

        params = {"page": num_pages}.update(self.default_params)

        # get the amount of data on last page
        data, _ = self.retrieve_data(self.url, self.headers, query_params=params)

        last_page_data_count = len(data)

        data_length = (100 * (num_pages - 1)) + last_page_data_count

        return data_length
        

    def __iter__(self):

        data_list, response = self.retrieve_data(self.url, self.headers, query_params=self.default_params)

        if data_list is None:
            yield None
            return 

        for data in data_list:
            yield data

        while 'next' in response.links.keys():
            next_page = response.links['next']['url']

            # Here we don't need to pass in params with the page, or the default params because the url from the headers already has those values
            data_list, response = self.retrieve_data(next_page, self.headers)

            if data_list is None:
                return

            for data in data_list:
                yield data

    def hit_api(self, url, headers, query_params={}, method='GET'):

        # print(f"Hitting endpoint with {method} request: {url}...\n")

        with httpx.Client() as client:

            try:
                response = client.request(
                    method=method, url=url, headers=headers, params=query_params)

                if is_key_depleted(response) is True:

                    key = self.key_manager.get_key()

                    self.headers = get_header(key)

            except TimeoutError:
                print("Request timed out. Sleeping 10 seconds and trying again...\n")
                time.sleep(10)
                return None

        return response 

    def retrieve_data(self, url, headers, query_params={}):

        num_attempts = 0
        while num_attempts < 10:

            response = self.hit_api(url, headers, query_params)
            if response is None:
                continue
            # update rate limit here

            try:
                page_data = response.json()
            except:
                page_data = json.loads(json.dumps(response.text))

            if type(page_data) == list:
                return page_data, response

            elif type(page_data) == dict:
                result = process_dict_response(response, page_data)

                if result == "break":
                    break
                elif result == "decrease_attempts":
                    num_attempts -= 1

            elif type(page_data) == str:
                result, data_loaded = process_str_response(response, page_data)

                if data_loaded:
                    return result, response

            num_attempts += 1

        return None, None

    async def __aiter__(self):
        
        last_page_num = self.get_last_page_number(self.url, self.headers)


        if last_page_num == 1:
            params = {"page": 1}.update(self.default_params)

            data_list, _ = self.retrieve_data(
                self.url, self.headers, query_params=params)

            for data in data_list:
                yield data

            return
        
        async with httpx.AsyncClient() as client:
            tasks = []
            for page_num in range(1, last_page_num + 1):

                params = {"page": page_num}.update(self.default_params)

                tasks.append(asyncio.ensure_future(
                    self.async_retrieve_data(client, self.url, self.headers, query_params=params)))
 
            index = 1
            while len(tasks) > 0:

                print(f"Batch {index}")
                data_list = await asyncio.gather(*tasks[:1])
            
                del tasks[:1]

                for data in data_list:
                    yield data

    async def async_hit_api(self, client, url, headers, method='GET'):
        # print(f"Hitting endpoint with {method} request: {url}...\n")

        try:
            response = await client.request(method=method, url=url, headers=headers)

            if is_key_depleted(response) is True:

                key = self.key_manager.get_key()

                self.headers = get_header(key)
        except TimeoutError:
            print("Request timed out. Sleeping 10 seconds and trying again...\n")
            time.sleep(10)
            return None

        print(url)

        return response


    async def async_retrieve_data(self, client, url, headers, query_params={}):

        num_attempts = 0
        while num_attempts < 10:

            response = await self.async_hit_api(client, url, headers)
            if response is None:
                continue
            # update rate limit here

            try:
                page_data = response.json()
            except:
                page_data = json.loads(json.dumps(response.text))

            if type(page_data) == list:
                return page_data, response

            elif type(page_data) == dict:
                result = process_dict_response(response, page_data)

                if result == "break":
                    break
                elif result == "decrease_attempts":
                    num_attempts -= 1

            elif type(page_data) == str:
                result, data_loaded = process_str_response(response, page_data)

                if data_loaded:
                    return result, response

            num_attempts += 1

        return None, None

    def get_last_page_number(self, url, headers):

        num_attempts = 0
        while num_attempts < 10:
            r = self.hit_api(url, headers, method="HEAD")

            if r:
                break

        else:
            return None

        if 'last' not in r.links.keys():
            return 1
        else:
            # get the last url from header
            last_page_url = r.links['last']['url']

            parsed_url = urlparse(last_page_url)
            num_pages = int(parse_qs(parsed_url.query)['page'][0])

            return num_pages


################################################################################

# Url Helper Method to remove query paramaters from the url
def clean_url(url, remove_fields):

    u = urlparse(url)
    query = parse_qs(u.query, keep_blank_values=True)

    for field in remove_fields:
        query.pop(field, None)

    u = u._replace(query=urlencode(query, True))
    clean_url = urlunparse(u)

    return clean_url

################################################################################

# Methods to process api responses

def process_dict_response(response, page_data):
    
    print("Request returned a dict: {}\n".format(page_data))
    if page_data['message'] == "Not Found":
        print(
            "Github repo was not found or does not exist for endpoint: "
            f"{response.url}\n"
        )
        return "break"

    if "You have exceeded a secondary rate limit. Please wait a few minutes before you try again" in page_data['message']:
        print('\n\n\n\nSleeping for 100 seconds due to secondary rate limit issue.\n\n\n\n')
        time.sleep(100)

        return "decrease_attempts"

    if "You have triggered an abuse detection mechanism." in page_data['message']:
        #self.update_rate_limit(response, temporarily_disable=True,platform=platform)

        return "decrease_attempts"

    if page_data['message'] == "Bad credentials":
        print("\n\n\n\n\n\n\n POSSIBLY BAD TOKEN \n\n\n\n\n\n\n")
        #self.update_rate_limit(response, bad_credentials=True, platform=platform)
        return "bad_credentials"

def process_str_response(response, page_data):
        print(f"Warning! page_data was string: {page_data}\n")
        if "<!DOCTYPE html>" in page_data:
            print("HTML was returned, trying again...\n")
            return "html_response", False
        elif len(page_data) == 0:
            print("Empty string, trying again...\n")
            return "empty_string", False
        else:
            try:
                page_data = json.loads(page_data)
                return page_data, True
            except:
                pass


################################################################################

# Other utility functions

# creates the header needed for a request, when given an api key
def get_header(oauth_key):

    return {'Authorization': f'token {oauth_key}'}


# determines if all the rate limit is used up on a key, and it is depleted
def is_key_depleted(response):

    rate_limit_header_key = "X-RateLimit-Remaining"

    rate_limit = int(response.headers[rate_limit_header_key])

    return rate_limit == 0


################################################################################

# Main function to test program

def main():
    small_url = "https://api.github.com/repos/bradtraversy/50projects50days/pulls?state=all&direction=desc"

    large_url = "https://api.github.com/repos/chaoss/augur/pulls?state=all&direction=desc"

    extra_large_url = "https://api.github.com/repos/freeCodeCamp/freeCodeCamp/pulls?state=all&direction=desc"


    config_path = '../augur.config.json'

    prs = GithubPaginator(extra_large_url, config_path)

    start_time = time.time()

    for i in range(0, 30):
        for pr in prs:
            pass

    total_time = time.time() - start_time
    print(total_time)

if __name__ == '__main__':
    # This code won't run if this file is imported.
    main()
