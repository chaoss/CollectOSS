
import datetime
from dateutil.parser import parse
import pandas as pd
import github
import json

class GitHubAPI(object):
    """
    GitHubAPI is a class for getting metrics from the GitHub API
    """
    def __init__(self, api_key):
        """
        Creates a new GitHub instance

        :param api_key: GitHub API key
        """
        self.GITUB_API_KEY = api_key
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
        j = 0
        for num in df.cumsum():
            i = i + 1
            if num >= threshold:
                worst = i
                break

        for num in df.sort_values(ascending=True).cumsum():
            j = j + 1
            if num >= threshold:
                best = j
                break

        bus_factor = [{'worst': worst, 'best' : best}]

        return pd.DataFrame(bus_factor)

    def tags(self, owner, repo):
        """
        Returns dates and names of tags

        :param owner: repo owner username
        :param repo: repo name
        """

        tags = self.__api.get_repo((owner + "/" + repo)).get_tags()
        tags_list = []

        for i in tags:
            commit = json.loads(json.dumps(i.commit.raw_data))
            date = commit['commit']['author']['date']
            tags_list.append({'date' : date, 'release' : i.name})

        return pd.DataFrame(tags_list)
