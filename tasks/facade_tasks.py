import sys
import json
import time
import traceback
import logging
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
import multiprocessing
import numpy as np
from celery import group, chain, chord, signature
from celery.utils.log import get_task_logger
from celery.result import allow_join_result
from celery.signals import after_setup_logger
from datetime import timedelta
import sqlalchemy as s

from augur_logging import *
from augur_config import AugurConfig


from facade_worker.facade_worker.facade02utilitymethods import update_repo_log, trim_commit, store_working_author, trim_author
from facade_worker.facade_worker.facade03analyzecommit import analyze_commit
from facade_worker.contributor_interfaceable.contributor_interface import *

from util.worker_util import create_grouped_task_load

from tasks.celery_init import celery_app as celery


from augur_db import data_parse
from augur_db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, Issue, IssueEvent, IssueLabel, IssueAssignee, PullRequestMessageRef, IssueMessageRef, Contributor, Repo

from util.github_paginator import GithubPaginator, hit_api
from util.gh_graphql_entities import PullRequest
from tasks.task_session import *

from facade_worker.facade_worker.facade00mainprogram import *

from augur_logging import TaskLogConfig


#Have one log file for facade_tasks
# facadeLogger = logging.getLogger(__name__)





"""
    You can prevent Celery from configuring any loggers at all by connecting 
    the setup_logging signal. This allows you to completely override the 
    logging configuration with your own.
"""
logger = logging.getLogger(__name__)
config_db_session = TaskSession(logger)
config = AugurConfig(config_db_session)
logs_directory = config.get_value("Logging", "logs_directory")
if logs_directory is None:
    raise Exception('logs_directory not specified in config.')


#Load logging config once at task definition
@after_setup_logger.connect
def setup_loggers(*args,**kwargs):
    #load config
    loggingConfig = TaskLogConfig(base_log_dir=logs_directory)

    
    



#enable celery multithreading
@celery.task
def analyze_commits_in_parallel(queue, repo_id, repo_location, multithreaded):
    #create new cfg for celery thread.
    logger = logging.getLogger(analyze_commits_in_parallel.__name__)
    cfg = FacadeConfig(logger)

    for analyzeCommit in queue:    

        analyze_commit(cfg, repo_id, repo_location, analyzeCommit, multithreaded)





# if platform.python_implementation() == 'PyPy':
#   import pymysql
# else:
#   import MySQLdb

def analysis(cfg, multithreaded, session=None, processes=6):

# Run the analysis by looping over all active repos. For each repo, we retrieve
# the list of commits which lead to HEAD. If any are missing from the database,
# they are filled in. Then we check to see if any commits in the database are
# not in the list of parents, and prune them out.
#
# We also keep track of the last commit to be processed, so that if the analysis
# is interrupted (possibly leading to partial data in the database for the
# commit being analyzed at the time) we can recover.

### Local helper functions ###

    def update_analysis_log(repos_id,status):

    # Log a repo's analysis status

        log_message = ("INSERT INTO analysis_log (repos_id,status) "
            "VALUES (%s,%s)")

        try:
            cfg.cursor.execute(log_message, (repos_id,status))
            cfg.db.commit()
        except:
            pass

### The real function starts here ###

    cfg.update_status('Running analysis')
    cfg.log_activity('Info',f"Beginning analysis.")

    start_date = cfg.get_setting('start_date')

    repo_list = "SELECT repo_id,repo_group_id,repo_path,repo_name FROM repo WHERE repo_status='Analyze'"
    cfg.cursor.execute(repo_list)
    repos = list(cfg.cursor)


    for repo in repos:

        
        #Add committers for repo if session
        if session != None:
            grab_committer_list(session,repo[0])

        update_analysis_log(repo[0],"Beginning analysis.")
        cfg.log_activity('Verbose','Analyzing repo: %s (%s)' % (repo[0],repo[3]))

        cfg.inc_repos_processed()

        # First we check to see if the previous analysis didn't complete

        get_status = ("SELECT working_commit FROM working_commits WHERE repos_id=%s")

        cfg.cursor.execute(get_status, (repo[0], ))
        try:
            working_commits = list(cfg.cursor)
        except:
            working_commits = []
        #cfg.cursor.fetchone()[1]

        # If there's a commit still there, the previous run was interrupted and
        # the commit data may be incomplete. It should be trimmed, just in case.
        for commit in working_commits:
            trim_commit(cfg, repo[0],commit[0])

            # Remove the working commit.
            remove_commit = ("DELETE FROM working_commits "
                "WHERE repos_id = %s AND working_commit = %s")
            cfg.cursor.execute(remove_commit, (repo[0],commit[0]))
            cfg.db.commit()

            cfg.log_activity('Debug','Removed working commit: %s' % commit[0])

        # Start the main analysis

        update_analysis_log(repo[0],'Collecting data')

        repo_loc = ('%s%s/%s%s/.git' % (cfg.repo_base_directory,
            repo[1], repo[2],
            repo[3]))
        # Grab the parents of HEAD

        parents = subprocess.Popen(["git --git-dir %s log --ignore-missing "
            "--pretty=format:'%%H' --since=%s" % (repo_loc,start_date)],
            stdout=subprocess.PIPE, shell=True)

        parent_commits = set(parents.stdout.read().decode("utf-8",errors="ignore").split(os.linesep))

        # If there are no commits in the range, we still get a blank entry in
        # the set. Remove it, as it messes with the calculations

        if '' in parent_commits:
            parent_commits.remove('')

        # Grab the existing commits from the database

        existing_commits = set()

        find_existing = ("SELECT DISTINCT cmt_commit_hash FROM commits WHERE repo_id=%s")

        cfg.cursor.execute(find_existing, (repo[0], ))

        try:
            for commit in list(cfg.cursor):
                existing_commits.add(commit[0])
        except:
            cfg.log_activity('Info', 'list(cfg.cursor) returned an error')

        # Find missing commits and add them

        missing_commits = parent_commits - existing_commits

        cfg.log_activity('Debug','Commits missing from repo %s: %s' %
            (repo[0],len(missing_commits)))

        ## TODO: Verify if the multithreaded approach here is optimal for postgresql

        if len(missing_commits) > 0:

            

            #cfg.log_activity('Info','Type of missing_commits: %s' % type(missing_commits))
            
            #Split commits into mostly equal queues so each process starts with a workload and there is no
            #    overhead to pass into queue from the parent.            
            #Each task generates their own cfg as celery cannot serialize this data
            
            
            contrib_jobs = create_grouped_task_load(repo[0],repo_loc,multithreaded,processes=processes,dataList=missing_commits,task=analyze_commits_in_parallel)

            group_result = contrib_jobs.apply_async()
            #Context manager needed for joining back to parent process properly.
            with allow_join_result():
                group_result.join()
                
            
        elif len(missing_commits) > 0:
            for commit in missing_commits:
                analyze_commit(cfg, repo[0], repo_loc, commit, multithreaded)


        update_analysis_log(repo[0],'Data collection complete')

        update_analysis_log(repo[0],'Beginning to trim commits')

        # Find commits which are out of the analysis range

        trimmed_commits = existing_commits - parent_commits

        cfg.log_activity('Debug','Commits to be trimmed from repo %s: %s' %
            (repo[0],len(trimmed_commits)))

        for commit in trimmed_commits:

            trim_commit(cfg, repo[0],commit)

        set_complete = "UPDATE repo SET repo_status='Complete' WHERE repo_id=%s and repo_status != 'Empty'"
        try:
            cfg.cursor.execute(set_complete, (repo[0], ))
        except:
            pass

        update_analysis_log(repo[0],'Commit trimming complete')

        update_analysis_log(repo[0],'Complete')

    cfg.log_activity('Info','Running analysis (complete)')


def facade_init(session):
    

    
    
    opts,args = getopt.getopt(sys.argv[1:],'hdpcuUaAmnfIrx')
    for opt in opts:
        if opt[0] == '-h':
            print("\nfacade-worker.py does everything by default except invalidating caches\n"
                    "and forcing updates, unless invoked with one of the following options.\n"
                    "In those cases, it will only do what you have selected.\n\n"
                    "Options:\n"
                    "   -d  Delete marked repos\n"
                    "   -c  Run 'git clone' on new repos\n"
                    "   -u  Check if any repos should be marked for updating\n"
                    "   -U  Force all repos to be marked for updating\n"
                    "   -p  Run 'git pull' on repos\n"
                    "   -a  Analyze git repos\n"
                    "   -A  Force all repos to be analyzed\n"
                    "   -m  Disable multithreaded mode (but why?)\n"
                    "   -n  Nuke stored affiliations (if mappings modified by hand)\n"
                    "   -f  Fill empty affiliations\n"
                    "   -I  Invalidate caches\n"
                    "   -r  Rebuild unknown affiliation and web caches\n"
                    "   -x  Create Excel summary files\n\n")
            sys.exit(0)

        elif opt[0] == '-d':
            delete_marked_repos = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: delete marked repos.')

        elif opt[0] == '-c':
            clone_repos = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: clone new repos.')

        elif opt[0] == '-u':
            check_updates = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: checking for repo updates')

        elif opt[0] == '-U':
            force_updates = 1
            session.cfg.log_activity('Info','Option set: forcing repo updates')

        elif opt[0] == '-p':
            pull_repos = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: update repos.')

        elif opt[0] == '-a':
            run_analysis = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: running analysis.')

        elif opt[0] == '-A':
            force_analysis = 1
            run_analysis = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: forcing analysis.')

        elif opt[0] == '-m':
            multithreaded = 0
            session.cfg.log_activity('Info','Option set: disabling multithreading.')

        elif opt[0] == '-n':
            nuke_stored_affiliations = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: nuking all affiliations')

        elif opt[0] == '-f':
            fix_affiliations = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: fixing affiliations.')

        elif opt[0] == '-I':
            force_invalidate_caches = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: Invalidate caches.')

        elif opt[0] == '-r':
            rebuild_caches = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: rebuilding caches.')

        elif opt[0] == '-x':
            create_xlsx_summary_files = 1
            limited_run = 1
            session.cfg.log_activity('Info','Option set: creating Excel summary files.')

    
    # Get the location of the directory where git repos are stored
    repo_base_directory = session.cfg.repo_base_directory

    # Determine if it's safe to start the script
    current_status = session.cfg.get_setting('utility_status')

    if current_status != 'Idle':
        session.cfg.log_activity('Error','Something is already running, aborting maintenance '
            'and analysis.\nIt is unsafe to continue.')
        # sys.exit(1)

    if len(repo_base_directory) == 0:
        session.cfg.log_activity('Error','No base directory. It is unsafe to continue.')
        session.cfg.update_status('Failed: No base directory')
        sys.exit(1)

    # Begin working


@celery.task
def facade_commits_model():

    print(facade_commits_model.__name__)
    logger = logging.getLogger(facade_commits_model.__name__)
    session = FacadeSession(logger)
    
    # Figure out what we need to do
    limited_run = session.limited_run
    delete_marked_repos = session.delete_marked_repos
    pull_repos = session.pull_repos
    clone_repos = session.clone_repos
    check_updates = session.check_updates
    force_updates = session.force_updates
    run_analysis = session.run_analysis
    force_analysis = session.force_analysis
    nuke_stored_affiliations = session.nuke_stored_affiliations
    fix_affiliations = session.fix_affiliations
    force_invalidate_caches = session.force_invalidate_caches
    rebuild_caches = session.rebuild_caches
     #if abs((datetime.datetime.strptime(session.cfg.get_setting('aliases_processed')[:-3], 
        # '%Y-%m-%d %I:%M:%S.%f') - datetime.datetime.now()).total_seconds()) // 3600 > int(session.cfg.get_setting(
        #   'update_frequency')) else 0
    force_invalidate_caches = session.force_invalidate_caches
    create_xlsx_summary_files = session.create_xlsx_summary_files
    multithreaded = session.multithreaded

    facade_init(session)

    start_time = time.time()
    session.cfg.log_activity('Quiet','Running facade-worker')

    if not limited_run or (limited_run and delete_marked_repos):
        git_repo_cleanup(session.cfg)

    if not limited_run or (limited_run and clone_repos):
        git_repo_initialize(session.cfg)

    if not limited_run or (limited_run and check_updates):
        check_for_repo_updates(session.cfg)

    if force_updates:
        force_repo_updates(session.cfg)

    if not limited_run or (limited_run and pull_repos):
        git_repo_updates(session.cfg)

    if force_analysis:
        force_repo_analysis(session.cfg)

    
    #Give analysis the github interface so that it can make API calls
    #if not limited_run or (limited_run and run_analysis):
    analysis(session.cfg, multithreaded, session=session)
    
    ### end moved up

    if nuke_stored_affiliations:
        nuke_affiliations(session.cfg)

    session.logger.info(session.cfg)
    if not limited_run or (limited_run and fix_affiliations):
        fill_empty_affiliations(session.cfg)

    if force_invalidate_caches:
        invalidate_caches(session.cfg)

    if not limited_run or (limited_run and rebuild_caches):
        rebuild_unknown_affiliation_and_web_caches(session.cfg)

    if not limited_run or (limited_run and create_xlsx_summary_files):

        session.cfg.log_activity('Info','Creating summary Excel files')

        # from excel_generators import *

        session.cfg.log_activity('Info','Creating summary Excel files (complete)')


    # All done
    session.cfg.update_status('Idle')
    session.cfg.log_activity('Quiet','facade-worker.py completed')
    
    elapsed_time = time.time() - start_time

    print('\nCompleted in %s\n' % timedelta(seconds=int(elapsed_time)))

    session.cfg.cursor.close()
    #session.cfg.cursor_people.close()
    session.cfg.db.close()
    #session.cfg.db_people.close()

@celery.task
def facade_grab_contribs(repo_id):
    logger = logging.getLogger(facade_grab_contribs.__name__)
    session = FacadeSession(logger)
    
    grab_committer_list(session,repo_id)
    

#Method to parallelize, takes a queue of data and iterates over it

@celery.task
def process_commit_metadata(contributorQueue,repo_id):
    logger = logging.getLogger(process_commit_metadata.__name__)
    session = FacadeSession(logger)

    for contributor in contributorQueue:
        # Get the email from the commit data
        email = contributor['email_raw'] if 'email_raw' in contributor else contributor['email']
    
        name = contributor['name']

        # check the email to see if it already exists in contributor_aliases
        try:
            # Look up email to see if resolved
            """
            alias_table_data = interface.db.execute(
                s.sql.select([s.column('alias_email')]).where(
                    interface.contributors_aliases_table.c.alias_email == email
                )
            ).fetchall()
            """


            alias_table_data = ContributorsAliases.query.filter_by(alias_email=email).all()
            if len(alias_table_data) >= 1:
                # Move on if email resolved

                #interface.logger.info(
                #    f"Email {email} has been resolved earlier.")

                continue
        except Exception as e:
            session.logger.info(
                f"alias table query failed with error: {e}")
        
        #Check the unresolved_commits table to avoid hitting endpoints that we know don't have relevant data needlessly
        try:
            
            unresolved_query_result = UnresolvedCommitEmails.query.filter_by(name=name).all()

            if len(unresolved_query_result) >= 1:

                #interface.logger.info(f"Commit data with email {email} has been unresolved in the past, skipping...")

                continue
        except Exception as e:
            session.logger.info(f"Failed to query unresolved alias table with error: {e}")
    

        login = None
    
        #Check the contributors table for a login for the given name
        try:
            contributors_with_matching_name = Contributors.query.filter_by(cntrb_full_name=name).one()

            login = contributors_with_matching_name.gh_login

        except Exception as e:
            session.logger.error(f"Failed local login lookup with error: {e}")
        

        # Try to get the login from the commit sha
        if login == None or login == "":
            login = get_login_with_commit_hash(session,contributor, repo_id)
    
        if login == None or login == "":
            # Try to get the login from supplemental data if not found with the commit hash
            login = get_login_with_supplemental_data(session,contributor)
    
        if login == None:
            continue

        url = ("https://api.github.com/users/" + login)

        user_data = request_dict_from_endpoint(session,url)

        if user_data == None:
            session.logger.warning(
                f"user_data was unable to be reached. Skipping...")
            continue

        # Use the email found in the commit data if api data is NULL
        emailFromCommitData = contributor['email_raw'] if 'email_raw' in contributor else contributor['email']

        session.logger.info(
            f"Successfully retrieved data from github for email: {emailFromCommitData}")

        # Get name from commit if not found by GitHub
        name_field = contributor['commit_name'] if 'commit_name' in contributor else contributor['name']

        try:
            
            cntrb_id = AugurUUID(session.platform_id,user_data['id']).to_UUID()
            # try to add contributor to database
            cntrb = {
                "cntrb_id" : cntrb_id,
                "cntrb_login": user_data['login'],
                "cntrb_created_at": user_data['created_at'],
                "cntrb_email": user_data['email'] if 'email' in user_data else None,
                "cntrb_company": user_data['company'] if 'company' in user_data else None,
                "cntrb_location": user_data['location'] if 'location' in user_data else None,
                # "cntrb_type": , dont have a use for this as of now ... let it default to null
                "cntrb_canonical": user_data['email'] if 'email' in user_data and user_data['email'] is not None else emailFromCommitData,
                "gh_user_id": user_data['id'],
                "gh_login": user_data['login'],
                "gh_url": user_data['url'],
                "gh_html_url": user_data['html_url'],
                "gh_node_id": user_data['node_id'],
                "gh_avatar_url": user_data['avatar_url'],
                "gh_gravatar_id": user_data['gravatar_id'],
                "gh_followers_url": user_data['followers_url'],
                "gh_following_url": user_data['following_url'],
                "gh_gists_url": user_data['gists_url'],
                "gh_starred_url": user_data['starred_url'],
                "gh_subscriptions_url": user_data['subscriptions_url'],
                "gh_organizations_url": user_data['organizations_url'],
                "gh_repos_url": user_data['repos_url'],
                "gh_events_url": user_data['events_url'],
                "gh_received_events_url": user_data['received_events_url'],
                "gh_type": user_data['type'],
                "gh_site_admin": user_data['site_admin'],
                "cntrb_last_used": None if 'updated_at' not in user_data else user_data['updated_at'],
                # Get name from commit if api doesn't get it.
                "cntrb_full_name": name_field if 'name' not in user_data or user_data['name'] is None else user_data['name'],
                #"tool_source": interface.tool_source,
                #"tool_version": interface.tool_version,
                #"data_source": interface.data_source
            }

            session.logger.info(f"{cntrb}")

        except Exception as e:
            session.logger.info(f"Error when trying to create cntrb: {e}")
            continue
        # Check if the github login exists in the contributors table and add the emails to alias' if it does.

        # Also update the contributor record with commit data if we can.
        """
        try:
            if not resolve_if_login_existing(session,cntrb):
                try:
                    #interface.db.execute(
                    #    interface.contributors_table.insert().values(cntrb))
                    newContrib = Contributors(**cntrb)
                    session.add(newContrib)
                    session.commit()
                except Exception as e:
                    session.logger.info(
                        f"Ran into likely database collision. Assuming contributor exists in database. Error: {e}")
            else:
                interface.update_contributor(cntrb)
        """
        
        #Executes an upsert with sqlalchemy 
        cntrb_natural_keys = ['cntrb_login']
        session.insert_data(cntrb,Contributors,cntrb_natural_keys)

        try:
            # Update alias after insertion. Insertion needs to happen first so we can get the autoincrementkey
            insert_alias(session,cntrb, emailFromCommitData)
        except LookupError as e:
            interface.logger.info(
                ''.join(traceback.format_exception(None, e, e.__traceback__)))
            interface.logger.info(
                f"Contributor id not able to be found in database despite the user_id existing. Something very wrong is happening. Error: {e}")
            return 
        

        
        # Resolve any unresolved emails if we get to this point.
        # They will get added to the alias table later
        # Do this last to absolutely make sure that the email was resolved before we remove it from the unresolved table.
        query = s.sql.text("""
            DELETE FROM unresolved_commit_emails
            WHERE email='{}'
        """.format(email))

        session.logger.info(f"Updating now resolved email {email}")

        try:
            #interface.db.execute(query)
            #session.query(UnresolvedCommitEmails).filter(UnresolvedCommitEmails.email == email).delete()
            #session.commit()
            session.execute_sql(query)
        except Exception as e:
            session.logger.info(
                f"Deleting now resolved email failed with error: {e}")
    
    
    return

@celery.task
def link_commits_to_contributor(contributorQueue):
        logger = logging.getLogger(link_commits_to_contributor.__name__)
        session = FacadeSession(logger)

        # iterate through all the commits with emails that appear in contributors and give them the relevant cntrb_id.
        for cntrb_email in contributorQueue:
            logger.debug(
                f"These are the emails and cntrb_id's  returned: {cntrb_email}")

            try:
                #database.execute(commits_table.update().where(
                #    commits_table.c.cmt_committer_email == cntrb_email['email']
                #).values({
                #    'cmt_ght_author_id': cntrb_email['cntrb_id']
                #}))
                stmnt = s.update(Commits).where(Commits.cmt_committer_email == cntrb_email['email']).values(
                    cmt_ght_author_id=cntrb_email['cntrb_id']
                ).execution_options(synchronize_session="fetch")

                result = session.execute(stmnt)
            except Exception as e:
                logger.info(
                    f"Ran into problem when enriching commit data. Error: {e}")
                continue
        
        return

# Update the contributors table from the data facade has gathered.
def insert_facade_contributors(session, repo_id,processes=4,multithreaded=True):
    session.logger.info(
        "Beginning process to insert contributors from facade commits for repo w entry info: {}\n".format(repo_id))

    # Get all of the commit data's emails and names from the commit table that do not appear
    # in the contributors table or the contributors_aliases table.
    new_contrib_sql = s.sql.text("""
            SELECT DISTINCT
                commits.cmt_author_name AS NAME,
                commits.cmt_commit_hash AS hash,
                commits.cmt_author_raw_email AS email_raw,
                'not_unresolved' as resolution_status
            FROM
                commits
            WHERE
                commits.repo_id = :repo_id
                AND (NOT EXISTS ( SELECT contributors.cntrb_canonical FROM contributors WHERE contributors.cntrb_canonical = commits.cmt_author_raw_email )
                or NOT EXISTS ( SELECT contributors_aliases.alias_email from contributors_aliases where contributors_aliases.alias_email = commits.cmt_author_raw_email)
                AND ( commits.cmt_author_name ) IN ( SELECT C.cmt_author_name FROM commits AS C WHERE C.repo_id = :repo_id GROUP BY C.cmt_author_name ))
            GROUP BY
                commits.cmt_author_name,
                commits.cmt_commit_hash,
                commits.cmt_author_raw_email
            UNION
            SELECT DISTINCT
                commits.cmt_author_name AS NAME,--commits.cmt_id AS id,
                commits.cmt_commit_hash AS hash,
                commits.cmt_author_raw_email AS email_raw,
                'unresolved' as resolution_status
            FROM
                commits
            WHERE
                commits.repo_id = :repo_id
                AND EXISTS ( SELECT unresolved_commit_emails.email FROM unresolved_commit_emails WHERE unresolved_commit_emails.email = commits.cmt_author_raw_email )
                AND ( commits.cmt_author_name ) IN ( SELECT C.cmt_author_name FROM commits AS C WHERE C.repo_id = :repo_id GROUP BY C.cmt_author_name )
            GROUP BY
                commits.cmt_author_name,
                commits.cmt_commit_hash,
                commits.cmt_author_raw_email
            ORDER BY
            hash
    """).bindparams(repo_id=repo_id)

    #Execute statement with session.
    new_contribs = session.execute_sql(new_contrib_sql).fetchall()

    #print(new_contribs)
    
    #json.loads(pd.read_sql(new_contrib_sql, self.db, params={
    #             'repo_id': repo_id}).to_json(orient="records"))

    
    if len(new_contribs) > 2 and multithreaded:
        
        #Split commits into mostly equal queues so each process starts with a workload and there is no
        #    overhead to pass into queue from the parent.
        

        contrib_jobs = create_grouped_task_load(repo_id,processes=processes,dataList=new_contribs,task=process_commit_metadata)
        
        result = contrib_jobs.apply_async()

        with allow_join_result():
            result.join()

    else:
        #I think this is the right syntax for running a celery task directly
        #It 'should' work like a function.
        process_commit_metadata(list(new_contribs),repo_id)

    session.logger.debug("DEBUG: Got through the new_contribs")
    

    # sql query used to find corresponding cntrb_id's of emails found in the contributor's table
    # i.e., if a contributor already exists, we use it!
    resolve_email_to_cntrb_id_sql = s.sql.text("""
        SELECT DISTINCT
            cntrb_id,
            contributors.cntrb_login AS login,
            contributors.cntrb_canonical AS email,
            commits.cmt_author_raw_email
        FROM
            contributors,
            commits
        WHERE
            contributors.cntrb_canonical = commits.cmt_author_raw_email
            AND commits.repo_id = :repo_id
        UNION
        SELECT DISTINCT
            contributors_aliases.cntrb_id,
                            contributors.cntrb_login as login, 
            contributors_aliases.alias_email AS email,
            commits.cmt_author_raw_email
        FROM
                            contributors,
            contributors_aliases,
            commits
        WHERE
            contributors_aliases.alias_email = commits.cmt_author_raw_email
                            AND contributors.cntrb_id = contributors_aliases.cntrb_id
            AND commits.repo_id = :repo_id
    """).bindparams(repo_id=repo_id)

    #self.logger.info("DEBUG: got passed the sql statement declaration")
    # Get a list of dicts that contain the emails and cntrb_id's of commits that appear in the contributor's table.
    #existing_cntrb_emails = json.loads(pd.read_sql(resolve_email_to_cntrb_id_sql, self.db, params={
    #                                    'repo_id': repo_id}).to_json(orient="records"))

    existing_cntrb_emails = session.execute_sql(resolve_email_to_cntrb_id_sql).fetchall()
    
    if len(existing_cntrb_emails) > 0 and multithreaded:
        
        #Split commits into mostly equal queues so each process starts with a workload and there is no
        #    overhead to pass into queue from the parent.
        
        
        update_jobs = create_grouped_task_load(processes=processes,dataList=existing_cntrb_emails,task=link_commits_to_contributor)

        result = update_jobs.apply_async()

        with allow_join_result():
            result.join()
    else:
        link_commits_to_contributor(list(existing_cntrb_emails))

    session.logger.info("Done with inserting and updating facade contributors")
    return

@celery.task
def facade_resolve_contribs():
    logger = logging.getLogger(facade_resolve_contribs.__name__)
    session = FacadeSession(logger)

    facade_init(session)

    multithreaded = session.multithreaded
    start_time = time.time()
    ### moved up by spg on 12/1/2021
    #Interface with the contributor worker and inserts relevant data by repo
    session.cfg.update_status('Updating Contributors')
    session.cfg.log_activity('Info', 'Updating Contributors with commits')
    query = ("SELECT repo_id FROM repo");

    session.cfg.cursor.execute(query)

    all_repos = list(session.cfg.cursor)

    #pdb.set_trace()
    #breakpoint()
    for repo in all_repos:
        session.logger.info(f"Processing repo {repo}")
        insert_facade_contributors(session,repo[0],multithreaded=multithreaded)
    
    elapsed_time = time.time() - start_time

    print('\nCompleted in %s\n' % timedelta(seconds=int(elapsed_time)))
