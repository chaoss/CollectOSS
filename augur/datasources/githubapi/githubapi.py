#SPDX-License-Identifier: MIT
"""
Data source that uses the GitHub API
"""

import json
import re
import pandas as pd
from github import Github
import requests
from augur.datasources.localcsv.localcsv import LocalCSV
from augur import logger
from augur.util import annotate
# end imports
# (don't remove the above line, it's for a script)

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
        self.api = Github(api_key)

    #####################################
    ###    DIVERSITY AND INCLUSION    ###
    #####################################


    #####################################
    ### GROWTH, MATURITY, AND DECLINE ###
    #####################################

    @annotate(tag='closed-issues')
    def closed_issues(self, owner, repo=None):
        """
        Timeseries of the count of the number of issues closed per day

        :param owner: The name of the project owner.
        :param repo: The name of the repo.
        :return: DataFrame with newly closed issues/day
        """

        url = "https://api.github.com/repos/{}/{}/issues?state=closed".format(owner, repo)
        json = requests.get(url, auth=('user', self.GITHUB_API_KEY)).json()
        df = pd.DataFrame(json, columns=['created_at'])

        df['created_at'] = pd.to_datetime(df['created_at']).dt.normalize()

        df = df.groupby('created_at').size().reset_index(name='count')

        return df

    @annotate(tag='code-commits')
    def code_commits(self, owner, repo):
        """
        Timeseries of the count of code commits per day.

        :param owner: The name of the project owner.
        :param repo: The name of the repo.
        :return: DataFrame with code commits/day.
        """
        i = 0
        url = "https://api.github.com/repos/{}/{}/commits?page={}"
        json = []

        # Paginate through all the code commits
        while True:
            j = requests.get(url.format(owner, repo, i),
                             auth=('user', self.GITHUB_API_KEY)).json()
            if len(j) == 0:
                break
            json += j
            i += 1

        df = pd.DataFrame.from_dict({i: json[i]['commit']['author']['date']
                                     for i in range(len(json))}, orient='index')
        df.columns = ['created_at']
        df['created_at'] = pd.to_datetime(df['created_at']).dt.normalize()
        df = df.groupby('created_at').size().reset_index(name='count')

        return df

    @annotate(tag='contributors')
    def contributors(self, owner, repo):
        """
        List of contributors and their contributions.

        :param owner: The name of the project owner
        :param repo: The name of the repo
        :return: DataFrame consisting of contributors and their contributions
        """
        url = 'https://api.github.com/repos/{}/{}/contributors'.format(owner, repo)
        json = requests.get(url, auth=('user', self.GITHUB_API_KEY)).json()

        df = pd.DataFrame(json, columns=['login', 'contributions'])

        return df

    @annotate(tag='lines-of-code-changed')
    def lines_of_code_changed(self, owner, repo=None):
        """
        Timeseries of the count of lines added, deleted, and the net change each week

        :param owner: The name of the project owner
        :param repo: The name of the repo
        :return: DataFrame with the associated lines changed information/week
        """
        # get the data we need from the GitHub API
        # see <project_root>/augur/githubapi.py for examples using the GraphQL API
        url = "https://api.github.com/repos/{}/{}/stats/code_frequency".format(owner, repo)
        json = requests.get(url, auth=('user', self.GITHUB_API_KEY)).json()
        # get our data into a dataframe
        df = pd.DataFrame(json, columns=['date', 'additions', 'deletions'])
        # all timeseries metrics need a 'date' column
        df['date'] = pd.to_datetime(df['date'], unit='s', infer_datetime_format=True)
        # normalize our data and create useful aggregates
        df['deletions'] = df['deletions'] * -1
        df['delta'] = df['additions'] - df['deletions']
        df['total_lines'] = df['delta'].cumsum()
        # return the dataframe
        return df

    @annotate(tag='open-issues')
    def open_issues(self, owner, repo):
        """
        Timeseries of the number of issues opened per day.

        :param owner: The username of the project owner.
        :param repo: The name of the repository.
        :return: DatFrame with number of issues opened per day.
        """

        url = 'https://api.github.com/repos/{}/{}/issues?state=all'.format(owner, repo)
        issues = []

        while True:
            response = requests.get(url, auth=('user', self.GITHUB_API_KEY))
            issues += response.json()

            if 'next' not in response.links:
                break

            url = response.links['next']['url']

        df = pd.DataFrame(issues, columns=['created_at'])
        df['created_at'] = pd.to_datetime(df['created_at']).dt.normalize()
        df = df.groupby('created_at').size().reset_index(name='count')

        return df



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

    @annotate(tag='bus-factor')
    def bus_factor(self, owner, repo, threshold=50):
        """
        Calculates bus factor by adding up percentages from highest to lowest until they exceed threshold

        :param owner: repo owner username
        :param repo: repo name
        :param threshold: Default 50;
        """
        cursor = ""
        url = "https://api.github.com/graphql"
        commit_count = []
        hasNextPage = True
        threshold = threshold / 100
        while hasNextPage:
            query = {"query" :
                     """
                        query{
                          repository(name: "%s", owner: "%s") {
                            ref(qualifiedName: "master") {
                              target {
                                ... on Commit {
                                  id
                                  history(first: 100%s) {
                                    pageInfo {
                                      hasNextPage
                                    }
                                    edges {
                                      cursor
                                      node {
                                        author {
                                          email
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                        """ % (repo, owner, cursor)
            }
            r = requests.post(url, auth=requests.auth.HTTPBasicAuth('user', self.GITHUB_API_KEY), json=query)
            raw = r.text
            data = json.loads(json.loads(json.dumps(raw)))
            hasNextPage = data['data']['repository']['ref']['target']['history']['pageInfo']['hasNextPage']
            commits = data['data']['repository']['ref']['target']['history']['edges']
            for i in commits:
                commit_count.append({'email' : i['node']['author']['email']})
            cursor = ", after: \"%s\"" % (commits[-1]['cursor'])


        df = pd.DataFrame(commit_count)

        total = df.email.count()

        df = df.groupby(['email']).email.count() / df.groupby(['email']).email.count().sum() * 100

        i = 0
        for num in df.sort_values(ascending=False).cumsum():
            i = i + 1
            if num >= threshold:
                break
        worst = i

        j = 0
        for num in df.sort_values(ascending=True).cumsum():
            j = j + 1
            if num >= threshold:
                break
        best = j

        bus_factor = [{'worst': worst, 'best' : best}]

        return pd.DataFrame(bus_factor)

    @annotate(tag='major-tags')
    def major_tags(self, owner, repo):
        """
        Timeseries of the dates and names of major version (according to semver) tags. May return blank if no major versions

        :param owner: repo owner username
        :param repo: repo name
        :return: DataFrame with major versions and their release date
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

    @annotate(tag='tags')
    def tags(self, owner, repo, raw=False):
        """
        Timeseries of the dates and names of tags

        :param owner: repo owner username
        :param repo: repo name
        :param raw: Default False; Returns list of dicts
        :return: DataFrame with all tags and their release date
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

    def contributors_gender(self, owner, repo=None):
        contributors = self.api.get_repo((owner + "/" + repo)).get_contributors()
        names = pd.DataFrame(columns=['name'])
        i = 0
        for contributor in contributors:
            if contributor.name is not None:
                names.loc[i] = [contributor.name.split()[0]]
                i += 1
        genderized = names.merge(LocalCSV.name_gender, how='inner', on=['name'])
        return genderized

    # def code_reviews(self, owner, repo=None):
    #     """
    #     Number of code reviews (merge requests) for a project

    #     :param owner: The name of the project owner
    #     :param repo: The name of the repo
    #     :return: DataFrame with each row being a merge request's creation date
    #     """

    #     url = 'https://api.github.com/graphql'
    #     headers = {'Authorization': 'token %s' % self.GITHUB_API_KEY}
    #     cursor = "null"
    #     pullReqTime = []
    #     numReviews = []
    #     count = 0

    #     while count < 100:

    #         query = """
    #         {
    #           repository(owner: "%s", name: "%s") {
    #                  pullRequests(first: 100, after: %s) {
    #                     edges {
    #                         cursor
    #                         node {
    #                           number
    #                           createdAt
    #                           reviews(first: 100) {
    #                             edges {
    #                               node {
    #                                 createdAt
    #                                 author {
    #                                   login
    #                                 }
    #                                 createdAt
    #                               }
    #                             }
    #                           }
    #                         }
    #                         cursor
    #                     }
    #                 }
    #             }
    #         }
    #         """ % (owner, repo, cursor)

    #         request = requests.post(url, json={'query': query}, headers=headers)
    #         if request.status_code == 200:
    #             data = request.json()
    #         else:
    #             raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

    #         pullReqs = data['data']['repository']['pullRequests']['edges']
    #         count += 1
    #         for i in pullReqs:
    #             pullReqTime = np.append(pullReqTime, i['node']['createdAt'])
    #             numReviews = np.append(numReviews, len(i['node']['reviews']['edges']))
    #         if len(data['data']['repository']['pullRequests']['edges']) < 100:
    #             break
    #         else:
    #             cursor = '"{}"'.format(data['data']['repository']['pullRequests']['edges'][-1]['cursor'])

    #     return pd.DataFrame({'date': pullReqTime, 'code_reviews': numReviews})
