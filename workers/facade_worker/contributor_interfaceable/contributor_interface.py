from requests.api import head
from workers.worker_base import *
import logging
from logging import FileHandler, Formatter, StreamHandler, log
from workers.worker_git_integration import WorkerGitInterfaceable
from workers.util import read_config
from psycopg2.errors import UniqueViolation
from random import randint
import json
import multiprocessing
import time
import numpy as np

# Debugger
import traceback

#Method to parallelize, takes a queue of data and iterates over it.
def process_commit_metadata(contributorQueue,interface,repo_id):
    
    for contributor in contributorQueue:
        # Get the email from the commit data
        email = contributor['email_raw'] if 'email_raw' in contributor else contributor['email']
    
        name = contributor['name']

        # check the email to see if it already exists in contributor_aliases
        try:
            # Look up email to see if resolved
            alias_table_data = interface.db.execute(
                s.sql.select([s.column('alias_email')]).where(
                    interface.contributors_aliases_table.c.alias_email == email
                )
            ).fetchall()
            if len(alias_table_data) >= 1:
                # Move on if email resolved

                #interface.logger.info(
                #    f"Email {email} has been resolved earlier.")

                continue
        except Exception as e:
            interface.logger.info(
                f"alias table query failed with error: {e}")
        
        #Check the unresolved_commits table to avoid hitting endpoints that we know don't have relevant data needlessly
        try:
            unresolved_query_result = interface.db.execute(
                s.sql.select([s.column('email'),s.column('name')]).where(
                    interface.unresolved_commit_emails_table.c.name == name and interface.unresolved_commit_emails_table.c.email == email
                )
            ).fetchall()

            if len(unresolved_query_result) >= 1:

                #interface.logger.info(f"Commit data with email {email} has been unresolved in the past, skipping...")

                continue
        except Exception as e:
            interface.logger.info(f"Failed to query unresolved alias table with error: {e}")
    

        login = None
    
        #Check the contributors table for a login for the given name
        try:
            contributors_with_matching_name = interface.db.execute(
                s.sql.select([s.column('gh_login')]).where(
                    interface.contributors_table.c.cntrb_full_name == name
                )
            ).fetchall()

            if len(contributors_with_matching_name) >= 1:
                login = contributors_with_matching_name[0]['gh_login']

        except Exception as e:
            interface.logger.error(f"Failed local login lookup with error: {e}")
        

        # Try to get the login from the commit sha
        if login == None or login == "":
            login = interface.get_login_with_commit_hash(contributor, repo_id)
    
        if login == None or login == "":
            # Try to get the login from supplemental data if not found with the commit hash
            login = interface.get_login_with_supplemental_data(contributor)
    
        if login == None:
            continue

        url = ("https://api.github.com/users/" + login)

        user_data = interface.request_dict_from_endpoint(url)

        if user_data == None:
            interface.logger.warning(
                f"user_data was unable to be reached. Skipping...")
            continue

        # Use the email found in the commit data if api data is NULL
        emailFromCommitData = contributor['email_raw'] if 'email_raw' in contributor else contributor['email']

        interface.logger.info(
            f"Successfully retrieved data from github for email: {emailFromCommitData}")

        # Get name from commit if not found by GitHub
        name_field = contributor['commit_name'] if 'commit_name' in contributor else contributor['name']

        try:

            # try to add contributor to database
            cntrb = {
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
                "tool_source": interface.tool_source,
                "tool_version": interface.tool_version,
                "data_source": interface.data_source
            }

        # interface.logger.info(f"{cntrb}")
        except Exception as e:
            interface.logger.info(f"Error when trying to create cntrb: {e}")
            continue
        # Check if the github login exists in the contributors table and add the emails to alias' if it does.

        # Also update the contributor record with commit data if we can.
        try:
            if not interface.resolve_if_login_existing(cntrb):
                try:
                    interface.db.execute(
                        interface.contributors_table.insert().values(cntrb))
                except Exception as e:
                    interface.logger.info(
                        f"Ran into likely database collision. Assuming contributor exists in database. Error: {e}")
            else:
                interface.update_contributor(cntrb)

            # Update alias after insertion. Insertion needs to happen first so we can get the autoincrementkey
            interface.insert_alias(cntrb, emailFromCommitData)
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

        interface.logger.info(f"Updating now resolved email {email}")

        try:
            interface.db.execute(query)
        except Exception as e:
            interface.logger.info(
                f"Deleting now resolved email failed with error: {e}")
    
    
    return



"""
This class serves as an extension for the facade worker to allow it to make api calls and interface with GitHub.
The motivation for doing it this way is because the functionality needed to interface with Github and/or GitLab
is contained within WorkerGitInterfaceable. This is a problem because facade was migrated into augur from its own
project and just making it inherit from a new class could have unintended consequences and moreover, the facade worker
doesn't even really need the WorkerGitInterfaceable for too much. This is mainly just to have better parity with the contributor
worker and table.
"""

"""
A few interesting ideas: Maybe get the top committers from each repo first? curl https://api.github.com/repos/chaoss/augur/contributors

"""


class ContributorInterfaceable(WorkerGitInterfaceable):
    
    def __init__(self, config={}, logger=None):
        # Define the data tables that we are needing
        # Define the tables needed to insert, update, or delete on

        worker_type = "contributor_interface"

        self.data_tables = ['contributors', 'pull_requests', 'commits',
                            'pull_request_assignees', 'pull_request_events', 'pull_request_labels',
                            'pull_request_message_ref', 'pull_request_meta', 'pull_request_repo',
                            'pull_request_reviewers', 'pull_request_teams', 'message', 'pull_request_commits',
                            'pull_request_files', 'pull_request_reviews', 'pull_request_review_message_ref',
                            'contributors_aliases', 'unresolved_commit_emails']
        self.operations_tables = ['worker_history', 'worker_job']

        self.platform = "github"
        # first set up logging.
        self._root_augur_dir = Persistant.ROOT_AUGUR_DIR
        self.augur_config = AugurConfig(self._root_augur_dir)

        # Get default logging settings
        self.config = config
        # self.config.update(self.augur_config.get_section("Logging"))

        # create a random port instead of 226
        # SPG 9/24/2021
        # self.facade_com = randint(47000,47555)

        # contrib_port = self.facade_com

        # Get the same logging dir as the facade worker.
        # self.config.update({
        #     # self.config['port_database'])
        #     'id': "workers.{}.{}".format("contributor_interface", contrib_port)
        # })

        # Getting stuck here.
        # self.initialize_logging()
        self.logger = logger

        
        self.finishing_task = False

        # try:

        #     theConfig = self.augur_config.get_section(["contributor_interface"])
        #     jsonConfig = json.loads(theConfig)
        #     self.logger.debug(f"The config for workers is: {json.dumps(jsonConfig, indent=2, sort_keys=True)}.")

        # except Exception as e:

        #     self.logger.debug(f"Exception in initialization is: {e}.")

        # self.logger = logging.getLogger(self.config["id"])
        # Test logging after init.
        self.logger.info(
            "Facade worker git interface logging set up correctly")
        # self.db_schema = None
        # Get config passed from the facade worker.
        self.config.update({
            'gh_api_key': self.augur_config.get_value('Database', 'key'),
            'gitlab_api_key': self.augur_config.get_value('Database', 'gitlab_api_key')
            # 'port': self.augur_config.get_value('Workers', 'contributor_interface')
        })

        
        tries = 5
        
        while tries > 0:
            try:
                self.initialize_database_connections()
                break
            except Exception as e:
                self.logger.error("Could not init database connection and oauth! {e}")
                
                if tries == 0:
                    raise e
            
            tries -= 1
                
        self.logger.info("Facade worker git interface database set up")
        self.logger.info(f"configuration passed is: {str(self.config)}.")

        # Needs to be an attribute of the class for incremental database insert using paginate_endpoint
        self.pk_source_prs = []

        self.logger.info("Facade now has contributor interface.")

        self.worker_type = "Contributor_interface"
        self.tool_source = '\'Facade Worker\''
        self.tool_version = '\'1.2.4\''
        self.data_source = '\'Git Log\''

        return

    def initialize_logging(self):
        # Get the log level in upper case from the augur config's logging section.
        self.config['log_level'] = self.config['log_level'].upper()
        if self.config['debug']:
            self.config['log_level'] = 'DEBUG'

        if self.config['verbose']:
            format_string = AugurLogging.verbose_format_string
        else:
            format_string = AugurLogging.simple_format_string

        format_string = AugurLogging.verbose_format_string

        # log_port = self.facade_com

        # Use stock python formatter for stdout
        formatter = Formatter(fmt=format_string)
        # User custom for stderr, Gives more info than verbose_format_string
        error_formatter = Formatter(fmt=AugurLogging.error_format_string)
        worker_type = "contributor_interface"
        worker_dir = AugurLogging.get_log_directories(
            self.augur_config, reset_logfiles=False) + "/workers/"
        Path(worker_dir).mkdir(exist_ok=True)
        logfile_dir = worker_dir + f"/{worker_type}/"
        Path(logfile_dir).mkdir(exist_ok=True)

        # Create more complex sublogs in the logfile directory determined by the AugurLogging class
        server_logfile = logfile_dir + \
            '{}_{}_server.log'.format(
                worker_type, self.config['port_database'])
        collection_logfile = logfile_dir + \
            '{}_{}_collection.log'.format(
                worker_type, self.config['port_database'])
        collection_errorfile = logfile_dir + \
            '{}_{}_collection.err'.format(
                worker_type, self.config['port_database'])
        self.config.update({
            'logfile_dir': logfile_dir,
            'server_logfile': server_logfile,
            'collection_logfile': collection_logfile,
            'collection_errorfile': collection_errorfile
        })

        collection_file_handler = FileHandler(
            filename=self.config['collection_logfile'], mode="a")
        collection_file_handler.setFormatter(formatter)
        collection_file_handler.setLevel(self.config['log_level'])

        collection_errorfile_handler = FileHandler(
            filename=self.config['collection_errorfile'], mode="a")
        collection_errorfile_handler.setFormatter(error_formatter)
        collection_errorfile_handler.setLevel(logging.WARNING)

        logger = logging.getLogger(self.config['id'])
        logger.handlers = []
        logger.addHandler(collection_file_handler)
        logger.addHandler(collection_errorfile_handler)
        logger.setLevel(self.config['log_level'])
        logger.propagate = False

        if self.config['debug']:
            self.config['log_level'] = 'DEBUG'
            console_handler = StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(self.config['log_level'])
            logger.addHandler(console_handler)

        if self.config['quiet']:
            logger.disabled = True

        self.logger = logger

        self.tool_source = '\'Facade Worker\'s Contributor Interface\''
        self.tool_version = '\'1.2.4\''
        self.data_source = '\'Git Log\''

    def create_endpoint_from_commit_sha(self, commit_sha, repo_id):
        self.logger.info(
            f"Trying to create endpoint from commit hash: {commit_sha}")

        # https://api.github.com/repos/chaoss/augur/commits/53b0cc122ac9ecc1588d76759dc2e8e437f45b48

        select_repo_path_query = s.sql.text("""
            SELECT repo_path, repo_name from repo
            WHERE repo_id = :repo_id_bind
        """)

        # Bind parameter
        select_repo_path_query = select_repo_path_query.bindparams(
            repo_id_bind=repo_id)
        result = self.db.execute(select_repo_path_query).fetchall()

        # if not found
        if not len(result) >= 1:
            raise LookupError

        if result[0]['repo_path'] is None or result[0]['repo_name'] is None:
            raise KeyError
        # print(result)

        # Else put into a more readable local var
        self.logger.info(f"Result: {result}")
        repo_path = result[0]['repo_path'].split(
            "/")[1] + "/" + result[0]['repo_name']

        url = "https://api.github.com/repos/" + repo_path + "/commits/" + commit_sha

        #self.logger.info(f"Url: {url}")

        return url


    # Try to construct the best url to ping GitHub's API for a username given a full name.
    def create_endpoint_from_name(self, contributor):
        self.logger.info(
            f"Trying to resolve contributor from name: {contributor}")

        # Try to get the 'names' field if 'commit_name' field is not present in contributor data.
        name_field = 'cmt_author_name' if 'commit_name' in contributor else 'name'

        # Deal with case where name is one word or none.
        if len(contributor[name_field].split()) < 2:
            raise ValueError
        cmt_cntrb = {
            'fname': contributor[name_field].split()[0],
            # Pythonic way to get the end of a list so that we truely get the last name.
            'lname': contributor[name_field].split()[-1]
        }
        url = 'https://api.github.com/search/users?q=fullname:{}+{}'.format(
            cmt_cntrb['fname'], cmt_cntrb['lname'])

        return url

    def insert_alias(self, contributor, email):
        # Insert cntrb_id and email of the corresponding record into the alias table
        # Another database call to get the contributor id is needed because its an autokeyincrement that is accessed by multiple workers
        # Same principle as enrich_cntrb_id method.
        contributor_table_data = self.db.execute(
            s.sql.select([s.column('cntrb_id'), s.column('cntrb_canonical')]).where(
                self.contributors_table.c.gh_user_id == contributor["gh_user_id"]
            )
        ).fetchall()

        # self.logger.info(f"Contributor query: {contributor_table_data}")

        # Handle potential failures
        if len(contributor_table_data) == 1:
            self.logger.info(
                f"cntrb_id {contributor_table_data[0]['cntrb_id']} found in database and assigned to enriched data")
        elif len(contributor_table_data) == 0:
            self.logger.error("Couldn't find contributor in database. Something has gone very wrong. Augur ran into a contributor whose login can be found in the contributor's table, but cannot be retrieved via the user_id that was gotten using the same login.")
            raise LookupError
        else:
            self.logger.info(
                f"There are more than one contributors in the table with gh_user_id={contributor['gh_user_id']}")

        self.logger.info(f"Creating alias for email: {email}")

        # Insert a new alias that corresponds to where the contributor was found
        # use the email of the new alias for canonical_email if the api returns NULL
        # TODO: It might be better to have the canonical_email allowed to be NUll because right now it has a null constraint.
        alias = {
            "cntrb_id": contributor_table_data[0]['cntrb_id'],
            "alias_email": email,
            "canonical_email": contributor['cntrb_canonical'] if 'cntrb_canonical' in contributor and contributor['cntrb_canonical'] is not None else email,
            "tool_source": self.tool_source,
            "tool_version": self.tool_version,
            "data_source": self.data_source
        }

        # Insert new alias
        try:
            self.db.execute(
                self.contributors_aliases_table.insert().values(alias))
        except s.exc.IntegrityError:
            # It's expected to catch duplicates this way so no output is logged.
            #pass
            self.logger.info(f"alias {alias} already exists")
        except Exception as e:
            self.logger.info(
                f"Ran into issue with alias: {alias}. Error: {e}")

        return

    # Takes the user data from the endpoint as arg
    # Updates the alias table if the login is already in the contributor's table with the new email.
    # Returns whether the login was found in the contributors table
    def resolve_if_login_existing(self, contributor):
        # check if login exists in contributors table
        select_cntrbs_query = s.sql.text("""
            SELECT cntrb_id from contributors
            WHERE cntrb_login = :gh_login_value
        """)

        # Bind parameter
        select_cntrbs_query = select_cntrbs_query.bindparams(
            gh_login_value=contributor['cntrb_login'])
        result = self.db.execute(select_cntrbs_query)

        # if yes
        if len(result.fetchall()) >= 1:
            # self.insert_alias(contributor, email) Functions should do one thing ideally.
            return True

        # If not found, return false
        self.logger.info(
            f"Contributor not found in contributors table but can be added. Adding...")
        return False

    def update_contributor(self, cntrb, max_attempts=3):

        # Get primary key so that we can update
        contributor_table_data = self.db.execute(
            s.sql.select([s.column('cntrb_id'), s.column('cntrb_canonical')]).where(
                self.contributors_table.c.gh_user_id == cntrb["gh_user_id"]
            )
        ).fetchall()

        attempts = 0

        # make sure not to overwrite canonical email if it isn't NULL

        canonical_email = contributor_table_data[0]['cntrb_canonical']
        # check if the contributor has a NULL canonical email or not
        #self.logger.info(f"The value of the canonical email is : {canonical_email}")

        if canonical_email is not None:
            del cntrb["cntrb_canonical"]
            self.logger.info(
                f"Existing canonical email {canonical_email} found in database and will not be overwritten.")

        while attempts < max_attempts:
            try:
                # Using with on a sqlalchemy connection prevents 'Connection refused' error
                # Ensures all database requests use the same connection
                with self.db.connect() as connection:
                    # Use primary key to update the correct data.
                    # It is important that non null data is not overwritten.
                    connection.execute(self.contributors_table.update().where(
                        self.contributors_table.c.cntrb_id == contributor_table_data[0]['cntrb_id']
                    ).values(cntrb))
                break  # break if success.
            except Exception as e:
                self.logger.info(
                    f"Ran into exception updating contributor with data: {cntrb}. Error: {e}")
                # give a delay so that we have a greater chance of success.
                time.sleep(1)

            attempts += 1

    # Try every distinct email found within a commit for possible username resolution.
    # Add email to garbage table if can't be resolved.
    #   \param contributor is the raw database entry
    #   \return A dictionary of response data from github with potential logins on success.
    #           None on failure

    def fetch_username_from_email(self, commit):

        # Default to failed state
        login_json = None

        self.logger.info(f"Here is the commit: {commit}")

        # email = commit['email_raw'] if 'email_raw' in commit else commit['email_raw']

        if len(commit['email_raw']) <= 2:
            return login_json  # Don't bother with emails that are blank or less than 2 characters

        try:
            url = self.create_endpoint_from_email(commit['email_raw'])
        except Exception as e:
            self.logger.info(
                f"Couldn't resolve email url with given data. Reason: {e}")
            # If the method throws an error it means that we can't hit the endpoint so we can't really do much
            return login_json

        login_json = self.request_dict_from_endpoint(
            url, timeout_wait=30)

        # Check if the email result got anything, if it failed try a name search.
        if login_json == None or 'total_count' not in login_json or login_json['total_count'] == 0:
            self.logger.info(
                f"Could not resolve the username from {commit['email_raw']}")

            # Go back to failure condition
            login_json = None

            # Add the email that couldn't be resolved to a garbage table.

            unresolved = {
                "email": commit['email_raw'],
                "name": commit['name'],
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source
            }

            self.logger.info(f"Inserting data to unresolved: {unresolved}")

            try:
                self.db.execute(
                    self.unresolved_commit_emails_table.insert().values(unresolved))
            except s.exc.IntegrityError:
                pass  # Pass because duplicate checking is expected
            except Exception as e:
                self.logger.info(
                    f"Could not create new unresolved email {unresolved['email']}. Error: {e}")
        else:
            # Return endpoint dictionary if email found it.
            return login_json

        # failure condition returns None
        return login_json

    # Method to return the login given commit data using the supplemental data in the commit
    #   -email
    #   -name
    def get_login_with_supplemental_data(self, commit_data):

        # Try to get login from all possible emails
        # Is None upon failure.
        login_json = self.fetch_username_from_email(commit_data)

        # Check if the email result got anything, if it failed try a name search.
        if login_json == None or 'total_count' not in login_json or login_json['total_count'] == 0:
            self.logger.info(
                "Could not resolve the username from the email. Trying a name only search...")

            try:
                url = self.create_endpoint_from_name(commit_data)
            except Exception as e:
                self.logger.info(
                    f"Couldn't resolve name url with given data. Reason: {e}")
                return None

            login_json = self.request_dict_from_endpoint(
                url, timeout_wait=30)

        # total_count is the count of username's found by the endpoint.
        if login_json == None or 'total_count' not in login_json:
            self.logger.info(
                "Search query returned an empty response, moving on...\n")
            return None
        if login_json['total_count'] == 0:
            self.logger.info(
                "Search query did not return any results, adding commit's table remains null...\n")

            return None

        # Grab first result and make sure it has the highest match score
        match = login_json['items'][0]
        for item in login_json['items']:
            if item['score'] > match['score']:
                match = item

        self.logger.info(
            "When searching for a contributor, we found the following users: {}\n".format(match))

        return match['login']

    def get_login_with_commit_hash(self, commit_data, repo_id):

        # Get endpoint for login from hash
        url = self.create_endpoint_from_commit_sha(
            commit_data['hash'], repo_id)

        # Send api request
        login_json = self.request_dict_from_endpoint(url)

        if login_json is None or 'sha' not in login_json:
            self.logger.info("Search query returned empty data. Moving on")
            return None

        try:
            match = login_json['author']['login']
        except:
            match = None

        return match

    # Update the contributors table from the data facade has gathered.
    def insert_facade_contributors(self, repo_id,processes=4,multithreaded=True):
        self.logger.info(
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
        """)
        new_contribs = json.loads(pd.read_sql(new_contrib_sql, self.db, params={
                                  'repo_id': repo_id}).to_json(orient="records"))

        
        if len(new_contribs) > 0 and multithreaded:
            
            #Split commits into mostly equal queues so each process starts with a workload and there is no
            #    overhead to pass into queue from the parent.
            
            numpyNewContribs = np.array(list(new_contribs))
            commitDataLists = np.array_split(numpyNewContribs, processes)
        
            processList = []
            #Create process start conditions
            for process in range(processes):
                interface = ContributorInterfaceable(config=self.config,logger=self.logger)

                processList.append(Process(target=process_commit_metadata, args=(commitDataLists[process].tolist(),interface,repo_id,)))
        
            #Multiprocess process commits
            for pNum,process in enumerate(processList):
                process.daemon = True
                process.start()
                self.logger.info(f"Process {pNum} started..")
            
        
            for pNum,process in enumerate(processList):
            
                process.join()

                self.logger.info(f"Process {pNum} has ended.")
        else:
            process_commit_metadata(list(new_contribs),self,repo_id)

        self.logger.debug("DEBUG: Got through the new_contribs")
        
        def link_commits_to_contributor(contributorQueue,logger,database, commits_table):
            # iterate through all the commits with emails that appear in contributors and give them the relevant cntrb_id.
            for cntrb_email in contributorQueue:
                logger.debug(
                   f"These are the emails and cntrb_id's  returned: {cntrb_email}")

                try:
                    database.execute(commits_table.update().where(
                        commits_table.c.cmt_committer_email == cntrb_email['email']
                    ).values({
                        'cmt_ght_author_id': cntrb_email['cntrb_id']
                    }))
                except Exception as e:
                    logger.info(
                        f"Ran into problem when enriching commit data. Error: {e}")
                    continue
            
            return

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
        """)

        #self.logger.info("DEBUG: got passed the sql statement declaration")
        # Get a list of dicts that contain the emails and cntrb_id's of commits that appear in the contributor's table.
        existing_cntrb_emails = json.loads(pd.read_sql(resolve_email_to_cntrb_id_sql, self.db, params={
                                           'repo_id': repo_id}).to_json(orient="records"))

        
        if len(existing_cntrb_emails) > 0 and multithreaded:
            
            #Split commits into mostly equal queues so each process starts with a workload and there is no
            #    overhead to pass into queue from the parent.
            
            numpyExistingCntrbEmails = np.array(list(existing_cntrb_emails))
            existingEmailsSplit = np.array_split(numpyExistingCntrbEmails,processes)
            
            processList = []
            #Create process start conditions
            for process in range(processes):
            
                processList.append(Process(target=link_commits_to_contributor, args=(existingEmailsSplit[process].tolist(),self.logger,self.db,self.commits_table,)))
        
        
            #Multiprocess process commits
            for pNum,process in enumerate(processList):
                process.daemon = True
                process.start()
                self.logger.info(f"Process {pNum} started..")
        
        
            for process in processList:
                process.join()
        else:
            link_commits_to_contributor(list(existing_cntrb_emails), self.logger, self.db, self.commits_table)

        self.logger.info("Done with inserting and updating facade contributors")
        return

    def create_endpoint_from_repo_id(self, repo_id):
        select_repo_path_query = s.sql.text("""
            SELECT repo_git from repo
            WHERE repo_id = :repo_id_bind
        """)

        # Bind parameter
        select_repo_path_query = select_repo_path_query.bindparams(
            repo_id_bind=repo_id)
        result = self.db.execute(select_repo_path_query).fetchall()

        # if not found
        if not len(result) >= 1:
            raise LookupError

        url = result[0]['repo_git']
        self.logger.info(f"Url: {url}")

        return url

    # Get all the committer data for a repo.
    # Used by facade in facade03analyzecommit

    def grab_committer_list(self, repo_id, platform="github"):

        # Create API endpoint from repo_id
        try:
            endpoint = self.create_endpoint_from_repo_id(repo_id)
        except Exception as e:
            self.logger.info(
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

        self.query_github_contributors(contrib_entry_info, repo_id)
        

