from requests.api import head
from workers.worker_base import *
import logging
from logging import FileHandler, Formatter, StreamHandler
from workers.worker_git_integration import WorkerGitInterfaceable
from workers.util import read_config
from psycopg2.errors import UniqueViolation
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

# TODO : Make this borrow everything that it can from the facade worker.
# i.e. port, logging, etc


class ContributorInterfaceable(WorkerGitInterfaceable):
    def __init__(self, config={}, special_rate_limit=10):
        # Define the data tables that we are needing
        # Define the tables needed to insert, update, or delete on
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
        self.config.update(self.augur_config.get_section("Logging"))

        # Get the same logging dir as the facade worker.
        self.config.update({
            # self.config['port_database'])
            'id': "workers.{}.{}".format("contributor_interface", "226")
        })

        # Getting stuck here.
        self.initialize_logging()
        # self.logger = logging.getLogger(self.config["id"])
        # Test logging after init.
        self.logger.info(
            "Facade worker git interface logging set up correctly")
        # self.db_schema = None
        self.config.update({
            'gh_api_key': self.augur_config.get_value('Database', 'key'),
            'gitlab_api_key': self.augur_config.get_value('Database', 'gitlab_api_key')
        })

        # Get config passed from the facade worker.
        self.initialize_database_connections()
        self.logger.info("Facade worker git interface database set up")

        # set up the max amount of requests this interface is allowed to make before sleeping for 2 minutes
        self.special_rate_limit = special_rate_limit
        self.recent_requests_made = 0

        self.logger.info("Facade now has contributor interface.")

    def initialize_logging(self):
        # Get the log level in upper case from the augur config's logging section.
        self.config['log_level'] = self.config['log_level'].upper()
        if self.config['debug']:
            self.config['log_level'] = 'DEBUG'

        if self.config['verbose']:
            format_string = AugurLogging.verbose_format_string
        else:
            format_string = AugurLogging.simple_format_string

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
        self.tool_version = '\'0.1.0\''
        self.data_source = '\'Git Log\''

    # Try to construct the best url to ping GitHub's API for a username given an email.
    """
    I changed this because of the following note on the API site: With the in qualifier you can restrict your search to the username (login), full name, public email, or any combination of these. When you omit this qualifier, only the username and email address are searched. For privacy reasons, you cannot search by email domain name.

    https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-users#search-only-users-or-organizations

    """
    def create_endpoint_from_email(self, email):
        self.logger.info(f"Trying to resolve contributor from email: {email}")
        #Note: I added "+type:user" to avoid having user owned organizations be returned
        #Also stopped splitting per note above. 
        self.logger.info(f"Trying to resolve contributor from email: {email}")

        url = 'https://api.github.com/search/users?q={}+in:email&&{}+in:email'.format(email)
        #url = 'https://api.github.com/search/users?q={}+in:email+type:user'.format(cmt_cntrb['email'])
        self.logger.info(f"url is: {url}")
        #(
        #    email.split('@')[0], email.split('@')[-1])

        return url

    # Try to construct the best url to ping GitHub's API for a username given a full name.
    def create_endpoint_from_name(self, contributor):
        self.logger.info(f"Trying to resolve contributor: {contributor}")

        # Try to get the 'names' field if 'commit_name' field is not present in contributor data.
        name_field = 'commit_name' if 'commit_name' in contributor else 'name'

        try:
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
        except:
            cmt_cntrb = {
                'fname': contributor[name_field].split()[0]
            }
            url = 'https://api.github.com/search/users?q=fullname:{}'.format(
                cmt_cntrb['fname'])

        return url

    # Hit the endpoint specified by the url and return the json that it returns if it returns a dict.
    # Returns None on failure.
    def request_dict_from_endpoint(self, url, timeout_wait=10):
        self.logger.info(f"Hitting endpoint: {url}")

        attempts = 0
        response_data = None
        success = False

        # This borrow's the logic to safely hit an endpoint from paginate_endpoint.
        while attempts < 10:
            try:
                response = requests.get(url=url, headers=self.headers)
            except TimeoutError:
                self.logger.info(
                    f"User data request for enriching contributor data failed with {attempts} attempts! Trying again...")
                time.sleep(timeout_wait)
                continue

            # Make sure we know how many requests our api tokens have.
            self.update_rate_limit(response, platform="github")

            # Update the special rate limit
            self.recent_requests_made += 1

            # Sleep if we have made a lot of requests recently
            if self.recent_requests_made == self.special_rate_limit:
                self.recent_requests_made = 0
                self.logger.info(
                    f"Special rate limit of {self.special_rate_limit} reached! Sleeping for thirty seconds.")
                # Sleep for thirty seconds before making a new request.
                time.sleep(20)

            try:
                response_data = response.json()
            except:
                response_data = json.loads(json.dumps(response.text))

            if type(response_data) == dict:
                # Sometimes GitHub Sends us an error message in a dict instead of a string.
                # While a bit annoying, it is easy to work around
                if 'message' in response_data:
                    try:
                        assert 'API rate limit exceeded' not in response_data['message']
                    except AssertionError as e:
                        self.logger.info(
                            f"Detected error in response data from gitHub. Trying again... Error: {e}")
                        attempts += 1
                        continue

                # self.logger.info(f"Returned dict: {response_data}")
                success = True
                break
            elif type(response_data) == list:
                self.logger.warning("Wrong type returned, trying again...")
                self.logger.info(f"Returned list: {response_data}")
            elif type(response_data) == str:
                self.logger.info(
                    f"Warning! page_data was string: {response_data}")
                if "<!DOCTYPE html>" in response_data:
                    self.logger.info("HTML was returned, trying again...\n")
                elif len(response_data) == 0:
                    self.logger.warning("Empty string, trying again...\n")
                else:
                    try:
                        # Sometimes raw text can be converted to a dict
                        response_data = json.loads(response_data)
                        success = True
                        break
                    except:
                        pass
            attempts += 1
        if not success:
            return None

        return response_data

    def insert_alias(self, contributor, commit_emails):
        # Insert cntrb_id and email of the corresponding record into the alias table
        # Another database call to get the contributor id is needed because its an autokeyincrement that is accessed by multiple workers
        # Same principle as enrich_cntrb_id method.
        contributor_table_data = self.db.execute(
            s.sql.select([s.column('cntrb_id'), s.column('cntrb_canonical')]).where(
                self.contributors_table.c.gh_user_id == contributor["gh_user_id"]
            )
        ).fetchall()

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


        for email in commit_emails:
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
                pass
                self.logger.info(f"aliase {alias} already exists")
            except Exception as e:
                self.logger.info(
                    f"Ran into issue with alias: {alias}. Error: {e}")

        return

    # Takes the user data from the endpoint as arg
    # Updates the alias table if the login is already in the contributor's table with the new email.
    # Returns whether the login was found in the contributors table
    def resolve_if_login_existing(self, contributor, commit_emails):
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
            self.insert_alias(contributor, commit_emails)
            return True

        # If not found, return false
        return False

    def update_contributor(self, cntrb, max_attempts=3):

        # Get primary key so that we can update
        contributor_table_data = self.db.execute(
            s.sql.select([s.column('cntrb_id')]).where(
                self.contributors_table.c.gh_user_id == cntrb["gh_user_id"]
            )
        ).fetchall()

        attempts = 0

        while attempts < max_attempts:
            try:
                # Using with on a sqlalchemy connection prevents 'Connection refused' error
                # Ensures all database requests use the same connection
                with self.db.connect() as connection:
                    # Use primary key to update the correct data.
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

    def fetch_username_from_email(self, emails):

        # Default to failed state
        login_json = None

        for email in emails:
            if len(email) <= 2:
                continue  # Don't bother with emails that are blank or less than 2 characters

            try:
                url = self.create_endpoint_from_email(email)
            except Exception as e:
                self.logger.info(
                    f"Couldn't resolve email url with given data. Reason: {e}")
        # If the method throws an error it means that we can't hit the endpoint so we can't really do much
                continue

            login_json = self.request_dict_from_endpoint(
                url, timeout_wait=30)

            # Check if the email result got anything, if it failed try a name search.
            if login_json == None or 'total_count' not in login_json or login_json['total_count'] == 0:
                self.logger.info(
                    f"Could not resolve the username from {email}")

                # Go back to failure condition
                login_json = None

                # Add the email that couldn't be resolved to a garbage table.

                unresolved = {
                    "email": email,
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
                continue
            else:
                # Return endpoint dictionary if email found it.
                return login_json

        # failure condition returns None
        return login_json

    # Update the contributors table from the data facade has gathered.

    def insert_facade_contributors(self, repo_id):
        self.logger.info(
            "Beginning process to insert contributors from facade commits for repo w entry info: {}\n".format(repo_id))

        # Get all of the commit data's emails and names from the commit table that do not appear in the contributors table
        new_contrib_sql = s.sql.text("""
                SELECT DISTINCT
                    commits.cmt_author_name AS NAME,--commits.cmt_id AS id,
                    commits.cmt_author_raw_email AS email_raw
                FROM
                    commits 
                WHERE
                    commits.repo_id = :repo_id
                    AND NOT EXISTS ( SELECT contributors.cntrb_email FROM contributors WHERE contributors.cntrb_email = commits.cmt_author_email ) 
                    AND (
                        commits.cmt_author_name 
                        ) IN (
                        SELECT 
                        C.cmt_author_name 
                    FROM
                        commits AS C 
                    WHERE
                        C.repo_id = :repo_id
                        AND C.cmt_author_email = commits.cmt_author_email 
                    GROUP BY
                        C.cmt_author_name
                    ) 
                GROUP BY
                    commits.cmt_author_name,
                    commits.cmt_author_raw_email
                order by name; 
        """)
        new_contribs = json.loads(pd.read_sql(new_contrib_sql, self.db, params={
                                  'repo_id': repo_id}).to_json(orient="records"))

        # Try to get GitHub API user data from each unique commit email.
        for contributor in new_contribs:

            # Get list of all emails in the commit data.
            # Start with the fields we know that we can start with
            emails = [contributor['email_raw']
                      if 'email_raw' in contributor else contributor['email']]

            # # Check if other emails match the previous, if they don't then add them
            # if contributor['email_raw'] not in emails:
            #     emails.append(contributor['email_raw'])

            # if contributor['committer_email'] not in emails:
            #     emails.append(contributor['committer_email'])

            # if contributor['committer_email_raw'] not in emails:
            #     emails.append(contributor['committer_email_raw'])

            self.logger.info(f"DEBUG: here is the email array: {emails}")

            #check each email to see if it already exists in contributor_aliases
            #The [:] is a python thing that lets us iterate over a copy of the list instead of the real thing, allowing deletion to take place in place.
            for email in emails[:]:
                try: 
                    #Look up email to see if resolved
                    alias_table_data = self.db.execute(
                        s.sql.select([s.column('alias_email')]).where(
                            self.contributors_aliases_table.c.alias_email == email
                        )
                    ).fetchall()

                    if len(alias_table_data) >= 1:
                        #delete from list if found.
                        emails.remove(email)
                except Exception as e:
                    self.logger.info(f"alias table query failed with error: {e}")

            self.logger.info(f"DEBUG: here is the email array after deletion: {emails}")

            #If all emails have been resolved. No need to hit any api's
            if len(emails) == 0:
                self.logger.info("Commit emails all found to be resolved. Continuing...")
                continue

            # Try to get login from all possible emails
            # Is None upon failure.
            login_json = self.fetch_username_from_email(emails)

            # Check if the email result got anything, if it failed try a name search.
            if login_json == None or 'total_count' not in login_json or login_json['total_count'] == 0:
                self.logger.info(
                    "Could not resolve the username from the email. Trying a name only search...")

                try:
                    url = self.create_endpoint_from_name(contributor)
                except Exception as e:
                    self.logger.info(
                        f"Couldn't resolve name url with given data. Reason: {e}")
                    continue

                login_json = self.request_dict_from_endpoint(
                    url, timeout_wait=30)

            # total_count is the count of username's found by the endpoint.
            if login_json == None or 'total_count' not in login_json:
                self.logger.info(
                    "Search query returned an empty response, moving on...\n")
                continue
            if login_json['total_count'] == 0:
                self.logger.info(
                    "Search query did not return any results, adding 1's to commits table...\n")

                emailToInsert = contributor['commit_email'] if 'commit_email' in contributor else contributor['email']

                try:
                    # At this point we know we can't do anything with the emails or the names provided so we make the cntrb_id foreign key 1
                    self.db.execute(self.commits_table.update().where(
                        self.commits_table.c.cmt_committer_email == emailToInsert
                    ).values({
                        'cmt_ght_author_id': 1
                    }))

                except Exception as e:
                    self.logger.info(
                        f"Could not enrich unresolvable email address with dummy data. Error: {e}")
                continue

            # Resolve any unresolved emails if we get to this point.
            #They will get added to the alias table later
            for email in emails:
                query = s.sql.text("""
                    DELETE FROM unresolved_commit_emails
                    WHERE email='{}'
                """.format(email))

                self.logger.info(f"Updating now resolved email {email}")

                try:
                    self.db.execute(query)
                except Exception as e:
                    self.logger.info(f"Deleting now resolved email failed with error: {e}")


            # Grab first result and make sure it has the highest match score
            match = login_json['items'][0]
            for item in login_json['items']:
                if item['score'] > match['score']:
                    match = item
            
            self.logger.info("When searching for a contributor with info {}, we found the following users: {}\n".format(
                contributor, match))

            # Check if gh_login exists in contributors table TODO

            url = ("https://api.github.com/users/" + match['login'])

            user_data = self.request_dict_from_endpoint(url)

            if user_data == None:
                self.logger.warning(
                    f"user_data was unable to be reached. Skipping...")
                continue

            # Use the email found in the commit data if api data is NULL
            emailFromCommitData = contributor['commit_email'] if 'commit_email' in contributor else contributor['email']

            # Get name from commit if not found by GitHub
            name_field = contributor['commit_name'] if 'commit_name' in contributor else contributor['name']

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
                "cntrb_full_name": name_field if 'name' not in user_data else user_data['name'],
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source
            }
            # Check if the github login exists in the contributors table and add the emails to alias' if it does.

            # Also update the contributor record with commit data if we can.

            try:
                if not self.resolve_if_login_existing(cntrb, emails):
                    try:
                        self.db.execute(
                            self.contributors_table.insert().values(cntrb))

                        # Update alias after insertion. Insertion needs to happen first so we can get the autoincrementkey
                        self.insert_alias(cntrb, emails)
                    except Exception as e:
                        self.logger.info(
                            f"Ran into likely database collision. Assuming contributor exists in database. Error: {e}")
                else:
                    self.update_contributor(cntrb)
            except LookupError as e:
                self.logger.info(
                    f"Contributor id not able to be found in database despite the user_id existing. Something very wrong is happening. Error: {e}")

        # sql query used to find corresponding cntrb_id's of emails found in the contributor's table
        resolve_email_to_cntrb_id_sql = s.sql.text("""
          select distinct cntrb_id, contributors.cntrb_email, commits.cmt_author_raw_email
          from
              contributors, commits
          where
              contributors.cntrb_email = commits.cmt_author_raw_email
          union
          select distinct cntrb_id, contributors.cntrb_email, commits.cmt_committer_raw_email
          from
              contributors, commits
          where
              contributors.cntrb_email = commits.cmt_committer_raw_email
              AND commits.repo_id =:repo_id
        """)

        # sql query to get emails from current repo that already exist in the contributor's table.

        # existing_contrib_sql = s.sql.text("""
        #  select distinct contributors.cntrb_email, commits.cmt_author_raw_email
        #  from
        #      contributors, commits
        #  where
        #      contributors.cntrb_email = commits.cmt_author_raw_email
        #      AND commits.repo_id =:repo_id
        #  union
        #  select distinct contributors.cntrb_email, commits.cmt_committer_raw_email
        #  from
        #      contributors, commits
        #  where
        #      contributors.cntrb_email = commits.cmt_committer_raw_email
        #      AND commits.repo_id =:repo_id
        # """)

        # Get a list of dicts that contain the emails and cntrb_id's of commits that appear in the contributor's table.
        existing_cntrb_emails = json.loads(pd.read_sql(resolve_email_to_cntrb_id_sql, self.db, params={
                                           'repo_id': repo_id}).to_json(orient="records"))

        # iterate through all the commits with emails that appear in contributors and give them the relevant cntrb_id.
        for cntrb_email in existing_cntrb_emails:
            self.logger.info(
                f"These are the emails and cntrb_id's  returned: {cntrb_email}")
            self.db.execute(self.commits_table.update().where(
                self.commits_table.c.cmt_committer_email == cntrb_email['cntrb_email']
            ).values({
                'cmt_ght_author_id': cntrb_email['cntrb_id']
            }))

        return
