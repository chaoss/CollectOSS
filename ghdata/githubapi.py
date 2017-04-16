
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

    def contributions_by_file(self, owner, repo, filename=None, start=None, end=None):
        """
        Gets number of addtions and deletions in each file by user

        Currently ignores changes from local users unattributed to Github users

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

        return df

    def contributions_by_percentage(self, owner, repo, filename=None, start=None, end=None):
        """
        Calculates percentage of commits in repo by user

        Puts it in dataframe with columns:
        user    percentage of commits

        Currently ignores changes from local users unattributed to Github user

        TODO: Have filename or file object as param and only calculate for that file

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

        return df
