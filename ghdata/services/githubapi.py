import pandas


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
        User    File    Num of Additions    Num of Deletions

        WORK IN PROGRESS
        """
        df = pd.DataFrame()
        commits = self.g.get_repo((owner + "/" + repo)).get_commits(since=start, until=end)
        for commit in commits:
            for file in commit.files:
                df.append({'user': commit.author, 'file': file.filename, 'additions': file.additions, 'deletions': file.deletions, 'total': file.changes})

        return df
