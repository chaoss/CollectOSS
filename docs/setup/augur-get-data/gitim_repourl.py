#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function
from getpass import getpass
from argparse import ArgumentParser
from os import chdir, path, makedirs, pardir, environ 
from subprocess import call, Popen
from functools import partial
from platform import python_version_tuple
import os
import logging
import traceback
import sys

logging.basicConfig(filename='gitim.log',filemode = 'w',level=logging.DEBUG)

from github import Github

if python_version_tuple()[0] == u'2':
    input = lambda prompt: raw_input(prompt.encode('utf8')).decode('utf8')

__original_author__ = u'"Samuel Marks", "Mustafa Hasturk" <mustafa.hasturk@yandex.com>'
__original_version__ = '2.0.0'
__derivative_author__ = u'"Carter Landis" <ccarterlandis@gmail.com>, "Sean Goggins" <outdoors@acm.org>'
__derivative_version__ = '0.0.1'


class Gitim():
    def __init__(self):
        print('GitIM is working hard...')

    def set_args(self):
        """ Create parser for command line arguments """
        parser = ArgumentParser(
                usage=u'python -m gitim -u\'\n\t\t\tUsername and password will be prompted.',
                description='Clone all your Github repositories.')
        parser.add_argument('-u', '--user', help='Your github username')
        parser.add_argument('-p', '--password', help=u'Github password')
        parser.add_argument('-t', '--token', help=u'Github OAuth token')
        parser.add_argument('-o', '--org', help=u'Organisation/team. User used by default.')
        parser.add_argument('-d', '--dest', help=u'Destination directory. Created if doesn\'t exist. [curr_dir]')
        parser.add_argument('--nopull', action='store_true', help=u'Don\'t pull if repository exists. [false]')
        parser.add_argument('--shallow', action='store_true', help=u'Perform shallow clone. [false]')
        parser.add_argument('--ssh', action='store_true', help=u'Use ssh+git urls for checkout. [false]')
        parser.add_argument('--repo_id', help=u'Repo id.')
        parser.add_argument('--project_id', help=u'Project id.')
        parser.add_argument('--projects', help=u'List of all projects to get repos for.')
        return parser

    def make_github_agent(self, args):
        """ Create github agent to auth """
        if args.token:
            g = Github(args.token)
        else:
            user = args.user
            password = args.password
            if not user:
                user = input(u'Username: ')
            if not password:
                password = getpass('Password: ')
            if not args.dest:
                args.dest = input(u'Destination: ')
            g = Github(user, password)
        return g

    def clone_main(self):
        """ Clone all repos """
        parser = self.set_args()
        args = parser.parse_args()
        g = self.make_github_agent(args)
        user = g.get_user().login
        # (BadCredentialsException, TwoFactorException, RateLimitExceededException)

        join = path.join
        if args.dest:
            if not path.exists(args.dest):
                makedirs(args.dest)
                print(u'mkdir -p "{}"'.format(args.dest))
            join = partial(path.join, args.dest)

        # with open('good_orgs.txt', 'r') as project_file:
        with open('projects.csv', 'r') as project_file:
            repo_id = int(args.repo_id)
            project_id = int(args.project_id)
            for project in project_file.readlines():
                try:
                    project_tuple = project.split(',')
                    project_tuple[3] = project_tuple[3][0:len(project_tuple[3])-1]
                    logging.debug(project_tuple)

                    get_repos = g.get_organization(project_tuple[0]).get_repos if project_tuple[0] else g.get_user().get_repos
                    with open('repos.csv', 'a') as repos_file:
                        for repo in get_repos():
                            # repos_file.write("{},{},{},NULL,NULL,2019-03-08 12:36:33.236898,New,\"{}\",\"{}\",\"{}\"\n".format(repo_id, project_id, repo[2], repo[0], repo[1], repo[3]))
                            print(project_tuple[3])
                            repos_file.write(("{},{},{},NULL,NULL,,New,\"{}\",{},\"{}\"\n").format(repo_id, project_id, repo.clone_url, project_tuple[1], project_tuple[2], project_tuple[3]))
                            repo_id+=1
                            logging.debug(repo)
                    project_id+=1
                    print(project_id)
                    #project_file.write(("{},{},{},{}\n").format(project_id, project_tuple[1], project_tuple[2], project_tuple[3]))
                    #logging.debug(repo_id, project_id, repo.clone_url, project_tuple[1], project_tuple[2], project_tuple[3])
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    #print("*** print_tb:")
                    logging.debug(traceback.print_tb(exc_traceback, limit=1))
                    formatted_lines = traceback.format_exc().splitlines()
                    logging.debug(formatted_lines[0])
                    logging.debug(formatted_lines[-1])
                    #logging.debug("*** format_exception:")
                    # exc_type below is ignored on 3.5 and later
                    logging.debug(repr(traceback.format_exception(exc_type, exc_value,
                                                          exc_traceback)))
                    #logging.debug("*** extract_tb:")
                    logging.debug(repr(traceback.extract_tb(exc_traceback)))
                    #logging.debug("*** format_tb:")
                    logging.debug(repr(traceback.format_tb(exc_traceback)))
                    #logging.debug("*** tb_lineno:", exc_traceback.tb_lineno) 
                    #logging.debug(traceback.print_exception(e))

if __name__ == '__main__':
    gitim = Gitim()
    gitim.clone_main()
