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

projects_file = open('value-projects.json')

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
        except KeyError as e:
            repos.append((project['projectName'], project['projectDescription'], project['projectRepository'], ''))
            theLogger.debug(e)
    # else:
    #     print(project['projectName'], ": DON'T CARE")

repos_file = open('repos.csv', 'w')


with open('projects.csv', 'w') as projects_file:
    for project in projects:
        projects_file.write("{},{},\"{}\",{}\n".format(project[0], project[1], project[2], project[3]))
        theLogger.debug(project[1])
        #project_id+=1

with open('projects_poop.csv', 'w') as projects_poop_file:
    for poo in projects_pooping:
        projects_poop_file.write("{},{},\"{}\",{}\n".format(project[0], project[1], project[2], project[3]))
        theLogger.debug(project[1])

project_id = 20
repo_id = 21000

with open('repos.csv', 'w') as repos_file:
    repos_file.write("repos_id, projects_id, repo_url, path, facade_name, added, status, name, description, project_url\n")
    for repo in repos:
        repos_file.write("{},{},{},NULL,NULL,2019-03-08 12:36:33.236898,New,\"{}\",\"{}\",\"{}\"\n".format(repo_id, project_id, repo[2], repo[0], repo[1], repo[3]))
        project_id+=1
        repo_id+=1

try:
    os.system('python -m gitim_repourl -t {} --project_id {} --repo_id {}'.format('06b79d598e4a27113a0c6341241493530948912f', project_id, repo_id))
except Exception as e:
    theLogger.debug(e)
    theLogger.debug(project_id)
    theLogger.debug(repo_id)
    
