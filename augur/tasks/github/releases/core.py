#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from augur.tasks.github.util.github_task_session import *
from augur.application.db.models import *
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.github.util.gh_graphql_entities import hit_api_graphql, request_graphql_dict
from augur.application.db.util import execute_session_query


def get_release_inf(session, repo_id, release, tag_only):
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
            'tag_only': tag_only
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
            'tag_only': tag_only
        }
        if date:
            release_inf['release_created_at'] = date

    return release_inf


def insert_release(session, repo_id, owner, release, tag_only = False):

    # Get current table values
    session.logger.info('Getting release table values\n')
    query = session.query(Release.release_id).filter(Release.repo_id == repo_id)
    release_id_data = execute_session_query(query, 'all')#pd.read_sql(release_id_data_sql, self.db, params={'repo_id': repo_id})
    release_id_data = [str(r_id).strip() for r_id in release_id_data]#release_id_data.apply(lambda x: x.str.strip())

    # Put all data together in format of the table
    session.logger.info(f'Inserting release for repo with id:{repo_id}, owner:{owner}, release name:{release["name"]}\n')
    release_inf = get_release_inf(session, repo_id, release, tag_only)

    #Do an upsert
    session.insert_data(release_inf,Release,['release_id'])

    session.logger.info(f"Inserted info for {owner}/{repo_id}/{release['name']}\n")

    return


def get_query(session, owner, repo, tag_only):
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
        """ % (owner, repo, 100)
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
        """ % (owner, repo, 100)

    session.logger.debug(f"query is: {query}")

    return query



def fetch_data(session, github_url, repo_id, tag_only = False):

    session.logger.info("Beginning filling the releases model for repo: " + github_url + "\n")

    owner, repo = get_owner_repo(github_url)

    url = 'https://api.github.com/graphql'

    query = get_query(session,owner, repo, tag_only)

    # Hit the graphql endpoint
    session.logger.info("Hitting endpoint: {} ...\n".format(url))
    data = request_graphql_dict(session, url, query)

    if 'data' in data:
        data = data['data']['repository']

    data['owner'] = owner

    return data

def releases_model(session, repo_git, repo_id):

    try:
        data = fetch_data(session,repo_git, repo_id)
    except Exception as e:
        session.logger.info(f"Ran into problem when fetching data for repo {repo_git}: {e}")
        return

    session.logger.info("repository value is: {}\n".format(data))
    if 'releases' in data:
        if 'edges' in data['releases'] and data['releases']['edges']:
            for n in data['releases']['edges']:
                if 'node' in n:
                    release = n['node']
                    #self.insert_release(task, repo_id, data['owner'], release)
                    insert_release(session, repo_id, data['owner'], release)
                else:
                    session.logger.info("There's no release to insert. Current node is not available in releases: {}\n".format(n))
        elif 'edges' in data['releases'] and not data['releases']['edges']:
            session.logger.info("Searching for tags instead of releases...")
            data = fetch_data(session,repo_git, repo_id,True)
            session.logger.info("refs value is: {}\n".format(data))
            if 'refs' in data:
                if 'edges' in data['refs']:
                    for n in data['refs']['edges']:
                        if 'node' in n:
                            release = n['node']
                            #self.insert_release(task, repo_id, data['owner'], release, True)
                            insert_release(session, repo_id, data['owner'], release, True)
                        else:
                            session.logger.info("There's no release to insert. Current node is not available in releases: {}\n".format(n))
                else:
                    session.logger.info("There are no releases to insert for current repository: {}\n".format(data))
            else:
                session.logger.info("There are no refs in data: {}\n".format(data))
        else:
            session.logger.info("There are no releases to insert for current repository: {}\n".format(data))
    else:
        session.logger.info("Graphql response does not contain repository: {}\n".format(data))