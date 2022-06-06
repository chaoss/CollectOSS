import collections
import httpx
import time
import json

from urllib.parse import *
from urllib.parse import parse_qs


class GithubPaginator(collections.abc.Sequence):
    def __init__(self, url, access_token, from_datetime=None, to_datetime=None):

        remove_fields = ["per_page", "page"]
        url = clean_url(url, remove_fields)

        per_page_param = {"per_page": 100}
        url = add_query_params(url, per_page_param)

        self.url = url
        self.from_datetime = from_datetime
        self.to_datetime = to_datetime
        self.rate_limit = None

        self.headers = {'Authorization': f'token {access_token}'}

    def __getitem__(self, index):

        # get the page the item is on
        items_page = (index // 100) + 1

        # create url to query
        per_page_param = {"page": items_page}
        url = add_query_params(self.url, per_page_param)

        data, _ = retrieve_data(url, self.headers)

        if data is None:
            return None

        # get the position of data on the page
        page_index = index % 100

        try:
            return data[page_index]
        except KeyError:
            return None

    def __len__(self):

        # make head request
        num_attempts = 0
        while num_attempts < 10:
            r = hit_api(self.url, self.headers, method="HEAD")

            if r:
                break

        else:
            return None

        num_pages = None
        last_page_data_count = None
        last_page_url = None

        if 'last' not in r.links.keys():
            num_pages = 1

            # add query page number to establish which page we need to look at and count the data
            page_num_param = {"page": num_pages}
            last_page_url = add_query_params(self.url, page_num_param)
            
        else:
            # get the last url from header
            last_page_url = get_url_from_header(r, 'last')

            parsed_url = urlparse(last_page_url)
            num_pages = int(parse_qs(parsed_url.query)['page'][0])

        # get the amount of data on last page
        data, _ = retrieve_data(last_page_url, self.headers)

        last_page_data_count = len(data)

        data_length = (100 * (num_pages - 1)) + last_page_data_count

        return data_length
        

    def __iter__(self):

        data_list, response = retrieve_data(self.url, self.headers)

        if data_list is None:
            yield None
            return 

        for data in data_list:
            yield data

        while 'next' in response.links.keys():
            next_page = get_url_from_header(response, 'next')
            data_list, response = retrieve_data(next_page, self.headers)

            if data_list is None:
                return

            for data in data_list:
                yield data

    def __aiter__(self):
        pass

def clean_url(url, remove_fields):

    u = urlparse(url)
    query = parse_qs(u.query, keep_blank_values=True)

    for field in remove_fields:
        query.pop(field, None)

    u = u._replace(query=urlencode(query, True))
    clean_url = urlunparse(u)

    return clean_url


def add_query_params(url: str, additional_params: dict) -> str:
    url_components = urlparse(url)
    original_params = parse_qs(url_components.query)
    # Before Python 3.5 you could update original_params with
    # additional_params, but here all the variables are immutable.
    merged_params = {**original_params, **additional_params}
    updated_query = urlencode(merged_params, doseq=True)
    # _replace() is how you can create a new NamedTuple with a changed field
    return url_components._replace(query=updated_query).geturl()

def get_url_from_header(request, type):

    return request.links[type]['url']

def retrieve_data(url, headers):

    num_attempts = 0
    while num_attempts < 10:

        response = hit_api(url, headers)
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

def hit_api(url, headers, method='GET'):

    # print(f"Hitting endpoint with {method} request: {url}...\n")

    try:
        response = httpx.request(method=method, url=url, headers=headers)
    except TimeoutError:
        print("Request timed out. Sleeping 10 seconds and trying again...\n")
        time.sleep(10)
        return None

    return response

def process_dict_response(response, page_data):
    
    print("Request returned a dict: {}\n".format(page_data))
    if page_data['message'] == "Not Found":
        print(
            "Github repo was not found or does not exist for endpoint: "
            f"{url.format(page_number)}\n"
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


# url = "https://api.github.com/repos/chaoss/augur/issues/events?per_page=50&page=5"

url = "https://api.github.com/repos/ABrain7710/cs-4320-github-assignment-one-repo/pulls?state=all&direction=desc"

with open('../augur.config.json', 'r') as f:
  access_token = json.load(f)["Database"]["key"]


prs = GithubPaginator(url, access_token)

print("Data")
for i in prs:
    print(i["url"])

print("Length")
print(len(prs))

print("First pr url")
print(prs[0]["url"])
print("\n")

