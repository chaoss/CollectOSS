from augur.tasks.github.facade_github.contributor_interfaceable.contributor_interface import * 
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.github.util.github_task_session import *
from augur.application.db.models import *
from augur.tasks.util.AugurUUID import GithubUUID
from augur.application.db.lib import bulk_insert_dicts, batch_insert_contributors
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

            # Extract all available profile fields using .get() so we never miss or crash on
            # optional keys. Email is only present when the user has made it public or when
            # the request is appropriately authenticated (see GitHub API docs).
            email = contributor.get('email')
            canonical_email = email
            company = contributor.get('company')
            location = contributor.get('location')
            full_name = contributor.get('name')
            created_at = contributor.get('created_at')
            updated_at = contributor.get('updated_at')

            # TODO get and store an owner id

            # Generate ID for cntrb table
            cntrb_id = GithubUUID()
            cntrb_id["user"] = int(contributor['id'])
            cntrb_id["platform"] = platform_id

            cntrb = {
                "cntrb_id": cntrb_id.to_UUID(),
                "cntrb_login": contributor['login'],
                "cntrb_created_at": created_at,
                "cntrb_email": email,
                "cntrb_company": company,
                "cntrb_location": location,
                "cntrb_canonical": canonical_email,
                "cntrb_full_name": full_name,
                "cntrb_last_used": updated_at,
                "gh_user_id": contributor['id'],
                "gh_login": contributor['login'],
                "gh_url": contributor.get('url'),
                "gh_html_url": contributor.get('html_url'),
                "gh_node_id": contributor.get('node_id'),
                "gh_avatar_url": contributor.get('avatar_url'),
                "gh_gravatar_id": contributor.get('gravatar_id'),
                "gh_followers_url": contributor.get('followers_url'),
                "gh_following_url": contributor.get('following_url'),
                "gh_gists_url": contributor.get('gists_url'),
                "gh_starred_url": contributor.get('starred_url'),
                "gh_subscriptions_url": contributor.get('subscriptions_url'),
                "gh_organizations_url": contributor.get('organizations_url'),
                "gh_repos_url": contributor.get('repos_url'),
                "gh_events_url": contributor.get('events_url'),
                "gh_received_events_url": contributor.get('received_events_url'),
                "gh_type": contributor.get('type'),
                "gh_site_admin": contributor.get('site_admin'),
            }

            #insert cntrb to table.
            #session.logger.info(f"Contributor:  {cntrb}  \n")
            batch_insert_contributors(logger, [cntrb])
            
        except Exception as e:
            logger.error("Caught exception: {}".format(e))
            logger.error("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
            raise e

# Get all the committer data for a repo.
# Used by facade in facade03analyzecommit
def grab_committer_list(logger, key_auth, repo_git, platform="github"):

    # Create API endpoint from repo_id
    query_github_contributors(logger, key_auth, repo_git)
    