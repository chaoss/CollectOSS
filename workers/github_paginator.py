import collections
import httpx

from urllib.parse import *
from urllib.parse import parse_qs


class GithubPaginator(collections.abc.Sequence):
    def __init__(self, url, from_datetime=None, to_datetime=None, access_token=None):

        remove_fields = ["per_page", "page"]
        url = clean_url(url, remove_fields)

        per_page_param = {"per_page": 100}
        url = add_query_params(url, per_page_param)

        self.url = url
        self.from_datetime = from_datetime
        self.to_datetime = to_datetime

        self.headers = {"Authorization": access_token}

    def __getitem__(self, index):

        # get the page the item is on
        items_page = (index // 100) + 1

        # create url to query
        per_page_param = {"page": items_page}
        url = add_query_params(self.url, per_page_param)

        data = httpx.get(url).json()

        # get the position of data on the page
        page_index = index % 100

        try:
            return data[page_index]
        except KeyError:
            return None

    def __len__(self):

        # make head request
        r = httpx.head(self.url)

        num_pages = None
        last_page_data_count = None
        last_page_url = None

        if 'last' not in r.links.keys():
            num_pages = 1
            per_page_param = {"page": num_pages}
            last_page_url = add_query_params(self.url, per_page_param)
            
        else:
            # get the last url from header
            last_page_url = get_url_from_header(r, 'last')

            parsed_url = urlparse(last_page_url)
            num_pages = int(parse_qs(parsed_url.query)['page'][0])

        # get the amount of data on last page
        r = httpx.get(last_page_url)

        last_page_data_count = len(r.json())

        data_length = (100 * (num_pages - 1)) + last_page_data_count

        return data_length
        

    def __iter__(self):

        r = httpx.get(url=self.url, headers=self.headers)
        yield r.json()

        while 'next' in r.links.keys():
            next_page = get_url_from_header(r, 'next')
            next_page_res = httpx.get(next_page, headers=self.headers)
            yield next_page_res.json()

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


url = "https://api.github.com/repos/chaoss/augur/issues/events?per_page=50&page=5"

issues = GithubPaginator(url)
print(len(issues))
# print(issues[10000000000])


