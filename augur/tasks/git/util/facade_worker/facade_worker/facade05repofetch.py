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

def git_repo_initialize(cfg, repo_group_id=None):

    # Select any new git repos so we can set up their locations and git clone

    if repo_group_id is None:
        cfg.update_status('Fetching non-cloned repos')
        cfg.log_activity('Info','Fetching non-cloned repos')

        query = "SELECT repo_id,repo_group_id,repo_git FROM repo WHERE repo_status LIKE 'New%'";
        cfg.cursor.execute(query)

        new_repos = []
        all_repos = list(cfg.cursor)

        for repo in all_repos:
            if not os.path.isdir(cfg.repo_base_directory + str(repo[0])):
                new_repos.append(repo)
    else:
        cfg.update_status('Fetching repos with repo group id: {}'.format(repo_group_id))
        cfg.log_activity('Info','Fetching repos with repo group id: {}'.format(repo_group_id))

        query = "SELECT repo_id,repo_group_id,repo_git FROM repo WHERE repo_status LIKE 'New%'";
        cfg.cursor.execute(query)

        new_repos = list(cfg.cursor)

    for row in new_repos:

        cfg.log_activity('Info','Fetching repos with repo group id: {}'.format(repo_group_id))
        cfg.log_activity('Info','Fetching repos with repo group id: {}'.format(repo_group_id))

        update_repo_log(cfg, row[0],'Cloning')

        git = html.unescape(row[2])

        # Strip protocol from remote URL, set a unique path on the filesystem
        if git.find('://',0) > 0:
            repo_relative_path = git[git.find('://',0)+3:][:git[git.find('://',0)+3:].rfind('/',0)+1]
            cfg.log_activity('Info','Repo Relative Path from facade05, from for row in new_repos, line 79: {}'.format(repo_relative_path))
            cfg.log_activity('Info','The git path used : {}'.format(git))


        else:
            repo_relative_path = git[:git.rfind('/',0)+1]
            cfg.log_activity('Info','Repo Relative Path from facade05, line 80, reset at 86: {}'.format(repo_relative_path))


        # Get the full path to the directory where we'll clone the repo
        repo_path = ('%s%s/%s' %
            (cfg.repo_base_directory,row[1],repo_relative_path))
        cfg.log_activity('Info','Repo Path from facade05, line 86: {}'.format(repo_path))


        # Get the name of repo
        repo_name = git[git.rfind('/',0)+1:]
        if repo_name.find('.git',0) > -1:
            repo_name = repo_name[:repo_name.find('.git',0)]
            cfg.log_activity('Info','Repo Name from facade05, line 93: {}'.format(repo_name))


        # Check if there will be a storage path collision
        query = ("SELECT NULL FROM repo WHERE CONCAT(repo_group_id,'/',repo_path,repo_name) = %s")
        cfg.cursor.execute(query, ('{}/{}{}'.format(row[1], repo_relative_path, repo_name), ))
        cfg.db.commit()

        # If there is a collision, append a slug to repo_name to yield a unique path
        if cfg.cursor.rowcount:

            slug = 1
            is_collision = True
            while is_collision:

                if os.path.isdir('%s%s-%s' % (repo_path,repo_name,slug)):
                    slug += 1
                else:
                    is_collision = False

            repo_name = '%s-%s' % (repo_name,slug)

            cfg.log_activity('Verbose','Identical repo detected, storing %s in %s' %
                (git,repo_name))

        # Create the prerequisite directories
        return_code = subprocess.Popen(['mkdir -p %s' %repo_path],shell=True).wait()
#        cfg.log_activity('Info','Return code value when making directors from facade05, line 120: {:d}'.format(return_code))



        # Make sure it's ok to proceed
        if return_code != 0:
            print("COULD NOT CREATE REPO DIRECTORY")

            update_repo_log(cfg, row[0],'Failed (mkdir)')
            cfg.update_status('Failed (mkdir %s)' % repo_path)
            cfg.log_activity('Error','Could not create repo directory: %s' %
                repo_path)

            sys.exit("Could not create git repo's prerequisite directories. "
                " Do you have write access?")

        update_repo_log(cfg, row[0],'New (cloning)')

        query = ("UPDATE repo SET repo_status='New (Initializing)', repo_path=%s, "
            "repo_name=%s WHERE repo_id=%s and repo_status != 'Empty'")

        cfg.cursor.execute(query, (repo_relative_path,repo_name,row[0]))
        cfg.db.commit()

        cfg.log_activity('Verbose','Cloning: %s' % git)

        cmd = "git -C %s clone '%s' %s" % (repo_path,git,repo_name)
        return_code = subprocess.Popen([cmd], shell=True).wait()

        if (return_code == 0):
            # If cloning succeeded, repo is ready for analysis
            # Mark the entire project for an update, so that under normal
            # circumstances caches are rebuilt only once per waiting period.

            update_project_status = ("UPDATE repo SET repo_status='Update' WHERE "
                "repo_group_id=%s AND repo_status != 'Empty'")
            cfg.cursor.execute(update_project_status, (row[1], ))
            cfg.db.commit()

            # Since we just cloned the new repo, set it straight to analyze.
            query = ("UPDATE repo SET repo_status='Analyze',repo_path=%s, repo_name=%s "
                "WHERE repo_id=%s and repo_status != 'Empty'")

            cfg.cursor.execute(query, (repo_relative_path,repo_name,row[0]))
            cfg.db.commit()

            update_repo_log(cfg, row[0],'Up-to-date')
            cfg.log_activity('Info','Cloned %s' % git)

        else:
            # If cloning failed, log it and set the status back to new
            update_repo_log(cfg, row[0],'Failed (%s)' % return_code)

            query = ("UPDATE repo SET repo_status='New (failed)' WHERE repo_id=%s and repo_status !='Empty'")

            cfg.cursor.execute(query, (row[0], ))
            cfg.db.commit()

            cfg.log_activity('Error','Could not clone %s' % git)

    cfg.log_activity('Info', 'Fetching new repos (complete)')

    
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
