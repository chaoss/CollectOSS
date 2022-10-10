#!/usr/bin/env python3

# Copyright 2016-2018 Brian Warner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier:  Apache-2.0

# Git repo maintenance
#
# This script is responsible for cloning new repos and keeping existing repos up
# to date. It can be run as often as you want (and will detect when it's
# already running, so as not to spawn parallel processes), but once or twice per
# day should be more than sufficient. Each time it runs, it updates the repo
# and checks for any parents of HEAD that aren't already accounted for in the
# repos. It also rebuilds analysis data, checks any changed affiliations and
# aliases, and caches data for display.
import sys
import platform
import imp
import time
import datetime
import html.parser
import subprocess
import os
import getopt
import xlsxwriter
import configparser
from .facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author  
from augur.application.db.models.augur_data import *

def git_repo_initialize(session, repo_group_id=None):

    # Select any new git repos so we can set up their locations and git clone
    new_repos = []
    if repo_group_id is None:
        session.update_status('Fetching non-cloned repos')
        session.log_activity('Info','Fetching non-cloned repos')

        query = s.sql.text("""SELECT repo_id,repo_group_id,repo_git FROM repo WHERE repo_status LIKE 'New%'""")
        
        
        #Get data as a list of dicts
        new_repos = session.fetchall_data_from_sql_text(query)#list(cfg.cursor)
    else:
        session.update_status(f"Fetching repos with repo group id: {repo_group_id}")
        session.log_activity('Info',f"Fetching repos with repo group id: {repo_group_id}")

        #query = s.sql.text("""SELECT repo_id,repo_group_id,repo_git FROM repo WHERE repo_status LIKE 'New%'""")
        #cfg.cursor.execute(query)
        result = session.query(Repo).filter('New' in Repo.repo_status).all()

        for repo in result:
            repo_dict = repo.__dict__
            try:
                del repo_dict['_sa_instance_state']
            except:
                pass
            
            new_repos.append(repo_dict)
    for row in new_repos:

        session.log_activity('Info',f"Fetching repos with repo group id: {row['repo_group_id']}")

        update_repo_log(session, row['repo_id'],'Cloning')

        git = html.unescape(row['repo_git'])

        # Strip protocol from remote URL, set a unique path on the filesystem
        if git.find('://',0) > 0:
            repo_relative_path = git[git.find('://',0)+3:][:git[git.find('://',0)+3:].rfind('/',0)+1]
            session.log_activity('Info',f"Repo Relative Path from facade05, from for row in new_repos, line 79: {repo_relative_path}")
            session.log_activity('Info',f"The git path used : {git}")


        else:
            repo_relative_path = git[:git.rfind('/',0)+1]
            session.log_activity('Info',f"Repo Relative Path from facade05, line 80, reset at 86: {repo_relative_path}")


        # Get the full path to the directory where we'll clone the repo
        repo_path = (f"{session.repo_base_directory}{row['repo_group_id']}/{repo_relative_path}")
        session.log_activity('Info',f"Repo Path from facade05, line 86: {repo_path}")


        # Get the name of repo
        repo_name = git[git.rfind('/',0)+1:]
        if repo_name.find('.git',0) > -1:
            repo_name = repo_name[:repo_name.find('.git',0)]
            session.log_activity('Info',f"Repo Name from facade05, line 93: {repo_name}")


        # Check if there will be a storage path collision
        query = s.sql.text("""SELECT NULL FROM repo WHERE CONCAT(repo_group_id,'/',repo_path,repo_name) = :repo_group_id
            """).bindparams(repo_group_id=f"{row['repo_group_id']}/{repo_relative_path}{repo_name}")
        
        result = session.fetchall_data_from_sql_text(query)

        # If there is a collision, append a slug to repo_name to yield a unique path
        if len(result):

            slug = 1
            is_collision = True
            while is_collision:

                if os.path.isdir(f"{repo_path}{repo_name}-{slug}"):
                    slug += 1
                else:
                    is_collision = False

            repo_name = f"{repo_name}-{slug}"

            session.log_activity('Verbose',f"Identical repo detected, storing {git} in {repo_name}")

        # Create the prerequisite directories
        return_code = subprocess.Popen([f"mkdir -p {repo_path}"],shell=True).wait()
#        cfg.log_activity('Info','Return code value when making directors from facade05, line 120: {:d}'.format(return_code))



        # Make sure it's ok to proceed
        if return_code != 0:
            print("COULD NOT CREATE REPO DIRECTORY")

            update_repo_log(session, row['repo_id'],'Failed (mkdir)')
            session.update_status(f"Failed (mkdir {repo_path})")
            session.log_activity('Error',f"Could not create repo directory: {repo_path}" )

            raise Exception("Could not create git repo's prerequisite directories. "
                " Do you have write access?")

        update_repo_log(session, row['repo_id'],'New (cloning)')

        query = s.sql.text("""UPDATE repo SET repo_status='New (Initializing)', repo_path=:pathParam, 
            repo_name=:nameParam WHERE repo_id=:idParam and repo_status != 'Empty'
            """).bindparams(pathParam=repo_relative_path,nameParam=repo_name,idParam=row['repo_id'])

        session.execute_sql(query)

        session.log_activity('Verbose',f"Cloning: {git}")

        cmd = f"git -C {repo_path} clone '{git}' {repo_name}"
        return_code = subprocess.Popen([cmd], shell=True).wait()

        if (return_code == 0):
            # If cloning succeeded, repo is ready for analysis
            # Mark the entire project for an update, so that under normal
            # circumstances caches are rebuilt only once per waiting period.

            update_project_status = s.sql.text("""UPDATE repo SET repo_status='Update' WHERE 
                repo_group_id=:repo_group_id AND repo_status != 'Empty'""").bindparams(repo_group_id=row['repo_group_id'])
            session.execute_sql(update_project_status)

            # Since we just cloned the new repo, set it straight to analyze.
            query = s.sql.text("""UPDATE repo SET repo_status='Analyze',repo_path=:repo_path, repo_name=:repo_name
                WHERE repo_id=:repo_id and repo_status != 'Empty'
                """).bindparams(repo_path=repo_relative_path,repo_name=repo_name,repo_id=row['repo_id'])

            session.execute_sql(query)

            update_repo_log(session, row['repo_id'],'Up-to-date')
            session.log_activity('Info',f"Cloned {git}")

        else:
            # If cloning failed, log it and set the status back to new
            update_repo_log(session, row['repo_id'],f"Failed ({return_code})")

            query = s.sql.text("""UPDATE repo SET repo_status='New (failed)' WHERE repo_id=:repo_id and repo_status !='Empty'
                """).bindparams(repo_id=row['repo_id'])

            session.execute_sql(query)

            session.log_activity('Error',f"Could not clone {git}" % git)

    session.log_activity('Info', f"Fetching new repos (complete)")

    
def check_for_repo_updates(session):

    cfg = session.cfg

# Check the last time a repo was updated and if it has been longer than the
# update_frequency, mark its project for updating during the next analysis.

    cfg.update_status('Checking if any repos need to update')
    cfg.log_activity('Info','Checking repos to update')

    update_frequency = cfg.get_setting('update_frequency')

    get_initialized_repos = ("SELECT repo_id FROM repo WHERE repo_status NOT LIKE 'New%' "
        "AND repo_status != 'Delete' "
        "AND repo_status != 'Analyze' AND repo_status != 'Empty'")
    cfg.cursor.execute(get_initialized_repos)
    repos = list(cfg.cursor)

    for repo in repos:

        # Figure out which repos have been updated within the waiting period

        get_last_update = ("SELECT NULL FROM repos_fetch_log WHERE "
            "repos_id=%s AND status='Up-to-date' AND "
            "date >= CURRENT_TIMESTAMP(6) - INTERVAL %s HOUR ")
        cfg.cursor.execute(get_last_update, (repo[0], update_frequency)) #['id'], update_frequency))

        # If the repo has not been updated within the waiting period, mark it.
        # Also mark any other repos in the project, so we only recache the
        # project once per waiting period.

        if cfg.cursor.rowcount == 0:
            mark_repo = ("""UPDATE repo
                SET repo_status='Update' 
                        WHERE repo.ctid IN (
                SELECT repo.ctid FROM repo JOIN repo_groups ON repo.repo_group_id=repo_groups.repo_group_id
                AND repo.repo_id=%s 
                AND repo.repo_status != 'Empty')""")

            # ("UPDATE repos r JOIN projects p ON p.id = r.projects_id "
            #     "SET status='Update' WHERE "
            #     "r.id=%s and r.status != 'Empty'")
            cfg.cursor.execute(mark_repo, (repo[0], ))#['id'], ))
            cfg.db.commit()

    # Mark the entire project for an update, so that under normal
    # circumstances caches are rebuilt only once per waiting period.

    update_project_status = ("""UPDATE repo
        SET repo_status='Update' 
                WHERE repo.ctid IN (
        SELECT repo.ctid FROM repo LEFT JOIN repo a ON repo.repo_group_id=a.repo_group_id
        AND repo.repo_status='Update'
        AND repo.repo_status != 'Analyze' 
        AND repo.repo_status != 'Empty')""")

    # ("UPDATE repos r LEFT JOIN repos s ON r.projects_id=s.projects_id "
    #     "SET r.status='Update' WHERE s.status='Update' AND "
    #     "r.status != 'Analyze' AND r.status != 'Empty'")

    session.insert_or_update_data(update_project_status)
    # cfg.cursor.execute(update_project_status)
    # cfg.db.commit()

    cfg.log_activity('Info','Checking repos to update (complete)')

def force_repo_updates(cfg):

# Set the status of all non-new repos to "Update".

    cfg.update_status('Forcing all non-new repos to update')
    cfg.log_activity('Info','Forcing repos to update')

    get_repo_ids = ("UPDATE repo SET repo_status='Update' WHERE repo_status "
        "NOT LIKE 'New%' AND repo_status!='Delete' AND repo_status !='Empty'")
    cfg.cursor.execute(get_repo_ids)
    cfg.db.commit()

    cfg.log_activity('Info','Forcing repos to update (complete)')

def force_repo_analysis(cfg):

# Set the status of all non-new repos to "Analyze".

    cfg.update_status('Forcing all non-new repos to be analyzed')
    cfg.log_activity('Info','Forcing repos to be analyzed')

    set_to_analyze = ("UPDATE repo SET repo_status='Analyze' WHERE repo_status "
        "NOT LIKE 'New%' AND repo_status!='Delete' AND repo_status != 'Empty'")
    cfg.cursor.execute(set_to_analyze)
    cfg.db.commit()

    cfg.log_activity('Info','Forcing repos to be analyzed (complete)')

def git_repo_updates(cfg):

# Update existing repos

    cfg.update_status('Updating repos')
    cfg.log_activity('Info','Updating existing repos')

    query = ("SELECT repo_id,repo_group_id,repo_git,repo_name,repo_path FROM repo WHERE "
        "repo_status='Update'");
    cfg.cursor.execute(query)

    existing_repos = list(cfg.cursor)

    for row in existing_repos:
        cfg.log_activity('Verbose','Attempting to update %s' % row[2])#['git'])
        update_repo_log(cfg, row[0],'Updating')#['id'],'Updating')

        attempt = 0

        # Try two times. If it fails the first time, reset and clean the git repo,
        # as somebody may have done a rebase. No work is being done in the local
        # repo, so there shouldn't be legit local changes to worry about.

        #default_branch = ''

        while attempt < 2:

            try:

                firstpull = ("git -C %s%s/%s%s pull"
                    % (cfg.repo_base_directory,row[1],row[4],row[3]))

                return_code_remote = subprocess.Popen([firstpull],shell=True).wait()

                cfg.log_activity('Verbose', 'Got to here. 1.')

                if return_code_remote == 0: 

#                    logremotedefault = ("git -C %s%s/%s%s remote set-head origin -a"
#                        % (cfg.repo_base_directory,row[1],row[4],row[3]))

#                    return_code_remote_default = subprocess.Popen([logremotedefault],stdout=subprocess.PIPE,shell=True).wait()

#                    cfg.log_activity('Verbose', f'remote default is {logremotedefault}.')

                    getremotedefault = ("git -C %s%s/%s%s remote show origin | sed -n '/HEAD branch/s/.*: //p'"
                        % (cfg.repo_base_directory,row[1],row[4],row[3]))

                    return_code_remote = subprocess.Popen([getremotedefault],stdout=subprocess.PIPE, shell=True).wait()

                    remotedefault = subprocess.Popen([getremotedefault],stdout=subprocess.PIPE,shell=True).communicate()[0]

                    remotedefault = remotedefault.decode()

                    cfg.log_activity('Verbose', f'remote default getting checked out is: {remotedefault}.')

                    getremotedefault = (f"git -C %s%s/%s%s checkout {remotedefault}"
                        % (cfg.repo_base_directory,row[1],row[4],row[3]))

                    cfg.log_activity('Verbose', f'get remote default command is: \n \n {getremotedefault} \n \n ')

                    return_code_remote_default_again = subprocess.Popen([getremotedefault],shell=True).wait()

                    if return_code_remote_default_again == 0: 
                        cfg.log_activity('Verbose', "local checkout worked.")
                        cmd = ("git -C %s%s/%s%s pull"
                            % (cfg.repo_base_directory,row[1],row[4],row[3]))#['projects_id'],row['path'],row['name']))

                        return_code = subprocess.Popen([cmd],shell=True).wait()

            except Exception as e: 
                cfg.log_activity('Verbose', f'Error code on branch change is {e}.')
                pass

            finally: 

                cmd = ("git -C %s%s/%s%s pull"
                    % (cfg.repo_base_directory,row[1],row[4],row[3]))#['projects_id'],row['path'],row['name']))

                return_code = subprocess.Popen([cmd],shell=True).wait()

            # If the attempt succeeded, then don't try any further fixes. If
            # the attempt to fix things failed, give up and try next time.
            if return_code == 0 or attempt == 2:
                break

            elif attempt == 0:
                cfg.log_activity('Verbose','git pull failed, attempting reset and '
                    'clean for %s' % row[2])

#                remotedefault = 'main'

#                logremotedefault = ("git -C %s%s/%s%s remote set-head origin -a"
#                    % (cfg.repo_base_directory,row[1],row[4],row[3]))

#                return_code_remote = subprocess.Popen([logremotedefault],stdout=subprocess.PIPE,shell=True).wait()

#                cfg.log_activity('Verbose', f'remote default is {logremotedefault}.')

                getremotedefault = ("git -C %s%s/%s%s remote show origin | sed -n '/HEAD branch/s/.*: //p'"
                    % (cfg.repo_base_directory,row[1],row[4],row[3]))

                return_code_remote = subprocess.Popen([getremotedefault],stdout=subprocess.PIPE,shell=True).wait()

                remotedefault = subprocess.Popen([getremotedefault],stdout=subprocess.PIPE,shell=True).communicate()[0]

                remotedefault = remotedefault.decode()

                try: 

                    getremotedefault = (f"git -C %s%s/%s%s checkout {remotedefault}"
                        % (cfg.repo_base_directory,row[1],row[4],row[3]))


                    return_code_remote_default = subprocess.Popen([getremotedefault],stdout=subprocess.PIPE,shell=True).wait()

                    return_message_getremotedefault = subprocess.Popen([getremotedefault],stdout=subprocess.PIPE,shell=True).communicate()[0]

                    cfg.log_activity('Verbose', f'get remote default result: {return_message_getremotedefault}')

                    getcurrentbranch = ("git -C %s%s/%s%s branch"
                        % (cfg.repo_base_directory,row[1],row[4],row[3]))

                    return_code_local = subprocess.Popen([getcurrentbranch],stdout=subprocess.PIPE,shell=True).wait()

                    localdefault = subprocess.Popen([getcurrentbranch],stdout=subprocess.PIPE,shell=True).communicate()[0]  

                    localdefault = localdefault.decode()

                    cfg.log_activity('Verbose', f'remote default is: {remotedefault}, and localdefault is {localdefault}.') 

                    cmd_checkout_default =  (f"git -C %s%s/%s%s checkout {remote_default}" 
                    % (cfg.repo_base_directory,row[1],row[4],row[3]))

                    cmd_checkout_default_wait = subprocess.Popen([cmd_checkout_default],shell=True).wait()

                    cmdpull2 = ("git -C %s%s/%s%s pull"
                        % (cfg.repo_base_directory,row[1],row[4],row[3]))

                    cmd_reset = ("git -C %s%s/%s%s reset --hard origin"
                        % (cfg.repo_base_directory,row[1],row[4],row[3]))

                    cmd_reset_wait = subprocess.Popen([cmd_reset],shell=True).wait()

                    cmd_clean = ("git -C %s%s/%s%s clean -df"
                        % (cfg.repo_base_directory,row[1],row[4],row[3]))

                    return_code_clean = subprocess.Popen([cmd_clean],shell=True).wait()

                except Exception as e: 

                    cfg.log_activity('Verbose', f'Second pass failed: {e}.')
                    pass 

            cmdpull2 = ("git -C %s%s/%s%s pull"
                        % (cfg.repo_base_directory,row[1],row[4],row[3]))
            
            print(cmdpull2)
            return_code = subprocess.Popen([cmdpull2],shell=True).wait()

            attempt += 1
 
                    #default_branch = ''

        if return_code == 0:

            set_to_analyze = "UPDATE repo SET repo_status='Analyze' WHERE repo_id=%s and repo_status != 'Empty'"
            cfg.cursor.execute(set_to_analyze, (row[0], ))
            cfg.db.commit()

            update_repo_log(cfg, row[0],'Up-to-date')
            cfg.log_activity('Verbose','Updated %s' % row[2])

        else: 

            update_repo_log(cfg, row[0],'Failed (%s)' % return_code)
            cfg.log_activity('Error','Could not update %s' % row[2])


    cfg.log_activity('Info','Updating existing repos (complete)')
