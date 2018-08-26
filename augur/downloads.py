#SPDX-License-Identifier: MIT
"""
Data source that gathers download stats from package managers
"""

import json
import pandas as pd
import requests
import datetime
import base64
from augur import logger
from augur.util import annotate

# end imports
# (don't remove the above line, it's for a script)

class Downloads(object):
    """Class for retrieveing download information using APIs and web scrapers"""
    def __init__(self, githubapi):
        self.__githubapi = githubapi.api

    #####################################
    ###    DIVERSITY AND INCLUSION    ###
    #####################################


    #####################################
    ### GROWTH, MATURITY, AND DECLINE ###
    #####################################


    #####################################
    ###            RISK               ###
    #####################################


    #####################################
    ###            VALUE              ###
    #####################################


    #####################################
    ###           ACTIVITY            ###
    #####################################


    #####################################
    ###         EXPERIMENTAL          ###
    #####################################
        
    @annotate(tag='downloads')
    def downloads(self, owner, repo):
        """
        Timeseries that returns package file and calls the correct function to the create download statistics

        :param owner: repo owner username
        :param repo: repo name
        :return: DataFrame with all downloads for that day
        """
        root_dir = self.__githubapi.get_repo((owner + "/" + repo)).get_dir_contents("/")

        for file in root_dir:
            if file.name == "Gemfile":
                return self.ruby_downloads(repo)
            if file.name == "package.json":
                contents = base64.b64decode(file.content)
                contents = contents.decode('utf-8')
                return self.npm_downloads(repo, contents)

    def ruby_downloads(self, repo):
        """
        Timeseries of daily downloads for ruby gems from bestgems.org API

        :param repo: repo name
        :return: DataFrame with count of ruby downloads
        """
        r = requests.get("http://bestgems.org/api/v1/gems/%s/daily_downloads.json" % (repo))
        raw = r.text
        df = pd.DataFrame(json.loads(json.loads(json.dumps(raw))))
        
        columnsTitles=["date","daily_downloads"]
        df = df.reindex(columns= columnsTitles)
        df.rename(columns= {"daily_downloads" : "downloads"}, inplace=True)

        return df

    def npm_downloads(self, repo, contents):
        """
        Returns daily downloads for ruby gems from bestgems.org API

        :param repo: repo name
        :param contents: contents of package.json
        :return: DataFrame with count of npm downloads
        """
        contents = json.loads(json.loads(json.dumps(contents)))
        name = contents["name"]
        dates = []
        r = requests.get("https://api.npmjs.org/downloads/range/0:%s/%s" % (datetime.datetime.today().strftime('%Y-%m-%d'), name))
        raw = r.text
        raw = json.loads(json.loads(json.dumps(raw)))
        df = pd.DataFrame(raw["downloads"])
        df.rename(columns= {"day" : "date"}, inplace=True)

        for i, row in df.iterrows():
            if row["downloads"] != 0:
                break
            else:
                df.drop(i, inplace=True)

        return df