from augur.tasks.github.facade_github.contributor_interfaceable.contributor_interface import * 
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.github.util.github_task_session import *
from augur.application.db.models import *
from augur.tasks.util.AugurUUID import GithubUUID
from augur.application.db.lib import bulk_insert_dicts
from augur.tasks.github.util.github_data_access import GithubDataAccess




def query_github_contributors(logger, key_auth, github_url):

    """ Data collection function
    Query the GitHub API for contributors
    """

    # Set platform id to 1 since it is a github method
    platform_id = 1

    # Extract owner/repo from the url for the endpoint
    try:
        owner, name = get_owner_repo(github_url)
    except IndexError as e:
        logger.error(f"Encountered bad url: {github_url}")
        raise e

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

    github_data_access = GithubDataAccess(key_auth, logger)

    contributor_count = github_data_access.get_resource_count(contributors_url)

    logger.info("Count of contributors needing insertion: " + str(contributor_count) + "\n")

    if contributor_count == 0:
        return

    for repo_contributor in github_data_access.paginate_resource(contributors_url):
        try:
            # Need to hit this single contributor endpoint to get extra data including...
            #   `created at`
            #   i think that's it
            cntrb_url = ("https://api.github.com/users/" + repo_contributor['login'])

            
            logger.info("Hitting endpoint: " + cntrb_url + " ...\n")
            #r = hit_api(session.oauths, cntrb_url, logger)
            #contributor = r.json()

            contributor = github_data_access.get_resource(cntrb_url)

            #logger.info(f"Contributor: {contributor} \n")
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
            cntrb_id["platform"] = platform_id

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
            bulk_insert_dicts(logger, cntrb,Contributor,cntrb_natural_keys)
            
        except Exception as e:
            logger.error("Caught exception: {}".format(e))
            logger.error("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
            raise e

# Get all the committer data for a repo.
# Used by facade in facade03analyzecommit
def grab_committer_list(logger, key_auth, repo_git, platform="github"):

    # Create API endpoint from repo_id
    query_github_contributors(logger, key_auth, repo_git)
    