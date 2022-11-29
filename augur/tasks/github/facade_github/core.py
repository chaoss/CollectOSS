from augur.tasks.github.facade_github.contributor_interfaceable.contributor_interface import * 
from augur.tasks.github.util.util import get_owner_repo
from numpy.lib.utils import source
from augur.tasks.github.util.github_task_session import *
from augur.tasks.github.util.github_paginator import *
from augur.application.db.models import *
import sqlalchemy as s
import time
import math
import traceback
from augur.tasks.util.AugurUUID import AugurUUID, GithubUUID, UnresolvableUUID





def query_github_contributors(session, entry_info, repo_id):

    """ Data collection function
    Query the GitHub API for contributors
    """
    session.logger.info(f"Querying contributors with given entry info: {entry_info}\n")

    ## It absolutely doesn't matter if the contributor has already contributoed to a repo. it only matters that they exist in our table, and
    ## if the DO, then we DO NOT want to insert them again in any GitHub Method.
    github_url = entry_info['given']['github_url'] if 'github_url' in entry_info['given'] else entry_info['given']['git_url']

    # Extract owner/repo from the url for the endpoint
    try:
        owner, name = get_owner_repo(github_url)
    except IndexError as e:
        session.logger.error(f"Encountered bad entry info: {entry_info}")
        return

    # Set the base of the url and place to hold contributors to insert
    contributors_url = (
        f"https://api.github.com/repos/{owner}/{name}/" +
        "contributors?state=all"
    )

    # Get contributors that we already have stored
    #   Set our duplicate and update column map keys (something other than PK) to
    #   check dupicates/needed column updates with
    table = 'contributors'
    table_pkey = 'cntrb_id'
    update_col_map = {'cntrb_email': 'email'}
    duplicate_col_map = {'cntrb_login': 'login'}

    #list to hold contributors needing insertion or update
    contributor_list = GithubPaginator(contributors_url, session.oauths,session.logger)#paginate(contributors_url, duplicate_col_map, update_col_map, table, table_pkey)

    len_contributor_list = len(contributor_list)

    session.logger.info("Count of contributors needing insertion: " + str(len_contributor_list) + "\n")

    if len_contributor_list == 0:
        return

    for repo_contributor in contributor_list:
        try:
            # Need to hit this single contributor endpoint to get extra data including...
            #   `created at`
            #   i think that's it
            cntrb_url = ("https://api.github.com/users/" + repo_contributor['login'])

            
            session.logger.info("Hitting endpoint: " + cntrb_url + " ...\n")
            #r = hit_api(session.oauths, cntrb_url, session.logger)
            #contributor = r.json()

            contributor = request_dict_from_endpoint(session, cntrb_url)

            #session.logger.info(f"Contributor: {contributor} \n")
            company = None
            location = None
            email = None
            if 'company' in contributor:
                company = contributor['company']
            if 'location' in contributor:
                location = contributor['location']
            if 'email' in contributor:
                email = contributor['email']
                canonical_email = contributor['email']

            #TODO get and store an owner id
            
            #Generate ID for cntrb table
            #cntrb_id = AugurUUID(session.platform_id,contributor['id']).to_UUID()
            cntrb_id = GithubUUID()
            cntrb_id["user"] = int(contributor['id'])
            cntrb_id["platform"] = session.platform_id

            cntrb = {
                "cntrb_id" : cntrb_id.to_UUID(),
                "cntrb_login": contributor['login'],
                "cntrb_created_at": contributor['created_at'],
                "cntrb_email": email,
                "cntrb_company": company,
                "cntrb_location": location,
                # "cntrb_type": , dont have a use for this as of now ... let it default to null
                "cntrb_canonical": canonical_email,
                "gh_user_id": contributor['id'],
                "gh_login": contributor['login'],
                "gh_url": contributor['url'],
                "gh_html_url": contributor['html_url'],
                "gh_node_id": contributor['node_id'], #This is what we are dup checking
                "gh_avatar_url": contributor['avatar_url'],
                "gh_gravatar_id": contributor['gravatar_id'],
                "gh_followers_url": contributor['followers_url'],
                "gh_following_url": contributor['following_url'],
                "gh_gists_url": contributor['gists_url'],
                "gh_starred_url": contributor['starred_url'],
                "gh_subscriptions_url": contributor['subscriptions_url'],
                "gh_organizations_url": contributor['organizations_url'],
                "gh_repos_url": contributor['repos_url'],
                "gh_events_url": contributor['events_url'],
                "gh_received_events_url": contributor['received_events_url'],
                "gh_type": contributor['type'],
                "gh_site_admin": contributor['site_admin'],
                "cntrb_last_used" : None if 'updated_at' not in contributor else contributor['updated_at'],
                "cntrb_full_name" : None if 'name' not in contributor else contributor['name'],
                #"tool_source": session.tool_source,
                #"tool_version": session.tool_version,
                #"data_source": session.data_source
            }

            cntrb_natural_keys = ['cntrb_id']
            #insert cntrb to table.
            #session.logger.info(f"Contributor:  {cntrb}  \n")
            session.insert_data(cntrb,Contributor,cntrb_natural_keys)
            
        except Exception as e:
            session.logger.error("Caught exception: {}".format(e))
            session.logger.error(f"Traceback: {traceback.format_exc()}")
            session.logger.error("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
            continue

# Get all the committer data for a repo.
# Used by facade in facade03analyzecommit
def grab_committer_list(session, repo_id, platform="github"):

    # Create API endpoint from repo_id
    try:
        endpoint = create_endpoint_from_repo_id(session, repo_id)
    except Exception as e:
        session.logger.info(
            f"Could not create endpoint from repo {repo_id} because of ERROR: {e}")
        # Exit on failure
        return


    contrib_entry_info = {
        'given': {
            'github_url': endpoint,
            'git_url': endpoint,
            'gitlab_url': endpoint
        }
    }

    query_github_contributors(session,contrib_entry_info, repo_id)
    