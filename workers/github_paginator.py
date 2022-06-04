import collections
import httpx

from urllib.parse import urlparse
from urllib.parse import parse_qs


class GithubPaginator(collections.abc.Sequence):
    def __init__(self, url, from_datetime=None, to_datetime=None):

        self.url = f"{url}?per_page=100"
        self.from_datetime = from_datetime
        self.to_datetime = to_datetime

    def __getitem__(self, index):

        # get the page the item is on
        items_page = (index // 100) + 1

        # create url to query
        url = f"{self.url}&page={items_page}"

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

        # get links (next, first, last prev)
        links = r.headers['Link']

        num_pages = None
        last_page_data_count = None
        last_page_url = None

        if 'last' not in links:
            num_pages = 1
            last_page_url = f"{self.url}&page={num_pages}"

        else:
            for link in links.split(','):

                if 'last' in link:
                    # get the last page link
                    last_page_url = (link.split("<"))[1].split(">")[0]

                    parsed_url = urlparse(last_page_url)
                    num_pages = int(parse_qs(parsed_url.query)['page'][0])

        # get the amount of data on last page
        r = httpx.get(last_page_url)

        last_page_data_count = len(r.json())

        data_length = (100 * (num_pages - 1)) + last_page_data_count

        return data_length
        

    def __iter__(self):

        # make a get request for data

        # yield data

        # if the headers include next then go to the next page
        pass

    def __aiter__(self):
        pass


url = "https://api.github.com/repos/chaoss/augur/issues/events"

issues = GithubPaginator(url)
# print(issues[0])
print(issues[10000000000])


