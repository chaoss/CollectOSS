import pandas as pd
import sys
if (sys.version_info > (3, 0)):
    import urllib.parse as url
else:
    import urllib as url
import requests


class PublicWWW(object):
    """
    PublicWWW is a class for making API requests to https://publicwww.com/ a
    search engine for the source of websites
    """

    def __init__(self, public_www_api_key):
        """
        Initalizes a PublicWWW instance

        :param public_www_api_key: The API key for PublicWWW. This is required to get the full names of more results
        """
        self.PUBLIC_WWW_API_KEY = public_www_api_key

    def linking_websites(self, owner, repo):
        """
        Finds the repo's popularity on the internet

        :param owner: The username of a project's owner
        :param repo: The name of the repository
        :return: DataFrame with the issues' id the date it was
                 opened, and the date it was first responded to
        """

        # Find websites that link to that repo
        repo_url="https://github.com/{owner}/{repo}".format(owner=owner, repo=repo)
        query = '<a+href%3D"{repourl}"'.format(repourl=url.quote_plus(repo_url))
        r = 'https://publicwww.com/websites/{query}/?export=csv&apikey={apikey}'.format(query=query, apikey=self.PUBLIC_WWW_API_KEY)
        result =  pd.read_csv(r, delimiter=';', header=None, names=['url', 'rank'])
        return result