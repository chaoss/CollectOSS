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
        self.tool_version = '0.0.1'
        self.data_source = 'GitHub API'

    def releases_model(self, task, repo_id):

        github_url = task['given']['github_url']

        self.logger.info("Beginning filling the releases model for repo: " + github_url + "\n")

        owner, repo = self.get_owner_repo(github_url)

        url = 'https://api.github.com/graphql'

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
                if data['errors']['message'] == 'API rate limit exceeded':
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

        if 'repository' in data:
            if 'releases' in data['repository']:
                if 'edges' in data['repository']['releases']:
                    for n in data['repository']['releases']['edges']:
                        if 'node' in n:
                            release = n['node']
                            insert_release(self, repo_id, owner, release)
                        self.logger.info("There's no release to insert. Current node is not available in releases: {}\n".format(n))
                self.logger.info("There are no releases to insert for current repository: {}\n".format(data))
            self.logger.info("Graphql response does not contain releases: {}\n".format(data))
        self.logger.info("Graphql response does not contain repository: {}\n".format(data))

    def insert_release(self, repo_id, owner, release):
        author = release['author']['name']+'_'+release['author']['company']
        # Put all data together in format of the table
        self.logger.info(f'Inserting release for repo with id:{repo_id}, owner:{owner}, release name:{release["name"]}\n')
        release_inf = {
            'release_id': release['id'],
            'repo_id': repo_id,
            'release_name': release['name'],
            'release_description': release['description'],
            'release_author': release['author'],
            'release_created_at': release['createdAt'],
            'release_published_at': release['publishedAt'],
            'release_updated_at': release['updatedAt'],
            'release_is_draft': release['isDraft'],
            'release_is_prerelease': release['isPrerelease'],
            'release_tag_name': release['tagName'],
            'release_url': release['url'],
            'tool_source': self.tool_source,
            'tool_version': self.tool_version,
            'data_source': self.data_source
        }

        result = self.db.execute(self.releases_table.insert().values(release_inf))
        self.logger.info(f"Primary Key inserted into releases table: {result.inserted_primary_key}\n")
        self.results_counter += 1

        self.logger.info(f"Inserted info for {owner}/{repo}/{release['name']}\n")

        #Register this task as completed
        self.register_task_completion(task, release_id, "releases")
        return


