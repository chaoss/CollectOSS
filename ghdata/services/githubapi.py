import pandas as pd


class GitHubAPI(object):
    """
    GitHubAPI is a class for getting metrics from the GitHub API
    """
    def __init__(self, api_key):
        """
        Creates a new GitHub instance

        :param api_key: GitHub API key
        """
        import github
        self.GITUB_API_KEY = api_key
        self.__api = github.Github(api_key)

    def contributions_by_file(self, owner, repo, start=None, end=None):
        """
        Gets number of addtions and deletions in each file by user

        Puts it in dataframe with columns:
        file    user    num of additions    num of deletion   total changes

        Currently ignores changes from local users unattributed to Github users

        TODO: Have filename or file object as param and only calculate for that file

        """

        df = []
        for commit in self.__api.get_repo((owner + "/" + repo)).get_commits(since=start,until=end):
            for file in commit.files:
                try:
                    df.append({'user': commit.author.login, 'file': file.filename, 'number of additions': file.additions, 'number of deletions': file.deletions, 'total': file.changes})
                except AttributeError:
                    pass

        df = pd.DataFrame(df)

        df.groupby(["file" ,"user"]).sum()

        return df

    def contributions_by_percentage(self, owner, repo, start=None, end=None):
        """
        Calculates percentage of commits in repo by user

        Puts it in dataframe with columns:
        user    percentage of commits

        Currently ignores changes from local users unattributed to Github user

        May equal to more than 100% due to rounding

        TODO: Have filename or file object as param and only calculate for that file

        """

        df = []
        for commit in self.__api.get_repo(('OSSHealth' + "/" + 'ghdata')).get_commits():
            try:
                df.append({'user': commit.author.login})
            except AttributeError:
                pass

        df = pd.DataFrame(df)

        df = df.groupby(['user']).user.count() / df.groupby(['user']).user.count().sum() * 100

        return df.round()
