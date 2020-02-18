#SPDX-License-Identifier: MIT
"""
Creates routes for the manager
"""

import logging
import time
import subprocess
import requests
from ..cli import db
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
        conn = db.get_db_connection(server._augur)
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
                    success.append(repo_name)
                else:
                    errors.append(repo_name)
            else:
                errors.append(repo)

        summary = json.dumps({'sucess':success, 'failures': errors})
        print(summary)
        return Response(response=summary,
                        status=200,
                        mimetype="application/json")

    
    @server.app.route('/{}/add-repo-group'.format(server.api_version), methods=['POST'])
    def add_repo_group():
        """ creates a new augur repo group and adds to it the given organization or user's repos
            takes an organization or user name 
        """
        conn = db.get_db_connection(server._augur)
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
        else: res = "created repo group"
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
        repogit = "https://github.com/" + given_org + "/" + reponame
        try:
            pd.read_sql(insert, self.conn, params={'repo_group_id': int(orgid), 'repo_git': repogit})
        except exc.ResourceClosedError:
            return True
        else:
            return False
        
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