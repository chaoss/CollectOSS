import json
import pandas as pd
import requests

class Downloads(object):
    """Class for retrieveing download information using APIs and web scrapers"""
    def __init__(self, githubapi):
        self.__githubapi = githubapi._GitHubAPI__api
        

    def downloads(self, owner, repo):
        """
        Detects package file and calls correct function for download statistics

        :param owner: repo owner username
        :param repo: repo name
        """
        root_dir = self.__githubapi.get_repo((owner + "/" + repo)).get_dir_contents("/")

        for file in root_dir:
            if file.name == "Gemfile":
                return self.ruby_downloads(repo)

        else:
            return


    def ruby_downloads(self, repo):
        """
        Returns daily downloads for ruby gems from bestgems.org API

        :param repo: repo name
        """
        r = requests.get("http://bestgems.org/api/v1/gems/%s/daily_downloads.json" % (repo))
        raw = r.text
        df = pd.DataFrame(json.loads(json.loads(json.dumps(raw))))
        
        columnsTitles=["date","daily_downloads"]
        df = df.reindex(columns= columnsTitles)
        df.rename(columns= {"daily_downloads" : "downloads"}, inplace=True)

        return df