from .localcsv import LocalCSV
import json
import re
from dateutil.parser import parse
import pandas as pd
import github
import requests

class GitHubAPI(object):
    """
    GitHubAPI is a class for getting metrics from the GitHub API
    """
    def __init__(self, api_key):
        """
        Creates a new GitHub instance

        :param api_key: GitHub API key
        """
        self.GITHUB_API_KEY = api_key
        self.__api = github.Github(api_key)

    def bus_factor(self, owner, repo, filename=None, start=None, end=None, threshold=50):
        """
        Calculates bus factor by adding up percentages from highest to lowest until they exceed threshold

        :param owner: repo owner username
        :param repo: repo name
        :param filename: optional; file or directory for function to run on
        :param start: optional; start time for analysis
        :param end: optional; end time for analysis
        :param threshold: Default 50;
        """

        if start != None:
            start = parse(start)
        else:
            start = github.GithubObject.NotSet

        if end != None:
            end = parse(end)
        else:
            end = github.GithubObject.NotSet

        commits = self.__api.get_repo((owner + "/" + repo)).get_commits(since=start, until=end)

        if filename != None:
            self.__api.get_repo((owner + "/" + repo)).get_contents(filename)

        df = []

        if filename != None:
            for commit in commits:
                for file in commit.files:
                    if file.filename == filename:
                        try:
                            df.append({'userid': commit.author.id})
                        except AttributeError:
                            pass
                        break
        else:
            for commit in commits:
                try:
                    df.append({'userid': commit.author.id})
                except AttributeError:
                    pass

        df = pd.DataFrame(df)

        df = df.groupby(['userid']).userid.count() / df.groupby(['userid']).userid.count().sum() * 100

        i = 0
        for num in df.cumsum():
            i = i + 1
            if num >= threshold:
                worst = i
                break

        i = 0
        for num in df.sort_values(ascending=True).cumsum():
            i = i + 1
            if num >= threshold:
                best = i
                break

        bus_factor = [{'worst': worst, 'best' : best}]

        return pd.DataFrame(bus_factor)

    def tags(self, owner, repo, raw=False):
        """
        Returns dates and names of tags

        :param owner: repo owner username
        :param repo: repo name
        :param raw: Default False; Returns list of dicts
        """

        cursor = "null"
        tags_list = []
        url = "https://api.github.com/graphql"

        while True:
            query = {"query" :
                     """
                    query {
                      repository(owner: "%s", name: "%s") {
                        tags: refs(refPrefix: "refs/tags/", first: 100, after: "%s") {
                          edges {
                            cursor
                            tag: node {
                              name
                              target {
                                ... on Tag {
                                  tagger {
                                    date
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
            """ % (owner, repo, cursor)
            }
            r = requests.post(url, auth=requests.auth.HTTPBasicAuth('user', self.GITHUB_API_KEY), json=query)
            raw = r.text
            data = json.loads(json.loads(json.dumps(raw)))
            tags = data['data']['repository']['tags']['edges']
            for i in tags:
                try:
                    tags_list.append({'date' : i['tag']['target']['tagger']['date'], 'release' : i['tag']['name']})
                except KeyError:
                    pass
            if data['data']['repository']['tags']['edges'] == []:
                break
            else:
                cursor = data['data']['repository']['tags']['edges'][-1]['cursor']
        return pd.DataFrame(tags_list)

    def major_tags(self, owner, repo):
        """
        Returns dates and names of major version (according to semver) tags. May return blank if no major versions

        :param owner: repo owner username
        :param repo: repo name
        """
        cursor = "null"
        tags_list = []
        url = "https://api.github.com/graphql"

        while True:
            query = {"query" :
                     """
                    query {
                      repository(owner: "%s", name: "%s") {
                        tags: refs(refPrefix: "refs/tags/", first: 100, after: "%s") {
                          edges {
                            cursor
                            tag: node {
                              name
                              target {
                                ... on Tag {
                                  tagger {
                                    date
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
            """ % (owner, repo, cursor)
            }
            r = requests.post(url, auth=requests.auth.HTTPBasicAuth('user', self.GITHUB_API_KEY), json=query)
            raw = r.text
            data = json.loads(json.loads(json.dumps(raw)))
            tags = data['data']['repository']['tags']['edges']
            for i in tags:
                try:
                    tags_list.append({'date' : i['tag']['target']['tagger']['date'], 'release' : i['tag']['name']})
                except KeyError:
                    pass
            if data['data']['repository']['tags']['edges'] == []:
                break
            else:
                cursor = data['data']['repository']['tags']['edges'][-1]['cursor']

        major_versions = []
        pattern = re.compile("[0-9]+\.[0]+\.[0]+$")
        for i in tags_list:
            try:
                if re.search(pattern, i["release"]) != None:
                    major_versions.append(i)
            except AttributeError:
                pass

        return pd.DataFrame(major_versions)


    def contributors_gender(self, owner, repo=None):
        contributors = self.__api.get_repo((owner + "/" + repo)).get_contributors()
        names = pd.DataFrame(columns=['name'])
        i = 0
        for contributor in contributors:
            if contributor.name is not None:
                names.loc[i] = [contributor.name.split()[0]]
                i += 1
        genderized = names.merge(LocalCSV.name_gender, how='inner', on=['name'])
        return genderized