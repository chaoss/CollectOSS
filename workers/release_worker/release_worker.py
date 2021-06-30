#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from workers.worker_base import Worker

#TODO - fully edit to match releases
class ReleaseWorker(Worker):
    """
    Worker that collects Repository Releases data from the Github API
    and stores it in our database.

    :param task: most recent task the broker added to the worker's queue
    :param config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config={}):

        worker_type = "release_worker"

        # Define what this worker can be given and know how to interpret
        given = [['github_url']]
        models = ['releases']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['releases']
        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        # Define data collection info
        self.tool_source = 'Release Worker'
        self.tool_version = '1.0.0'
        self.data_source = 'GitHub API'

    def get_release_inf(self, repo_id, release, tag_only):
        if not tag_only:
            name = "" if release['author']['name'] is None else release['author']['name']
            company = "" if release['author']['company'] is None else release['author']['company']
            author = name + '_' + company
            release_inf = {
                'release_id': release['id'],
                'repo_id': repo_id,
                'release_name': release['name'],
                'release_description': release['description'],
                'release_author': author,
                'release_created_at': release['createdAt'],
                'release_published_at': release['publishedAt'],
                'release_updated_at': release['updatedAt'],
                'release_is_draft': release['isDraft'],
                'release_is_prerelease': release['isPrerelease'],
                'release_tag_name': release['tagName'],
                'release_url': release['url'],
                'tag_only': tag_only,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }
        else:
            if 'tagger' in release['target']:
                if 'name' in release['target']['tagger']:
                    name = release['target']['tagger']['name']
                else:
                    name = ""
                if 'email' in release['target']['tagger']:
                    email = '_' + release['target']['tagger']['email']
                else:
                    email = ""
                author = name + email
                if 'date' in release['target']['tagger']:
                    date = release['target']['tagger']['date']
                else:
                    date = ""
            else:
                author = ""
                date = ""
            release_inf = {
                'release_id': release['id'],
                'repo_id': repo_id,
                'release_name': release['name'],
                'release_author': author,
                'release_tag_name': release['name'],
                'tag_only': tag_only,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }
            if date:
                release_inf['release_created_at'] = date

        return release_inf


    def insert_release(self, task, repo_id, owner, release, tag_only = False):

        # Get current table values
        release_id_data_sql = s.sql.text("""
            SELECT releases.release_id
            FROM releases
            WHERE repo_id = :repo_id
        """)
        self.logger.info(f'Getting release table values with the following PSQL query: \n{release_id_data_sql}\n')
        release_id_data = pd.read_sql(release_id_data_sql, self.db, params={'repo_id': repo_id})
        release_id_data = release_id_data.apply(lambda x: x.str.strip())

        # Put all data together in format of the table
        self.logger.info(f'Inserting release for repo with id:{repo_id}, owner:{owner}, release name:{release["name"]}\n')
        release_inf = self.get_release_inf(repo_id, release, tag_only)

        if release_id_data.size > 0 and release['id'] in release_id_data.values:
            result = self.db.execute(self.releases_table.update().where(
                self.releases_table.c.release_id==release['id']).values(release_inf))
            self.logger.info(f"Release {release['id']} updated into releases table\n")
        else:
            result = self.db.execute(self.releases_table.insert().values(release_inf))
            self.logger.info(f"Release {release['id']} inserted into releases table\n")
            self.logger.info(f"Primary Key inserted into releases table: {result.inserted_primary_key}\n")
        self.results_counter += 1

        self.logger.info(f"Inserted info for {owner}/{repo_id}/{release['name']}\n")

        #Register this task as completed
        self.register_task_completion(task, repo_id, "releases")
        return

    def get_query(self, owner, repo, tag_only):
        if not tag_only:
            query = """
                {
                    repository(owner:"%s", name:"%s"){
                        id
                        releases(orderBy: {field: CREATED_AT, direction: ASC}, last: %d) {
                            edges {
                                node {
                                    name
                                    publishedAt
                                    createdAt
                                    description
                                    id
                                    isDraft
                                    isPrerelease
                                    tagName
                                    url
                                    updatedAt
                                    author {
                                        name
                                        company
                                    }
                                }
                            }
                        }
                    }
                }
            """ % (owner, repo, 10)
        else:
            query = """
                {
                    repository(owner:"%s", name:"%s"){
                        id
                        refs(refPrefix: "refs/tags/", last: %d){
                            edges {
                                node {
                                    name
                                    id
                                    target {
                                        ... on Tag {
                                            tagger {
                                                name
                                                email
                                                date
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            """ % (owner, repo, 10)

        return query

    def fetch_data(self, task, repo_id, tag_only = False):

        github_url = task['given']['github_url']

        self.logger.info("Beginning filling the releases model for repo: " + github_url + "\n")

        owner, repo = self.get_owner_repo(github_url)

        url = 'https://api.github.com/graphql'

        query = self.get_query(owner, repo, tag_only)

        # Hit the graphql endpoint and retry 3 times in case of failure
        num_attempts = 0
        success = False
        while num_attempts < 3:
            self.logger.info("Hitting endpoint: {} ...\n".format(url))
            r = requests.post(url, json={'query': query}, headers=self.headers)
            self.update_gh_rate_limit(r)

            try:
                data = r.json()
            except:
                data = json.loads(json.dumps(r.text))

            if 'errors' in data:
                self.logger.info("Error!: {}".format(data['errors']))
                if data['errors'][0]['message'] == 'API rate limit exceeded':
                    self.update_gh_rate_limit(r)
                    continue

            if 'data' in data:
                success = True
                data = data['data']['repository']
                break
            else:
                self.logger.info("Request returned a non-data dict: {}\n".format(data))
                if data['message'] == 'Not Found':
                    self.logger.info("Github repo was not found or does not exist for endpoint: {}\n".format(url))
                    break
                if data['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                    self.update_gh_rate_limit(r, temporarily_disable=True)
                    continue
                if data['message'] == 'Bad credentials':
                    self.update_gh_rate_limit(r, bad_credentials=True)
                    continue
            num_attempts += 1
        if not success:
            self.register_task_failure(task, repo_id, "Failed to hit endpoint: {}".format(url))
            return

        data['owner'] = owner

        return data


    def releases_model(self, task, repo_id):

        data = self.fetch_data(task, repo_id)

        self.logger.info("repository value is: {}\n".format(data))
        if 'releases' in data:
            if 'edges' in data['releases'] and data['releases']['edges']:
                for n in data['releases']['edges']:
                    if 'node' in n:
                        release = n['node']
                        self.insert_release(task, repo_id, data['owner'], release)
                    else:
                        self.logger.info("There's no release to insert. Current node is not available in releases: {}\n".format(n))
            elif 'edges' in data['releases'] and not data['releases']['edges']:
                self.logger.info("Searching for tags instead of releases...")
                data = self.fetch_data(task, repo_id, True)
                self.logger.info("refs value is: {}\n".format(data))
                if 'refs' in data:
                    if 'edges' in data['refs']:
                        for n in data['refs']['edges']:
                            if 'node' in n:
                                release = n['node']
                                self.insert_release(task, repo_id, data['owner'], release, True)
                            else:
                                self.logger.info("There's no release to insert. Current node is not available in releases: {}\n".format(n))
                    else:
                        self.logger.info("There are no releases to insert for current repository: {}\n".format(data))
                else:
                    self.logger.info("There are no refs in data: {}\n".format(data))
            else:
                self.logger.info("There are no releases to insert for current repository: {}\n".format(data))
        else:
            self.logger.info("Graphql response does not contain repository: {}\n".format(data))
