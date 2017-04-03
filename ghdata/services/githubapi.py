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
