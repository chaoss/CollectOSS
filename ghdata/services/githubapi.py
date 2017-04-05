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
        File    User    Num of Additions    Num of Deletion   Total Changes

        Currently ignores changes from local users unattributed to Github users

        WORK IN PROGRESS

        """

        df = []
        for commit in self.__api.get_repo((owner + "/" + repo)).get_commits(since=start,until=end):
            for file in commit.files:
                try:
                    df.append({'User': commit.author.login, 'File': file.filename, 'Number of Additions': file.additions, 'Number of Deletions': file.deletions, 'Total': file.changes})
                except AttributeError:
                    pass

        df = pd.DataFrame(df)

        df.groupby(["File" ,"User"]).sum()

        return df
