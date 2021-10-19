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
from augur.config import AugurConfig
import os 
import traceback 

logger = logging.getLogger(__name__)

def create_routes(server):

    @server.app.route('/{}/add-repos'.format(server.api_version), methods=['POST'])
    def add_repos():
        """ returns list of successfully inserted repos and repos that caused an error
            adds repos belonging to any user or group to an existing augur repo group
            'repos' are in the form org/repo, user/repo, or maybe even a full url 
        """
        if authenticate_request(server.augur_app, request):
            group = request.json['group']
            repo_manager = Repo_insertion_manager(group, server.augur_app.database)
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

            status_code = 200
            summary = {'repos_inserted': success, 'repos_not_inserted': errors}
            summary = json.dumps(summary)
        else:
            status_code = 401
            summary = json.dumps({'error': "Augur API key is either missing or invalid"})

        return Response(response=summary,
                        status=status_code,
                        mimetype="application/json")

    @server.app.route('/{}/create-repo-group'.format(server.api_version), methods=['POST'])
    def create_repo_group():
        if authenticate_request(server.augur_app, request):
            group = request.json['group']
            repo_manager = Repo_insertion_manager(group, server.augur_app.database)
            summary = {}
            summary['errors'] = []
            summary['repo_groups_created'] = []

            if group == '':
                summary['errors'].append("invalid group name")
                return Response(response=summary, status=200, mimetype="application/json")
                
            try:
                group_id = repo_manager.get_org_id()
            except TypeError:
                try:
                    group_id = repo_manager.insert_repo_group()
                except TypeError:
                    summary['errors'].append("couldn't create group")
                else: 
                    summary['repo_groups_created'].append({"repo_group_id": group_id, "rg_name": group})
            else:
                summary['errors'].append("group already exists")

            summary = json.dumps(summary)
            status_code = 200
        else:
            status_code = 401
            summary = json.dumps({'error': "Augur API key is either missing or invalid"})

        return Response(response=summary, 
                        status=status_code, 
                        mimetype="application/json")

    @server.app.route('/{}/import-org'.format(server.api_version), methods=['POST'])
    def add_repo_group():
        """ creates a new augur repo group and adds to it the given organization or user's repos
            takes an organization or user name 
        """
        if authenticate_request(server.augur_app, request):
            group = request.json['org']
            repo_manager = Repo_insertion_manager(group, server.augur_app.database)
            summary = {}
            summary['group_errors'] = []
            summary['failed_repo_records'] = []
            summary['repo_records_created'] = []
            group_exists = False
            try:
                #look for group in augur db
                group_id = repo_manager.get_org_id()
            except TypeError:
                #look for group on github
                if repo_manager.group_exists_gh():
                    try:
                        group_id = repo_manager.insert_repo_group()
                    except TypeError:
                        summary['group_errors'].append("failed to create group")
                    else:
                        group_exists = True
                else:
                    summary['group_errors'].append("could not locate group in database or on github")
            else:
                group_exists = True

            if group_exists:
                summary['group_id'] = str(group_id)
                summary['rg_name'] = group
                try:
                    repos_gh = repo_manager.fetch_repos()
                    repos_in_augur = repo_manager.get_existing_repos(group_id)
                    repos_db_set = set()
                    for name in repos_in_augur:
                        #repo_git is more reliable than repo name, so we'll just grab everything after the last slash 
                        name = (name['repo_git'].rsplit('/', 1)[1])
                        repos_db_set.add(name)
                    repos_to_insert = set(repos_gh) - repos_db_set

                    for repo in repos_to_insert:
                        try:
                            repo_id = repo_manager.insert_repo(group_id, group, repo)
                        except exc.SQLAlchemyError:
                            summary['failed_repo_records'].append(repo)
                        else:
                            summary['repo_records_created'].append(get_inserted_repo(group_id, repo_id, repo, group, repo_manager.github_urlify(group, repo)))
                except requests.ConnectionError:
                    summary['group_errors'] = "failed to find the group's child repos"
                    logger.debug(f'Error is: {e}.')
                except Exception as e: 
                    logger.debug(f'Error is: {e}.')

            status_code = 200
            summary = json.dumps(summary)
        else:
            status_code = 401
            summary = json.dumps({'error': "Augur API key is either missing or invalid"})

        return Response(response=summary,
                        status=status_code,
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
    ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self, organization_name, database_connection):
        #self.initialize_logging()
        self.org = organization_name
        self.db = database_connection
        ## added for keys
        self._root_augur_dir = Repo_insertion_manager.ROOT_AUGUR_DIR
        self.augur_config = AugurConfig(self._root_augur_dir)
        ##########


    def get_existing_repos(self, group_id):
        """returns repos belonging to repogroup in augur db"""
        select_repos_query = s.sql.text("""
            SELECT repo_git from augur_data.repo
            WHERE repo_group_id = :repo_group_id
        """)
        select_repos_query = select_repos_query.bindparams(repo_group_id = group_id)
        result = self.db.execute(select_repos_query)
        return result.fetchall()

## This doesn't permit importing of an individual's repo, as they don't show up under "orgs"
#    def group_exists_gh(self):
#        url = url = "https://api.github.com/orgs/{}".format(self.org)
#        res = requests.get(url).json()
#        try:
#            if res['message'] == "Not Found":
#                return False
#        except KeyError:
#            return True

## Revised Version of Method
    def group_exists_gh(self):
        url = url = "https://api.github.com/orgs/{}".format(self.org)
        ## attempting to add key due to rate limiting
        gh_api_key = self.augur_config.get_value('Database', 'key')
        self.headers = {'Authorization': 'token %s' % gh_api_key}
        #r = requests.get(url=cntrb_url, headers=self.headers)
####### Original request code
#        res = requests.get(url).json()
########
        res = requests.get(url=url, headers=self.headers).json()
        try:
            if res['message'] == "Not Found":
                url = url = "https://api.github.com/users/{}".format(self.org) 
                res = requests.get(url=url, headers=self.headers).json()
                if res['message'] == "Not Found":
                    return False
        except KeyError:
            return True

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
        gh_api_key = self.augur_config.get_value('Database', 'key')
        self.headers = {'Authorization': 'token %s' % gh_api_key} 
        repos = []
        page = 1
        url = self.paginate(page)
        res = requests.get(url, headers=self.headers).json()
        while res:
            for repo in res:
                repos.append(repo['name'])
            page += 1
            res = requests.get(self.paginate(page)).json()
        return repos

## Modified pagination to account for github orgs that look like orgs but are actually users. 
    def paginate(self, page):
### Modified here to incorporate the use of a GitHub API Key
        gh_api_key = self.augur_config.get_value('Database', 'key')
        self.headers = {'Authorization': 'token %s' % gh_api_key}    
        url = "https://api.github.com/orgs/{}/repos?per_page=100&page={}"
        res = requests.get(url, headers=self.headers).json()
        if res['message'] == "Not Found":
            url = "https://api.github.com/users/{}/repos?per_page=100&page={}" 
            res = requests.get(url=url, headers=self.headers).json()
        return url.format(self.org, str(page))


        #r = requests.get(url=cntrb_url, headers=self.headers)
####### Original request code
#        res = requests.get(url).json()
########
        res = requests.get(url=url, headers=self.headers).json()



#        url = "https://api.github.com/orgs/{}/repos?per_page=100&page={}"
#        res = requests.get(url).json()
#        if res['message'] == "Not Found":
#            url = "https://api.github.com/users/{}/repos?per_page=100&page={}" 
#            res = requests.get(url).json()
#        return url.format(self.org, str(page))

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

def authenticate_request(augur_app, request):

    # do I like doing it like this? not at all
    # do I have the time to implement a better solution right now? not at all
    user = augur_app.config.get_value('Database', 'user')
    password = augur_app.config.get_value('Database', 'password')
    host = augur_app.config.get_value('Database', 'host')
    port = augur_app.config.get_value('Database', 'port')
    dbname = augur_app.config.get_value('Database', 'name')

    DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
    )

    operations_db = s.create_engine(DB_STR, poolclass=s.pool.NullPool)

    update_api_key_sql = s.sql.text("""
        SELECT value FROM augur_operations.augur_settings WHERE setting='augur_api_key';
    """)

    retrieved_api_key = operations_db.execute(update_api_key_sql).fetchone()[0]

    try:
        given_api_key = request.json['augur_api_key']
    except KeyError:
        return False

    if given_api_key == retrieved_api_key and given_api_key != "invalid_key":
        return True
    else:
        return False
