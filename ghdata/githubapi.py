
import datetime
from dateutil.parser import parse
import pandas as pd
import github


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

    def contributions_by_file(self, owner, repo, filename=None, start=None, end=None, ascending=False):
        """
        Gets number of addtions and deletions in each file by user

        Currently ignores changes from local users unattributed to Github users

        :param owner: repo owner username
        :param repo: repo name
        :param filename: optional; file or directory for function to run on
        :param start: optional; start time for analysis
        :param end: optional; end time for analysis
        :param ascending: Default False; returns dataframe in ascending order
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

        for commit in commits:
            for file in commit.files:
                if filename != None:
                    try:
                        if file.changes != 0 and file.filename == filename:
                            df.append({'user': commit.author.login, 'file': file.filename, 'number of additions': file.additions, 'number of deletions': file.deletions, 'total': file.changes})
                    except AttributeError:
                        pass
                else:
                    try:
                        if file.changes != 0:
                            df.append({'user': commit.author.login, 'file': file.filename, 'number of additions': file.additions, 'number of deletions': file.deletions, 'total': file.changes})
                    except AttributeError:
                        pass

        df = pd.DataFrame(df)

        df = df.groupby(["file", "user"]).sum()

        df = df.sort_values(ascending=ascending)

        return df

    def contributions_by_percentage(self, owner, repo, filename=None, start=None, end=None, ascending=False):
        """
        Calculates percentage of commits in repo by user

        Puts it in dataframe with columns:
        user    percentage of commits

        Currently ignores changes from local users unattributed to Github user

        :param owner: repo owner username
        :param repo: repo name
        :param filename: optional; file or directory for function to run on
        :param start: optional; start time for analysis
        :param end: optional; end time for analysis
        :param ascending: Default False; returns dataframe in ascending order
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
                            df.append({'user': commit.author.login})
                        except AttributeError:
                            pass
                        break
        else:
            for commit in commits:
                try:
                    df.append({'user': commit.author.login})
                except AttributeError:
                    pass

        df = pd.DataFrame(df)

        df = df.groupby(['user']).user.count() / df.groupby(['user']).user.count().sum() * 100

        df = df.sort_values(ascending=ascending)

        return df

    def bus_factor(self, owner, repo, filename=None, start=None, end=None, threshold=50, best=False):
        """
        Calculates bus factor by adding up percentages from highest to lowest until they exceed threshold

        :param owner: repo owner username
        :param repo: repo name
        :param filename: optional; file or directory for function to run on
        :param start: optional; start time for analysis
        :param end: optional; end time for analysis
        :param threshold: Default 50;
        :param best: Default False; If true, sums from lowest to highestn
        """

        df = self.contributions_by_percentage(owner, repo, filename, start, end, best)

        i = 0
        for num in df.cumsum():
            i = i + 1
            if num >= threshold:
                bus_factor = pd.Series(i, index=["Bus Factor"])
                return bus_factor
