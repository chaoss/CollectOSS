#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import json
from gitim_repourl import *
import logging

theLogger = logging.getLogger('iterator_log')
theLogger.setLevel(logging.DEBUG)
logFileHandler = logging.FileHandler("iterator.log")
logFileHandler.setLevel(logging.DEBUG)
#theLogger.basicConfig(filename='example.log',filemode = 'w',level=theLogger.DEBUG)

projects_file = open('repos-orgs-to-get.json')

project_json = json.load(projects_file)

projects = []
repos = []
## Inserting a field name row at the top, because I love the people.
projects_pooping = []

for project in project_json:
    url = project['projectRepository']
    slash_count = 0
    for char in url:
        if char == '/':
            slash_count += 1
    ## TODO: I cleaned up the urls by hand so nothing ENDS is a "/" 
    ## Need to add that logic in here, just to clean up URLs with trailing slashes. 

    if slash_count == 3:
        # print(project['projectName'], ": project")
        try:
            projects.append((project['projectRepository'][19:], project['projectName'], project['projectDescription'], project['projectWebsite']))
            theLogger.debug((project['projectRepository'][19:], project['projectName'], project['projectDescription'], project['projectWebsite']))
        except KeyError as e:
            projects_pooping.append((project['projectName'], project['projectDescription'], project['projectRepository'], 'none'))
            projects.append((project['projectName'], project['projectDescription'], project['projectRepository'], 'none'))
            # I don't know why the order is different above ... but it seems to work right ? 
            #projects.append((project['projectRepository'], project['projectName'], project['projectDescription'], 'none'))
            theLogger.debug(e)
    if slash_count == 4:
        try:
            repos.append((project['projectName'], project['projectDescription'], project['projectRepository'], project['projectWebsite']))
            projects.append(('Standalone_Repository', 'No_Description', project['projectRepository'], project['projectWebsite']))
        except KeyError as e:
            repos.append((project['projectName'], project['projectDescription'], project['projectRepository'], ''))
            projects.append((project['projectName'], project['projectDescription'], project['projectRepository'], 'none'))

            theLogger.debug(e)
    # else:
    #     print(project['projectName'], ": DON'T CARE")

repos_file = open('repos.csv', 'w')
repos_sql = open('repo_groups.sql','w')

with open('projects.csv', 'w') as projects_file:
    projects_file.write("Project_Name, Project_Name, repo_url, project_url\n")
    for project in projects:
        projects_file.write("{},{},\"{}\",{}\n".format(project[0], project[1], project[2], project[3]))
        theLogger.debug(project[1])
        #project_id+=1

with open('projects_poop.csv', 'w') as projects_poop_file:
    for poo in projects_pooping:
        projects_poop_file.write("{},{},\"{}\",{}\n".format(project[0], project[1], project[2], project[3]))
        theLogger.debug(project[1])

project_id = 22000
repo_id = 22000

with open('repos.csv', 'w') as repos_file:
    #repos_file.write("repos_id, projects_id, repo_url, path, facade_name, added, status, name, description, project_url\n")
    for repo in repos:
        repos_file.write("{},{},{},NULL,NULL,,New,\"{}\",\"{}\",\"{}\"\n".format(repo_id, project_id, repo[2], repo[0], repo[1], repo[3]))
        # repos_sql.write("INSERT INTO \"augur_data\".\"repo_groups\"(\"rg_name\", \"rg_description\", \"rg_website\", \"rg_recache\", \"rg_last_modified\", \"rg_type\", \"tool_source\", \"tool_version\", \"data_source\", \"data_collection_date\") VALUES ('Twitter', 'All of the Twitter Repositories', 'http://www.twitter.com', 0, CURRENT_TIMESTAMP, NULL, 'Data Load', 'Data Load', 'Old Twitter Repo List', CURRENT_TIMESTAMP);\n")
        project_id+=1
        repo_id+=1

# with open('repo_groups.sql','w') as repos_sql:
#     for repo in repos: 
#         repos_sql.write("INSERT INTO \"augur_data\".\"repo_groups\"(\"rg_name\", \"rg_description\", \"rg_website\", \"rg_recache\", \"rg_last_modified\", \"rg_type\", \"tool_source\", \"tool_version\", \"data_source\", \"data_collection_date\") VALUES ('Twitter', 'All of the Twitter Repositories', 'http://www.twitter.com', 0, CURRENT_TIMESTAMP, NULL, 'Data Load', 'Data Load', 'Old Twitter Repo List', CURRENT_TIMESTAMP);\n")

try:
    os.system('python -m gitim_repourl -t {} --project_id {} --repo_id {}'.format('your github api key here', project_id, repo_id))
except Exception as e:
    theLogger.debug(e)
    theLogger.debug(project_id)
    theLogger.debug(repo_id)
    
