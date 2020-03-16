#SPDX-License-Identifier: MIT
"""
Creates routes for the manager
"""

import logging
import time
import requests
import sqlalchemy as s
from sqlalchemy import exc
from flask import request, Response
import json

def create_manager_routes(server):

    @server.app.route('/{}/add-repos'.format(server.api_version), methods=['POST'])
    def add_repos():
        """ returns list of successfully inserted repos and repos that caused an error
            adds repos belonging to any user or group to an existing augur repo group
            'repos' are in the form org/repo, user/repo, or maybe even a full url 
        """
        db_connection = get_db_engine(server._augur).connect()
        group = request.json['group']
        repo_manager = Repo_insertion_manager(group, db_connection)
        group_id = repo_manager.get_org_id()
        errors = {}
        errors['invalid_inputs'] = []
        errors['failed_records'] = []
        success = []
        repos = request.json['repos']
        for repo in repos:
            url = Git_string(repo)
            url.clean_full_string()
            try: #need to test because we require org/repo or full git url
                url.is_repo()
                repo_name = url.get_repo_name()
                repo_parent = url.get_repo_organization()
            except ValueError:
                errors['invalid_inputs'].append(repo)
            else:   
                try:
                    repo_id = repo_manager.insert_repo(group_id, repo_parent, repo_name)
                except exc.SQLAlchemyError:
                    errors['failed_records'].append(repo_name)
                else: 
                    success.append(get_inserted_repo(group_id, repo_id, repo_name, group, repo_manager.github_urlify(repo_parent, repo_name)))

        summary = {'repos_inserted': success, 'repos_not_inserted': errors}
        summary = json.dumps(summary)
        return Response(response=summary,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/add-repo-group'.format(server.api_version), methods=['POST'])
    def add_repo_group():
        """ creates a new augur repo group and adds to it the given organization or user's repos
            takes an organization or user name 
        """
        conn = get_db_engine(server._augur)
        group = request.json['group']
        repo_manager = Repo_insertion_manager(group, conn)
        summary = {}
        summary['group_errors'] = []
        summary['failed_repo_records'] = []
        summary['repo_records_created'] = []
        
        try:
            group_id = repo_manager.get_org_id()
        except TypeError:
            try:
                group_id = repo_manager.insert_repo_group()
            except TypeError:
                summary['group_errors'].append("failed to create group")
            else:
                group_exists = True
        else:
            group_exists = True

        if group_exists:
            summary['group_id'] = str(group_id)
            summary['rg_name'] = group
            try:
                repos = repo_manager.fetch_repos()
                i = 0
                for repo in repos:
                    try:
                        i += 1
                        print(str(i))
                        repo_id = repo_manager.insert_repo(group_id, group, repo)
                    except exc.SQLAlchemyError:
                        summary['failed_repo_records'].append(repo)
                    else:
                        summary['repo_records_created'].append(get_inserted_repo(group_id, repo_id, repo, group, repo_manager.github_urlify(group, repo)))
            except requests.ConnectionError:
                summary['group_errors'] = "failed to find the group's child repos"

        summary = json.dumps(summary)
        return Response(response=summary,
                        status=200,
                        mimetype="application/json")
    
    def get_inserted_repo(groupid, repoid, reponame, groupname, url):
        inserted_repo={}
        inserted_repo['repo_group_id'] = str(groupid)
        inserted_repo['repo_id'] = str(repoid)
        inserted_repo['repo_name'] = reponame
        inserted_repo['rg_name'] = groupname
        inserted_repo['url'] = url
        return inserted_repo

class Repo_insertion_manager():
    def __init__(self, organization_name, database_connection):
        self.org = organization_name
        self.db = database_connection

    def insert_repo(self, orgid, given_org, reponame):
        """creates a new repo record"""
        insert_repo_query = s.sql.text("""
            INSERT INTO augur_data.repo(repo_group_id, repo_git, repo_status,
                tool_source, tool_version, data_source, data_collection_date)
            VALUES (:repo_group_id, :repo_git, 'New', 'CLI', 1.0, 'Git', CURRENT_TIMESTAMP)
            RETURNING repo_id
        """)
        repogit = self.github_urlify(given_org, reponame)
        insert_repo_query = insert_repo_query.bindparams(repo_group_id = int(orgid), repo_git = repogit)
        result = self.db.execute(insert_repo_query).fetchone()
        return result['repo_id']

    def github_urlify(self, org, repo):
        return "https://github.com/" + org + "/" + repo

    def get_org_id(self):
        select_group_query = s.sql.text("""
            SELECT repo_group_id
            FROM augur_data.repo_groups
            WHERE rg_name = :group_name
        """)
        select_group_query = select_group_query.bindparams(group_name = self.org)
        result = self.db.execute(select_group_query)
        row = result.fetchone()
        return row['repo_group_id']
        
    def insert_repo_group(self):
        """creates a new repo_group record and returns its id"""
        insert_group_query = s.sql.text("""
            INSERT INTO augur_data.repo_groups(rg_name, rg_description, rg_website, rg_recache, rg_last_modified, rg_type, 
                tool_source, tool_version, data_source, data_collection_date)
            VALUES (:group_name, '', '', 1, CURRENT_TIMESTAMP, 'Unknown', 'Loaded by user', 1.0, 'Git', CURRENT_TIMESTAMP)
            RETURNING repo_group_id
        """)
        insert_group_query = insert_group_query.bindparams(group_name = self.org)
        result = self.db.execute(insert_group_query)
        row = result.fetchone()
        return row['repo_group_id']

    def fetch_repos(self):
        """uses the github api to return repos belonging to the given organization"""
        repos = []
        page = 1
        url = self.paginate(page)
        res = requests.get(url).json()
        while res:
            for repo in res:
                repos.append(repo['name'])
            page += 1
            res = requests.get(self.paginate(page)).json()
        return repos

    def paginate(self, page):
        url = "https://api.github.com/orgs/{}/repos?per_page=100&page={}"
        return url.format(self.org, str(page))

        

class Git_string():
    """ represents possible repo, org or username arguments """
    def __init__(self, string_to_process):
        self.name = string_to_process

    def clean_full_string(self):
        """remove trailing slash, protocol, and source if present"""
        org = self.name
        if org.endswith('/'):
            org = org[:-1]
        if org.startswith('https://'):
            org = org[8:]
            slash_index = org.find('/')
            org = org[slash_index+1:]
        if org.startswith('git://'):
            org = org[6:]
            slash_index = org.find('/') 
            org = org[slash_index+1:]
        self.name = org

    def is_repo(self):
        """test for org/repo or user/repo form"""
        slash_count = 0
        for char in self.name:
            if char == '/':
                slash_count += 1
        if slash_count == 1:
            return
        else:
            raise ValueError
        
    def get_repo_organization(self):
        org = self.name
        return org[:org.find('/')]

    def get_repo_name(self):
        repo = self.name
        return repo[repo.find('/')+1:]

def get_db_engine(app):

    user = app.read_config('Database', 'user')
    password = app.read_config('Database', 'password')
    host = app.read_config('Database', 'host')
    port = app.read_config('Database', 'port')
    dbname = app.read_config('Database', 'name')

    DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
    )

    return s.create_engine(DB_STR, poolclass=s.pool.NullPool)
