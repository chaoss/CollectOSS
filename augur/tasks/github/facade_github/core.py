from augur.tasks.github.facade_github.contributor_interfaceable import contributor_interface
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

    session.logger.info("Count of contributors needing insertion: " + str(len(contributor_list)) + "\n")


    #TODO raise exception if repo not exist.

    if len(contributor_list) == 0:
        return

    for repo_contributor in contributor_list:
        try:
            # Need to hit this single contributor endpoint to get extra data including...
            #   `created at`
            #   i think that's it
            cntrb_url = ("https://api.github.com/users/" + repo_contributor['login'])

            
            session.logger.info("Hitting endpoint: " + cntrb_url + " ...\n")
            r = hit_api(session, cntrb_url)
            contributor = r.json()

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
            #dup check
            #TODO: add additional fields to check if needed.
            #existingMatchingContributors = self.db.execute(
            #    s.sql.select(
            #        [self.contributors_table.c.gh_node_id]
            #    ).where(
            #        self.contributors_table.c.gh_node_id==cntrb["gh_node_id"]
            #    )
            #).fetchall()

            #stmnt = select(Contributors.gh_node_id).where(Contributors.gh_node_id == cntrb["gh_node_id"])
            existingMatchingContributors = session.query(Contributor).filter_by(gh_node_id=cntrb["gh_node_id"]).all() #session.execute(stmnt)

            if len(existingMatchingContributors) > 0:
                break #if contributor already exists in table

            cntrb_natural_keys = ['cntrb_login']
            #insert cntrb to table.
            session.insert_data(cntrb,Contributor,cntrb_natural_keys)
            
        except Exception as e:
            session.logger.error("Caught exception: {}".format(e))
            session.logger.error(f"Traceback: {traceback.format_exc()}")
            session.logger.error("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
            continue

# Hit the endpoint specified by the url and return the json that it returns if it returns a dict.
# Returns None on failure.
def request_dict_from_endpoint(session, url, timeout_wait=10):
    #session.logger.info(f"Hitting endpoint: {url}")

    attempts = 0
    response_data = None
    success = False

    while attempts < 10:
        try:
            response = hit_api(session, url)
        except TimeoutError:
            session.logger.info(
                f"User data request for enriching contributor data failed with {attempts} attempts! Trying again...")
            time.sleep(timeout_wait)
            continue

        if not response:
            attempts += 1
            continue
        
        try:
            response_data = response.json()
        except:
            response_data = json.loads(json.dumps(response.text))

        if type(response_data) == dict:
            err = process_dict_response(session.logger,response,response_data)

            #If we get an error message that's not None
            if err:
                attempts += 1
                continue

            # self.logger.info(f"Returned dict: {response_data}")
            success = True
            break
        elif type(response_data) == list:
            session.logger.warning("Wrong type returned, trying again...")
            session.logger.info(f"Returned list: {response_data}")
        elif type(response_data) == str:
            session.logger.info(
                f"Warning! page_data was string: {response_data}")
            if "<!DOCTYPE html>" in response_data:
                session.logger.info("HTML was returned, trying again...\n")
            elif len(response_data) == 0:
                session.logger.warning("Empty string, trying again...\n")
            else:
                try:
                    # Sometimes raw text can be converted to a dict
                    response_data = json.loads(response_data)

                    err = process_dict_response(session.logger,response,response_data)

                    #If we get an error message that's not None
                    if err:
                        continue
                    
                    success = True
                    break
                except:
                    pass
        attempts += 1
    if not success:
        return None

    return response_data


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
    