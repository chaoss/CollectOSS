#SPDX-License-Identifier: MIT
"""
Creates routes for the manager
"""

import logging
import time
import subprocess
import requests
import sqlalchemy as s
from sqlalchemy import exc
import pandas as pd
from flask import request, Response
import json

def create_manager_routes(server):

    @server.app.route('/{}/add-repos'.format(server.api_version), methods=['POST'])
    def add_repos():
        """ returns list of successfully inserted repos and repos that caused an error
            adds repos belonging to any user or group to an existing augur repo group
            'repos' are in the form org/repo, user/repo, or maybe even a full url 
        """
        conn = get_db_connection(server._augur)
        data = request.json
        group = data['group']
        repos = data['repos']
        
        man = Repo_manager(group, conn)
        group_id = man.get_org_id() #we can assume a valid group here
        errors = []
        success = []
        for repo in repos:
            url = Git_string(repo)
            url.clean_full_string()
            if url.is_repo(): #need to test because we requre org/repo or full git url
                repo_name = url.get_repo_name()
                repo_parent = url.org_of_repo()
                if man.insert_repo(group_id, repo_parent, repo_name):
                    r={}
                    r['repo_group_id'] = str(group_id)
                    r['repo_id'] = str(man.repo_id(repo_parent, repo_name))
                    r['repo_name'] = repo_name
                    r['rg_name'] = group
                    r['url'] = man.repo_git(group, repo_name)
                    success.append(r)
                else:
                    errors.append(repo_name)
            else:
                errors.append(repo)

        summary = {'sucess': success, 'failures': errors}
        summary = json.dumps(summary)
        print(summary)
        return Response(response=summary,
                        status=200,
                        mimetype="application/json")

    
    @server.app.route('/{}/add-repo-group'.format(server.api_version), methods=['POST'])
    def add_repo_group():
        """ creates a new augur repo group and adds to it the given organization or user's repos
            takes an organization or user name 
        """
        conn = get_db_connection(server._augur)
        data = request.json
        errors = ""
        group = data['group']
        man = Repo_manager(group, conn)
        group_id = man.get_org_id()
        if group_id < 0:
            try:
                group_id = man.new_org()
            except:
                errors = "failed to create group"
        try:
            repos = man.get_repos()
            for repo in repos:
                man.insert_repo(group_id, group, repo)
        except:
            errors = "failed to add repos to group"
            
        if errors: res = errors
        else: res = json.dumps({'group_id': str(group_id), 'rg_name': group})
        return Response(response=res,
                        status=200,
                        mimetype="application/json")

class Repo_manager():
    def __init__(self, orgname, dbconn):
        self.org = orgname
        self.conn = dbconn

    def insert_repo(self, orgid, given_org, reponame):
        """creates a new repo record"""
        insert = s.sql.text("""
            INSERT INTO augur_data.repo(repo_group_id, repo_git, repo_status,
                tool_source, tool_version, data_source, data_collection_date)
            VALUES (:repo_group_id, :repo_git, 'New', 'CLI', 1.0, 'Git', CURRENT_TIMESTAMP)    
        """)
        repogit = self.repo_git(given_org, reponame)
        try:
            pd.read_sql(insert, self.conn, params={'repo_group_id': int(orgid), 'repo_git': repogit})
        except exc.ResourceClosedError:
            return True
        else:
            return False

    def repo_git(self, org, repo):
        return "https://github.com/" + org + "/" + repo

    def repo_id(self, org, repo_name):
        """returns the repo_id of given repo"""
        select = s.sql.text("""
            SELECT repo_id
            FROM augur_data.repo
            WHERE repo_git = :repogit
            LIMIT 1
        """)
        repo_git = self.repo_git(org, repo_name)
        result = pd.read_sql(select, self.conn, params={'repogit': repo_git})
        return result.values[0][0]


    def get_org_id(self):
        """returns repo_group_id or -1 if not present"""
        select = s.sql.text("""
            SELECT repo_group_id
            FROM augur_data.repo_groups
            WHERE rg_name = :orgname
        """)
        result = pd.read_sql(select, self.conn, params={'orgname': self.org})
        if result.empty:
            return -1
        else:
            return result.values[0][0] 

    def new_org(self):
        """creates a new repo_group record"""
        insert = s.sql.text("""
            INSERT INTO augur_data.repo_groups(rg_name, rg_description, rg_website, rg_recache, rg_last_modified, rg_type, 
                tool_source, tool_version, data_source, data_collection_date)
            VALUES (:neworgname, '', '', 1, CURRENT_TIMESTAMP, 'Unknown', 'Loaded by user', 1.0, 'Git', CURRENT_TIMESTAMP);
        """)
        try:
            pd.read_sql(insert, self.conn, params={'neworgname': self.org})
        except exc.ResourceClosedError:
            return self.get_org_id()
        else:
            raise Exception

    def get_repos(self):
        """return repos belonging to the given organization"""
        repos = []
        page = 1
        url = self.inc_url(page)
        res = requests.get(url).json()
        while res:
            for repo in res:
                repos.append(repo['name'])
            page += 1
            res = requests.get(self.inc_url(page)).json()
        return repos

    def inc_url(self, page):
        url = 'https://api.github.com/orgs/' + self.org +'/repos?per_page=100&page='+ str(page)
        return url

        

class Git_string():
    """ represents possible repo, org or username arguments """
    def __init__(self, arg):
        self.name = arg

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
            return True
        else:
            return False
        
    def org_of_repo(self):
        org = self.name
        return org[:org.find('/')]

    def get_repo_name(self):
        repo = self.name
        return repo[repo.find('/')+1:]

def get_db_connection(app):

    user = app.read_config('Database', 'user', 'AUGUR_DB_USER', 'augur')
    password = app.read_config('Database', 'password', 'AUGUR_DB_PASS', 'password')
    host = app.read_config('Database', 'host', 'AUGUR_DB_HOST', '127.0.0.1')
    port = app.read_config('Database', 'port', 'AUGUR_DB_PORT', '5433')
    dbname = app.read_config('Database', 'database', 'AUGUR_DB_NAME', 'augur')
    schema = app.read_config('Database', 'schema', 'AUGUR_DB_SCHEMA', 'augur_data')

    DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
    )

    return s.create_engine(DB_STR, poolclass=s.pool.NullPool)