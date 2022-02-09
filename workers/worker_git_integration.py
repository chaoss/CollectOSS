#Get everything that the base depends on.
import math

from numpy.lib.utils import source
from workers.worker_base import *
import sqlalchemy as s
import time
import math

#This is a worker base subclass that adds the ability to query github/gitlab with the api key
class WorkerGitInterfaceable(Worker):
    def __init__(self, worker_type, config={}, given=[], models=[], data_tables=[], operations_tables=[], platform="github"):
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        self.config.update({
            'gh_api_key': self.augur_config.get_value('Database', 'key'),
            'gitlab_api_key': self.augur_config.get_value('Database', 'gitlab_api_key')
        })

        #Fix loose attribute definition
        self.headers = None
        self.platform = platform
        self.given = given
        self.models = models

        self.specs = {
            'id': self.config['id'], # what the broker knows this worker as
            'location': self.config['location'], # host + port worker is running on (so broker can send tasks here)
            'qualifications':  [
                {
                    'given': self.given, # type of repo this worker can be given as a task
                    'models': self.models # models this worker can fill for a repo as a task
                }
            ],
            'config': self.config
        }

        # Send broker hello message

				# Attempts to determine if these attributes exist
				# If not, it creates them with default values
        try:
            self.tool_source
            self.tool_version
            self.data_source
        except AttributeError:
            self.tool_source = 'Augur Worker Testing'
            self.tool_version = '0.0.0'
            self.data_source = 'Augur Worker Testing'

    #database interface, additional functionality with github interface.
    def initialize_database_connections(self):
        super().initialize_database_connections()
        # Organize different api keys/oauths available
        self.logger.info("Initializing API key.")
        if 'gh_api_key' in self.config or 'gitlab_api_key' in self.config:
            try:
                self.init_oauths(self.platform)
            except AttributeError:
                self.logger.error("Worker not configured to use API key!")
        else:
            self.oauths = [{'oauth_id': 0}]

    def find_id_from_login(self, login, platform='github'):
        """ Retrieves our contributor table primary key value for the contributor with
            the given GitHub login credentials, if this contributor is not there, then
            they get inserted.

        :param login: String, the GitHub login username to find the primary key id for
        :return: Integer, the id of the row in our database with the matching GitHub login
        """
        idSQL = s.sql.text("""
            SELECT cntrb_id FROM contributors WHERE cntrb_login = '{}' \
            AND LOWER(data_source) = '{} api'
            """.format(login, platform))

        rs = pd.read_sql(idSQL, self.db, params={})
        data_list = [list(row) for row in rs.itertuples(index=False)]
        try:
            return data_list[0][0]
        except:
            self.logger.info('contributor needs to be added...')

        if platform == 'github':
            cntrb_url = ("https://api.github.com/users/" + login)
        elif platform == 'gitlab':
            cntrb_url = ("https://gitlab.com/api/v4/users?username=" + login )
        self.logger.info("Hitting endpoint: {} ...\n".format(cntrb_url))

				# Possible infinite loop if this request never succeeds?
        while True:
            try:
                r = requests.get(url=cntrb_url, headers=self.headers)
                break
            except TimeoutError as e:
                self.logger.info("Request timed out. Sleeping 10 seconds and trying again...\n")
                time.sleep(30)

        self.update_rate_limit(r)
        contributor = r.json()

				# Used primarily for the Gitlab block below
        company = None
        location = None
        email = None
        if 'company' in contributor:
            company = contributor['company']
        if 'location' in contributor:
            location = contributor['location']
        if 'email' in contributor:
            email = contributor['email']

        ''' Because a user name nan exists, we needed to cast any string where their 
            user name appears as a string, because otherwise python was casting it as a float '''
        if platform == 'github':
            cntrb = {
                'cntrb_login': str(contributor['login']) if 'login' in contributor else None,
                'cntrb_email': str(contributor['email']) if 'email' in contributor else None,
                'cntrb_company': str(contributor['company']) if 'company' in contributor else None,
                'cntrb_location': str(contributor['location']) if 'location' in contributor else None,
                'cntrb_created_at': contributor['created_at'] if 'created_at' in contributor else None,
                'cntrb_canonical': str(contributor['email']) if 'email' in contributor else None,
                'gh_user_id': contributor['id'] if 'id' in contributor else None,
                'gh_login': str(contributor['login']) if 'login' in contributor else None,
                'gh_url': str(contributor['url']) if 'url' in contributor else None,
                'gh_html_url': str(contributor['html_url']) if 'html_url' in contributor else None,
                'gh_node_id': contributor['node_id'] if 'node_id' in contributor else None,
                'gh_avatar_url': str(contributor['avatar_url']) if 'avatar_url' in contributor else None,
                'gh_gravatar_id': str(contributor['gravatar_id']) if 'gravatar_id' in contributor else None,
                'gh_followers_url': str(contributor['followers_url']) if 'followers_url' in contributor else None,
                'gh_following_url': str(contributor['following_url']) if 'following_url' in contributor else None,
                'gh_gists_url': str(contributor['gists_url']) if 'gists_url' in contributor else None,
                'gh_starred_url': str(contributor['starred_url']) if 'starred_url' in contributor else None,
                'gh_subscriptions_url': str(contributor['subscriptions_url']) if 'subscriptions_url' in contributor else None,
                'gh_organizations_url': str(contributor['organizations_url']) if 'organizations_url' in contributor else None,
                'gh_repos_url': str(contributor['repos_url']) if 'repos_url' in contributor else None,
                'gh_events_url': str(contributor['events_url']) if 'events_url' in contributor else None,
                'gh_received_events_url': str(contributor['received_events_url']) if 'received_events_url' in contributor else None,
                'gh_type': contributor['type'] if 'type' in contributor else None,
                'gh_site_admin': contributor['site_admin'] if 'site_admin' in contributor else None,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }

        elif platform == 'gitlab':
            cntrb =  {
                'cntrb_login': contributor[0]['username'] if 'username' in contributor[0] else None,
                'cntrb_email': email,
                'cntrb_company': company,
                'cntrb_location': location,
                'cntrb_created_at': contributor[0]['created_at'] if 'created_at' in contributor[0] else None,
                'cntrb_canonical': email,
                'gh_user_id': contributor[0]['id'],
                'gh_login': contributor[0]['username'],
                'gh_url': contributor[0]['web_url'],
                'gh_html_url': None,
                'gh_node_id': None,
                'gh_avatar_url': contributor[0]['avatar_url'],
                'gh_gravatar_id': None,
                'gh_followers_url': None,
                'gh_following_url': None,
                'gh_gists_url': None,
                'gh_starred_url': None,
                'gh_subscriptions_url': None,
                'gh_organizations_url': None,
                'gh_repos_url': None,
                'gh_events_url': None,
                'gh_received_events_url': None,
                'gh_type': None,
                'gh_site_admin': None,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }
        result = self.db.execute(self.contributors_table.insert().values(cntrb))
        self.logger.info("Primary key inserted into the contributors table: " + str(result.inserted_primary_key))
        self.results_counter += 1
        self.cntrb_id_inc = int(result.inserted_primary_key[0])
        self.logger.info(f"Inserted contributor: {cntrb['cntrb_login']}\n")

        return self.find_id_from_login(login, platform)

    def init_oauths(self, platform='github'):

        self.oauths = []
        self.headers = None
        self.logger.info("Trying initialization.")
        # Make a list of api key in the config combined w keys stored in the database
        # Select endpoint to hit solely to retrieve rate limit
        #   information from headers of the response
        # Adjust header keys needed to fetch rate limit information from the API responses
        if platform == 'github':
            url = "https://api.github.com/users/sgoggins"
            oauthSQL = s.sql.text("""
                SELECT * FROM worker_oauth WHERE access_token <> '{}' and platform = 'github'
                """.format(self.config['gh_api_key']))
            key_name = 'gh_api_key'
            rate_limit_header_key = "X-RateLimit-Remaining"
            rate_limit_reset_header_key = "X-RateLimit-Reset"
        elif platform == 'gitlab':
            url = "https://gitlab.com/api/v4/version"
            oauthSQL = s.sql.text("""
                SELECT * FROM worker_oauth WHERE access_token <> '{}' and platform = 'gitlab'
                """.format(self.config['gitlab_api_key']))
            key_name = 'gitlab_api_key'
            rate_limit_header_key = 'ratelimit-remaining'
            rate_limit_reset_header_key = 'ratelimit-reset'

        for oauth in [{'oauth_id': 0, 'access_token': self.config[key_name]}] + json.loads(
            pd.read_sql(oauthSQL, self.helper_db, params={}).to_json(orient="records")
        ):
            if platform == 'github':
                self.headers = {'Authorization': 'token %s' % oauth['access_token']}
            elif platform == 'gitlab':
                self.headers = {'Authorization': 'Bearer %s' % oauth['access_token']}
            response = requests.get(url=url, headers=self.headers)
            self.oauths.append({
                    'oauth_id': oauth['oauth_id'],
                    'access_token': oauth['access_token'],
                    'rate_limit': int(response.headers[rate_limit_header_key]),
                    'seconds_to_reset': (
                        datetime.datetime.fromtimestamp(
                            int(response.headers[rate_limit_reset_header_key])
                        ) - datetime.datetime.now()
                    ).total_seconds()
                })
            self.logger.debug("Found OAuth available for use: {}".format(self.oauths[-1]))

        if len(self.oauths) == 0:
            self.logger.info(
                "No API keys detected, please include one in your config or in the "
                "worker_oauths table in the augur_operations schema of your database."
            )

        # First key to be used will be the one specified in the config (first element in
        #   self.oauths array will always be the key in use)
        if platform == 'github':
            self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}
        elif platform == 'gitlab':
            self.headers = {'Authorization': 'Bearer %s' % self.oauths[0]['access_token']}

        self.logger.info("OAuth initialized\n")

    def enrich_cntrb_id(
        self, data, key, action_map_additions={'insert': {'source': [], 'augur': []}},
        platform='github', prefix=''
    ):

        if not len(data):
            self.logger.info(f"Enrich contrib data is empty for {len(data)}, for the key {key}.")

            raise ValueError

        self.logger.info(f"Enriching contributor ids for {len(data)} data points...")

        source_df = pd.DataFrame(data)
        expanded_source_df = self._add_nested_columns(
            source_df.copy(), [key] + action_map_additions['insert']['source']
        )

        # Insert cntrbs that are not in db

        cntrb_action_map = {
            'insert': {
                'source': [key] + action_map_additions['insert']['source'] + [f'{prefix}id'],
                'augur': ['cntrb_login'] + action_map_additions['insert']['augur'] + ['gh_user_id']
            }
        }

        table_values_cntrb = self.db.execute(
            s.sql.select(self.get_relevant_columns(self.contributors_table,cntrb_action_map))
        ).fetchall()

        source_data = expanded_source_df.to_dict(orient='records')

        #Filter out bad data where we can't even hit the api.
        source_data = [data for data in source_data if f'{prefix}login' in data and data[f'{prefix}login'] != None and type(data[f'{prefix}login']) is str]

        self.logger.info(f"table_values_cntrb keys: {table_values_cntrb[0].keys()}")
        # self.logger.info(f"source_data keys: {source_data[0].keys()}")

        #We can't use this because of worker collisions
        #TODO: seperate this method into it's own worker.
        #cntrb_id_offset = self.get_max_id(self.contributors_table, 'cntrb_id') - 1

        self.logger.debug(f"Enriching {len(source_data)} contributors.")

        # source_data = source_data.loc[data[f'{prefix}login'] != 'nan']

        # loop through data to test if it is already in the database
        for index, data in enumerate(source_data):

            if data[f'{prefix}login'] == 'nan':
                self.logger.debug("Nan user found continuing")
                continue

            #removed this log because it was generating a lot of data.
            #self.logger.info(f"Enriching {index} of {len(source_data)}")

            user_unique_ids = []

            #Allow for alt identifiers to be checked if user.id is not present in source_data
            try:
                #This will trigger a KeyError if data has alt identifier.
                data[f'{prefix}id']
                for row in table_values_cntrb:
                    # removed checks for nan user in this block because this is getting all the gh_user_ids that are
                    # already in the database so it doesn't need to be filtered from the database, it needs to be
                    # filtered out so it is never inserted into the database
                    # Andrew Brain 12/21/2021
                    user_unique_ids.append(row['gh_user_id'])

            except KeyError:
                self.print_traceback("Enrich_cntrb_id, data doesn't have user.id. Using node_id instead", e, True)

            finally: 
                for row in table_values_cntrb:
                    try:
                        user_unique_ids.append(row['gh_node_id'])
                    except Exception as e:
                        self.logger.info(f"Error adding gh_node_id: {e}. Row: {row}")
                        self.print_traceback("", e, True)



            #self.logger.info(f"gh_user_ids: {gh_user_ids}")

            # self.logger.info(f"Users gh_user_id: {data['user.id']}")
            # in_user_ids = False
            # if data['user.id'] in gh_user_ids:
            #     in_user_ids = True
            # self.logger.info(f"{data['user.id']} is in gh_user_ids")

            # self.logger.info(f"table_values_cntrb len: {len(table_values_cntrb)}")

            #Deal with if data
            #See if we can check using the user.id
            source_data_id = None
            try:
                source_data_id = data[f'{prefix}id']
            except KeyError:
                source_data_id = data[f'{prefix}node_id']


            #if user.id is in the database then there is no need to add the contributor
            if source_data_id in user_unique_ids:

                self.logger.info("{} found in database".format(source_data_id))

                user_id_row = []
                try:
                    data[f'{prefix}id']
                    #gets the dict from the table_values_cntrb that contains data['user.id']
                    user_id_row = list(filter(lambda x: x['gh_user_id'] == source_data_id, table_values_cntrb))[0]
                    #### Andrew: in a small number of cases, using data on contributors originally gathered in late 2019, there
                    #### is a mismatch .. the gh_user_id for a login is different. I suspect this rare case to be one 
                    #### where a person did something that changed their gh_user_id ... I am unsure how this can happen ... 
                except KeyError:
                    user_id_row = list(filter(lambda x: x['gh_node_id'] == source_data_id, table_values_cntrb))[0]
                    #pass # 12/3/2021 SPG ... added pass to try to get past this key error in large inserts.
                    continue # 12/3/2021 SPG ... may be better inside a loop

                #assigns the cntrb_id to the source data to be returned to the workers
                data['cntrb_id'] = user_id_row['cntrb_id']
                self.logger.info(f"cntrb_id {data['cntrb_id']} found in database and assigned to enriched data")

            #contributor is not in the database
            else:

              self.logger.info("{} not in database, making api call".format(source_data_id))

              self.logger.info("login: {}".format(data[f'{prefix}login']))

              try:
                url = ("https://api.github.com/users/" + str(data[f'{prefix}login']))
              except Exception as e:
                self.logger.info(f"Error when creating url: {e}. Data: {data}")
                #pass # changed continue to pass 12/3/2021 SPG
                continue # changed back 12/3/2021 SPG
              attempts = 0
              contributor = None
              success = False

              while attempts < 10:
                self.logger.info(f"Hitting endpoint: {url} ...\n")
                try:
                  response = requests.get(url=url, headers=self.headers)
                except TimeoutError:
                  self.logger.info(f"User data request for enriching contributor data failed with {attempts} attempts! Trying again...")
                  time.sleep(10)
                  #pass # changed continue to pass 12/3/2021 SPG
                  continue # changed back 12/3/2021 SPG
                self.update_rate_limit(response,platform=platform)

                try:
                  contributor = response.json()
                except:
                  contributor = json.loads(json.dumps(response.text))
                  continue # added continue 12/3/2021 SPG


                if type(contributor) == dict:
                  self.logger.info("Request returned a dict!")
                  self.logger.info(f"Contributor data: {contributor}") 
                  # contributor['gh_login'] = str(contributor['gh_login']) ## cast as string by SPG on 11/28/2021 due to `nan` user
                  success = True
                  break
                elif type(contributor) == list:
                  self.logger.warning("Wrong type returned trying again...")
                  self.logger.info(f"Contributor data: {contributor}")
                elif type(contributor) == str:
                  self.logger.info(f"Warning! page_data was string: {contributor}\n")
                  if "<!DOCTYPE html>" in contributor:
                    self.logger.info("HTML was returned, trying again...\n")
                  elif len(contributor) == 0:
                    self.logger.warning("Empty string, trying again...\n")
                  else:
                    try:
                      contributor = json.loads(contributor)
                      # contributor['gh_login'] = str(contributor['gh_login']) ## cast as string by SPG on 11/28/2021 due to `nan` user                     
                      success = True
                      break
                    except:
                      pass
                attempts += 1
              if not success:
                break




              self.logger.info(f"Contributor data: {contributor}")

              cntrb = {
              "cntrb_login": contributor['login'],
              "cntrb_created_at": contributor['created_at'],
              "cntrb_email": contributor['email'] if 'email' in contributor else None,
              "cntrb_company": contributor['company'] if 'company' in contributor else None,
              "cntrb_location": contributor['location'] if 'location' in contributor else None,
              # "cntrb_type": , dont have a use for this as of now ... let it default to null
              "cntrb_canonical": contributor['email'] if 'email' in contributor else None,
              "gh_user_id": contributor['id'],
              "gh_login": str(contributor['login']),  ## cast as string by SPG on 11/28/2021 due to `nan` user
              "gh_url": contributor['url'],
              "gh_html_url": contributor['html_url'],
              "gh_node_id": contributor['node_id'],
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
              "tool_source": self.tool_source,
              "tool_version": self.tool_version,
              "data_source": self.data_source
              }

              #insert new contributor into database
              # TODO: make this method it's own worker. This errors because of collisions between github_worker and pull_request_worker.
              #We can solve this by making another worker with a queue. It wouldn't have to be too complicated.
              try:
                self.db.execute(self.contributors_table.insert().values(cntrb))
              except s.exc.IntegrityError:
                self.logger.info(f"there was a collision caught ....")
                self.logger.info(traceback.format_exc())
                #pass # added by sean 11/29/2021 ... think it might be blocking comment insertion otherwise
                continue # changed to continue on 12/3/2021
              except Exception as e:
                self.logger.info(f"Contributor was unable to be added to table! Attempting to get cntrb_id from table anyway because of possible collision. Error: {e}")
                #pass # added by sean 11/29/2021 ... think it might be blocking comment insertion otherwise
                continue 

              #Get the contributor id from the newly inserted contributor.
              cntrb_id_row = self.db.execute(
                  s.sql.select(self.get_relevant_columns(self.contributors_table,cntrb_action_map)).where(
                    self.contributors_table.c.gh_user_id==cntrb["gh_user_id"]
                  )
                ).fetchall()

              #Handle and log rare failure cases. If this part errors something is very wrong.
              if len(cntrb_id_row) == 1:
                data['cntrb_id'] = cntrb_id_row[0]['cntrb_id']
                self.logger.info(f"cntrb_id {data['cntrb_id']} found in database and assigned to enriched data")
              elif len(cntrb_id_row) == 0:
                self.logger.error("Couldn't find contributor in database. Something has gone very wrong. Augur ran into a contributor that is unable to be inserted into the contributors table but is also not present in that table.")
              else:
                self.logger.info(f"There are more than one contributors in the table with gh_user_id={cntrb['gh_user_id']}")


              cntrb_data = {
              'cntrb_id': int(data['cntrb_id']), # came through as a float. Fixed 11/28/2021, SPG
              'gh_node_id': cntrb['gh_node_id'],
              'cntrb_login': str(cntrb['cntrb_login']), # NaN user issue. Fixed 11/28/2021, SPG
              'gh_user_id': int(cntrb['gh_user_id']) # came through as a float. Fixed 11/28/2021, SPG
              }
              #This updates our list of who is already in the database as we iterate to avoid duplicates.
              #People who make changes tend to make more than one in a row.
              table_values_cntrb.append(cntrb_data)

        self.logger.info(
          "Contributor id enrichment successful, result has "
          f"{len(source_data)} data points.\n"
        )

        for data in source_data:

            self.logger.debug("User login type: " + str(type(data[f'{prefix}login'])) + ". Login: " + str(data[f'{prefix}login']))

            try:
                data['cntrb_id']
            except:
                self.logger.debug(f"AB ERROR: data exiting enrich_cntrb_id without cntrb_id, login is: " + str(data[f'{prefix}login']))

        return source_data

    # Try to construct the best url to ping GitHub's API for a username given an email.
    """
    I changed this because of the following note on the API site: With the in qualifier you can restrict your search to the username (login), full name, public email, or any combination of these. When you omit this qualifier, only the username and email address are searched. For privacy reasons, you cannot search by email domain name.

    https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-users#search-only-users-or-organizations

    """

    def create_endpoint_from_email(self, email):
        self.logger.info(f"Trying to resolve contributor from email: {email}")
        # Note: I added "+type:user" to avoid having user owned organizations be returned
        # Also stopped splitting per note above.
        url = 'https://api.github.com/search/users?q={}+in:email+type:user'.format(
            email)
        

        return url
    
    def query_github_contributors(self, entry_info, repo_id):

        """ Data collection function
        Query the GitHub API for contributors
        """
        self.logger.info(f"Querying contributors with given entry info: {entry_info}\n")

        ## It absolutely doesn't matter if the contributor has already contributoed to a repo. it only matters that they exist in our table, and
        ## if the DO, then we DO NOT want to insert them again in any GitHub Method.
        github_url = entry_info['given']['github_url'] if 'github_url' in entry_info['given'] else entry_info['given']['git_url']

        # Extract owner/repo from the url for the endpoint
        try:
            owner, name = self.get_owner_repo(github_url)
        except IndexError as e:
            self.logger.error(f"Encountered bad entry info: {entry_info}")
            return

        # Set the base of the url and place to hold contributors to insert
        contributors_url = (
            f"https://api.github.com/repos/{owner}/{name}/" +
            "contributors?per_page=100&page={}"
        )

        # Get contributors that we already have stored
        #   Set our duplicate and update column map keys (something other than PK) to
        #   check dupicates/needed column updates with
        table = 'contributors'
        table_pkey = 'cntrb_id'
        update_col_map = {'cntrb_email': 'email'}
        duplicate_col_map = {'cntrb_login': 'login'}

        #list to hold contributors needing insertion or update
        contributors = self.paginate(contributors_url, duplicate_col_map, update_col_map, table, table_pkey)

        self.logger.info("Count of contributors needing insertion: " + str(len(contributors)) + "\n")

        for repo_contributor in contributors:
            try:
                # Need to hit this single contributor endpoint to get extra data including...
                #   `created at`
                #   i think that's it
                cntrb_url = ("https://api.github.com/users/" + repo_contributor['login'])
                self.logger.info("Hitting endpoint: " + cntrb_url + " ...\n")
                r = requests.get(url=cntrb_url, headers=self.headers)
                self.update_gh_rate_limit(r)
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

                cntrb = {
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
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }
                #dup check
                #TODO: add additional fields to check if needed.
                existingMatchingContributors = self.db.execute(
                    s.sql.select(
                        [self.contributors_table.c.gh_node_id]
                    ).where(
                        self.contributors_table.c.gh_node_id==cntrb["gh_node_id"]
                    )
                ).fetchall()

                if len(existingMatchingContributors) > 0:
                    break #if contributor already exists in table


                # Commit insertion to table
                if repo_contributor['flag'] == 'need_update':
                    result = self.db.execute(self.contributors_table.update().where(
                        self.worker_history_table.c.cntrb_email==email).values(cntrb))
                    self.logger.info("Updated tuple in the contributors table with existing email: {}".format(email))
                    self.cntrb_id_inc = repo_contributor['pkey']
                elif repo_contributor['flag'] == 'need_insertion':
                    result = self.db.execute(self.contributors_table.insert().values(cntrb))
                    self.logger.info("Primary key inserted into the contributors table: {}".format(result.inserted_primary_key))

                    #For workers that aren't an interface.
                    if self.worker_type != "Contributor_interface":
                        self.results_counter += 1

                    self.logger.info("Inserted contributor: " + contributor['login'] + "\n")

                    # Increment our global track of the cntrb id for the possibility of it being used as a FK
                    self.cntrb_id_inc = int(result.inserted_primary_key[0])

            except Exception as e:
                self.logger.error("Caught exception: {}".format(e))
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                self.logger.error("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
                continue

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
                time.sleep(60)

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
    
    #probably a better version of query_github_contributors but uses bulk_insert which is a bit shaky right now.
    def query_github_contributors_bulk(self, entry_info, repo_id):

        """ Data collection function
        Query the GitHub API for contributors.
        Uses paginate_endpoint rather than paginate, and supports stagger for larger repos.
        """
        self.logger.info(f"Querying contributors with given entry info: {entry_info}\n")

        github_url = entry_info['given']['github_url'] if 'github_url' in entry_info['given'] else entry_info['given']['git_url']

        owner, name = self.get_owner_repo(github_url)

        contributors_url = (f"https://api.github.com/repos/{owner}/{name}/" +
            "contributors?per_page=100&page={}")

        action_map = {
            'insert': {
                'source': ['login'],
                'augur': ['cntrb_login']
            },
            'update': {
                'source': ['email'],
                'augur': ['cntrb_email']
            }
        }

        source_contributors = self.paginate_endpoint(contributors_url, action_map=action_map,
            table=self.contributors_table)

        contributors_insert = []

        for repo_contributor in source_contributors['insert']:
            # Need to hit this single contributor endpoint to get extra data
            cntrb_url = (f"https://api.github.com/users/{repo_contributor['login']}")
            self.logger.info(f"Hitting endpoint: {cntrb_url} ...\n")
            r = requests.get(url=cntrb_url, headers=self.headers)
            self.update_gh_rate_limit(r)
            contributor = r.json()

            contributors_insert.append({
                'cntrb_login': contributor['login'],
                'cntrb_created_at': contributor['created_at'],
                'cntrb_email': contributor['email'] if 'email' in contributor else None,
                'cntrb_company': contributor['company'] if 'company' in contributor else None,
                'cntrb_location': contributor['location'] if 'location' in contributor else None,
                'cntrb_canonical': contributor['email'] if 'email' in contributor else None,
                'gh_user_id': contributor['id'],
                'gh_login': contributor['login'],
                'gh_url': contributor['url'],
                'gh_html_url': contributor['html_url'],
                'gh_node_id': contributor['node_id'],
                'gh_avatar_url': contributor['avatar_url'],
                'gh_gravatar_id': contributor['gravatar_id'],
                'gh_followers_url': contributor['followers_url'],
                'gh_following_url': contributor['following_url'],
                'gh_gists_url': contributor['gists_url'],
                'gh_starred_url': contributor['starred_url'],
                'gh_subscriptions_url': contributor['subscriptions_url'],
                'gh_organizations_url': contributor['organizations_url'],
                'gh_repos_url': contributor['repos_url'],
                'gh_events_url': contributor['events_url'],
                'gh_received_events_url': contributor['received_events_url'],
                'gh_type': contributor['type'],
                'gh_site_admin': contributor['site_admin'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            })

        contributors_insert_result, contributors_update_result = self.bulk_insert(self.contributors_table,
            update=source_contributors['update'], unique_columns=action_map['insert']['augur'],
            insert=contributors_insert, update_columns=action_map['update']['augur'])
    
    def query_gitlab_contributors(self, entry_info, repo_id):

        gitlab_url = (
            entry_info['given']['gitlab_url'] if 'gitlab_url' in entry_info['given']
            else entry_info['given']['git_url']
        )

        self.logger.info("Querying contributors with given entry info: " + str(entry_info) + "\n")

        path = urlparse(gitlab_url)
        split = path[2].split('/')

        owner = split[1]
        name = split[2]

        # Handles git url case by removing the extension
        if ".git" in name:
            name = name[:-4]

        url_encoded_format = quote(owner + '/' + name, safe='')

        table = 'contributors'
        table_pkey = 'cntrb_id'
        ### Here we are adding gitlab user information from the API
        ### Following Gabe's rework of the contributor worker.

        ### The GitLab API will NEVER give you an email. It will let you
        ### Query an email, but never give you one.
        ### ## Gitlab email api: https://gitlab.com/api/v4/users?search=s@goggins.com
        ### We don't need to update right now, so commenting out.
        ### TODO: SOLVE LOGIC.
        # update_col_map = {'cntrb_email': 'email'}
        update_col_map = {}
        duplicate_col_map = {'gl_username': 'username'}

        # list to hold contributors needing insertion or update
        contributors = self.paginate("https://gitlab.com/api/v4/projects/" + url_encoded_format + "/repository/contributors?per_page=100&page={}", duplicate_col_map, update_col_map, table, table_pkey, platform='gitlab')

        for repo_contributor in contributors:
            try:
                cntrb_compressed_url = ("https://gitlab.com/api/v4/users?search=" + repo_contributor['email'])
                self.logger.info("Hitting endpoint: " + cntrb_compressed_url + " ...\n")
                r = requests.get(url=cntrb_compressed_url, headers=self.headers)
                contributor_compressed = r.json()

                email = repo_contributor['email']
                self.logger.info(contributor_compressed)
                if len(contributor_compressed) == 0 or type(contributor_compressed) is dict or "id" not in contributor_compressed[0]:
                    continue

                self.logger.info("Fetching for user: " + str(contributor_compressed[0]["id"]))

                cntrb_url = ("https://gitlab.com/api/v4/users/" + str(contributor_compressed[0]["id"]))
                self.logger.info("Hitting end point to get complete contributor info now: " + cntrb_url + "...\n")
                r = requests.get(url=cntrb_url, headers=self.headers)
                contributor = r.json()

                cntrb = {
                    "gl_id": contributor.get('gl_id', None),
                    "gl_full_name": contributor.get('full_name', None),
                    "gl_username": contributor.get('username', None),
                    "gl_state": contributor.get('state', None),
                    "gl_avatar_url": contributor.get('avatar_url', None),
                    "gl_web_url": contributor.get('web_url', None),
                    #"cntrb_login": contributor.get('username', None),
                    #"cntrb_created_at": contributor.get('created_at', None),
                    "cntrb_email": ('email', None),
                    #"cntrb_company": contributor.get('organization', None),
                    #"cntrb_location": contributor.get('location', None),
                    # "cntrb_type": , dont have a use for this as of now ... let it default to null
                    #"cntrb_canonical": contributor.get('public_email', None),
                    #"gh_user_id": contributor.get('id', None),
                    #"gh_login": contributor.get('username', None),
                    #"gh_url": contributor.get('web_url', None),
                    #"gh_html_url": contributor.get('web_url', None),
                    #"gh_node_id": None,
                    #"gh_avatar_url": contributor.get('avatar_url', None),
                    #"gh_gravatar_id": None,
                    #"gh_followers_url": None,
                    #"gh_following_url": None,
                    #"gh_gists_url": None,
                    #"gh_starred_url": None,
                    #"gh_subscriptions_url": None,
                    #"gh_organizations_url": None,
                    #"gh_repos_url": None,
                    #"gh_events_url": None,
                    #"gh_received_events_url": None,
                    #"gh_type": None,
                    #"gh_site_admin": None,
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                # Commit insertion to table
                if repo_contributor['flag'] == 'need_update':
                    result = self.db.execute(self.contributors_table.update().where(
                        self.worker_history_table.c.cntrb_email == email).values(cntrb))
                    self.logger.info("Updated tuple in the contributors table with existing email: {}".format(email))
                    self.cntrb_id_inc = repo_contributor['pkey']
                elif repo_contributor['flag'] == 'need_insertion':
                    result = self.db.execute(self.contributors_table.insert().values(cntrb))
                    self.logger.info("Primary key inserted into the contributors table: {}".format(result.inserted_primary_key))
                    self.results_counter += 1

                    self.logger.info("Inserted contributor: " + contributor['username'] + "\n")

                    # Increment our global track of the cntrb id for the possibility of it being used as a FK
                    self.cntrb_id_inc = int(result.inserted_primary_key[0])

            except Exception as e:
                self.logger.info("Caught exception: {}".format(e))
                self.logger.info("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
                continue

    def update_gitlab_rate_limit(self, response, bad_credentials=False, temporarily_disable=False):
        # Try to get rate limit from request headers, sometimes it does not work (GH's issue)
        #   In that case we just decrement from last recieved header count
        if bad_credentials and len(self.oauths) > 1:
            self.logger.info(
                f"Removing oauth with bad credentials from consideration: {self.oauths[0]}"
            )
            del self.oauths[0]

        if temporarily_disable:
            self.logger.info("Gitlab rate limit reached. Temp. disabling...")
            self.oauths[0]['rate_limit'] = 0
        else:
            try:
                self.oauths[0]['rate_limit'] = int(response.headers['RateLimit-Remaining'])
            except:
                self.oauths[0]['rate_limit'] -= 1
        self.logger.info("Updated rate limit, you have: " +
            str(self.oauths[0]['rate_limit']) + " requests remaining.")
        if self.oauths[0]['rate_limit'] <= 0:
            try:
                reset_time = response.headers['RateLimit-Reset']
            except Exception as e:
                self.logger.info(f"Could not get reset time from headers because of error: {e}")
                reset_time = 3600
            time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
            self.logger.info("Rate limit exceeded, checking for other available keys to use.")

            # We will be finding oauth with the highest rate limit left out of our list of oauths
            new_oauth = self.oauths[0]
            # Endpoint to hit solely to retrieve rate limit information from headers of the response
            url = "https://gitlab.com/api/v4/version"

            other_oauths = self.oauths[0:] if len(self.oauths) > 1 else []
            for oauth in other_oauths:
                # self.logger.info("Inspecting rate limit info for oauth: {}\n".format(oauth))
                self.headers = {"PRIVATE-TOKEN" : oauth['access_token']}
                response = requests.get(url=url, headers=self.headers)
                oauth['rate_limit'] = int(response.headers['RateLimit-Remaining'])
                oauth['seconds_to_reset'] = (
                    datetime.datetime.fromtimestamp(
                        int(response.headers['RateLimit-Reset'])
                    ) - datetime.datetime.now()
                ).total_seconds()

                # Update oauth to switch to if a higher limit is found
                if oauth['rate_limit'] > new_oauth['rate_limit']:
                    self.logger.info(f"Higher rate limit found in oauth: {oauth}")
                    new_oauth = oauth
                elif (
                    oauth['rate_limit'] == new_oauth['rate_limit']
                    and oauth['seconds_to_reset'] < new_oauth['seconds_to_reset']
                ):
                    self.logger.info(
                        f"Lower wait time found in oauth with same rate limit: {oauth}"
                    )
                    new_oauth = oauth

            if new_oauth['rate_limit'] <= 0 and new_oauth['seconds_to_reset'] > 0:
                self.logger.info(
                    "No oauths with >0 rate limit were found, waiting for oauth with "
                    f"smallest wait time: {new_oauth}\n"
                )
                time.sleep(new_oauth['seconds_to_reset'])

            # Make new oauth the 0th element in self.oauths so we know which one is in use
            index = self.oauths.index(new_oauth)
            self.oauths[0], self.oauths[index] = self.oauths[index], self.oauths[0]
            self.logger.info("Using oauth: {}\n".format(self.oauths[0]))

            # Change headers to be using the new oauth's key
            self.headers = {"PRIVATE-TOKEN" : self.oauths[0]['access_token']}

    def update_gh_rate_limit(self, response, bad_credentials=False, temporarily_disable=False):
        # Try to get rate limit from request headers, sometimes it does not work (GH's issue)
        #   In that case we just decrement from last recieved header count
        if bad_credentials and len(self.oauths) > 1:
            self.logger.warning(
                f"Removing oauth with bad credentials from consideration: {self.oauths[0]}"
            )
            del self.oauths[0]

        if temporarily_disable:
            self.logger.debug(
                "Github thinks we are abusing their api. Preventing use "
                "of this key until its rate limit resets..."
            )
            self.oauths[0]['rate_limit'] = 0
        else:
            try:
                self.oauths[0]['rate_limit'] = int(response.headers['X-RateLimit-Remaining'])
                # self.logger.info("Recieved rate limit from headers\n")
            except:
                self.oauths[0]['rate_limit'] -= 1
                self.logger.info("Headers did not work, had to decrement")
                time.sleep(30)

        self.logger.info(
            f"Updated rate limit, you have: {self.oauths[0]['rate_limit']} requests remaining."
        )

        #Stalls after here for some reason.
        if self.oauths[0]['rate_limit'] <= 0:
            try:
                reset_time = response.headers['X-RateLimit-Reset']
            except Exception as e:
                self.logger.error(f"Could not get reset time from headers because of error: {e}")
                reset_time = 3600
            time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
            self.logger.info("Rate limit exceeded, checking for other available keys to use.")

            # We will be finding oauth with the highest rate limit left out of our list of oauths
            new_oauth = self.oauths[0]
            # Endpoint to hit solely to retrieve rate limit information from headers of the response
            url = "https://api.github.com/users/sgoggins"

            other_oauths = self.oauths[0:] if len(self.oauths) > 1 else []
            for oauth in other_oauths:
                # self.logger.info("Inspecting rate limit info for oauth: {}\n".format(oauth))
                self.headers = {'Authorization': 'token %s' % oauth['access_token']}

                attempts = 3
                success = False
                while attempts > 0 and not success:
                    response = requests.get(url=url, headers=self.headers)
                    try:
                        oauth['rate_limit'] = int(response.headers['X-RateLimit-Remaining'])
                        oauth['seconds_to_reset'] = (
                            datetime.datetime.fromtimestamp(
                                int(response.headers['X-RateLimit-Reset'])
                            ) - datetime.datetime.now()
                        ).total_seconds()
                        success = True
                    except Exception as e:
                        self.logger.info(
                            f"oath method ran into error getting info from headers: {e}\n"
                        )
                        self.logger.info(f"{self.headers}\n{url}\n")
                    attempts -= 1
                if not success:
                    continue

                # Update oauth to switch to if a higher limit is found
                if oauth['rate_limit'] > new_oauth['rate_limit']:
                    self.logger.info("Higher rate limit found in oauth: {}\n".format(oauth))
                    new_oauth = oauth
                elif (
                    oauth['rate_limit'] == new_oauth['rate_limit']
                    and oauth['seconds_to_reset'] < new_oauth['seconds_to_reset']
                ):
                    self.logger.info(
                        f"Lower wait time found in oauth with same rate limit: {oauth}\n"
                    )
                    new_oauth = oauth

            if new_oauth['rate_limit'] <= 0 and new_oauth['seconds_to_reset'] > 0:
                self.logger.info(
                    "No oauths with >0 rate limit were found, waiting for oauth with "
                    f"smallest wait time: {new_oauth}\n"
                )
                time.sleep(new_oauth['seconds_to_reset'])

            # Make new oauth the 0th element in self.oauths so we know which one is in use
            index = self.oauths.index(new_oauth)
            self.oauths[0], self.oauths[index] = self.oauths[index], self.oauths[0]
            self.logger.info("Using oauth: {}\n".format(self.oauths[0]))

            # Change headers to be using the new oauth's key
            self.headers = {'Authorization': 'token %s' % self.oauths[0]['access_token']}

    def update_rate_limit(
        self, response, bad_credentials=False, temporarily_disable=False, platform="gitlab"
    ):
        if platform == 'gitlab':
            return self.update_gitlab_rate_limit(
                response, bad_credentials=bad_credentials, temporarily_disable=temporarily_disable
            )
        elif platform == 'github':
            return self.update_gh_rate_limit(
                response, bad_credentials=bad_credentials, temporarily_disable=temporarily_disable
            )

    #insertion_method and stagger are arguments that allow paginate_endpoint to insert at around ~500 pages at a time.
    def paginate_endpoint(
        self, url, action_map={}, table=None, where_clause=True, platform='github', in_memory=True, stagger=False, insertion_method=None, insertion_threshold=1000
    ):

        #Get augur columns using the action map along with the primary key
        table_values = self.db.execute(
            s.sql.select(self.get_relevant_columns(table, action_map)).where(where_clause)
        ).fetchall()

        page_number = 1
        multiple_pages = False
        need_insertion = []
        need_update = []

        #Stores sum of page data
        all_data = []
        forward_pagination = True
        backwards_activation = False
        last_page_number = -1

        #Block to handle page queries and retry at least 10 times
        while True:

            # Multiple attempts to hit endpoint
            num_attempts = 0
            success = False
            while num_attempts < 10:
                self.logger.info(f"Hitting endpoint: {url.format(page_number)}...\n")
                try:
                    response = requests.get(url=url.format(page_number), headers=self.headers)
                except TimeoutError as e:
                    self.logger.info("Request timed out. Sleeping 10 seconds and trying again...\n")
                    time.sleep(10)
                    continue

                self.update_rate_limit(response, platform=platform)

                try:
                    page_data = response.json()
                except:
                    page_data = json.loads(json.dumps(response.text))

                if type(page_data) == list:
                    success = True
                    break
                elif type(page_data) == dict:
                    self.logger.info("Request returned a dict: {}\n".format(page_data))
                    if page_data['message'] == "Not Found":
                        self.logger.warning(
                            "Github repo was not found or does not exist for endpoint: "
                            f"{url.format(page_number)}\n"
                        )
                        break
                    if "You have exceeded a secondary rate limit. Please wait a few minutes before you try again" in page_data['message']:
                        num_attempts -=1
                        self.logger.info('\n\n\n\nSleeping for 100 seconds due to secondary rate limit issue.\n\n\n\n')
                        time.sleep(100)
                    if "You have triggered an abuse detection mechanism." in page_data['message']:
                        num_attempts -= 1
                        self.update_rate_limit(response, temporarily_disable=True,platform=platform)
                    if page_data['message'] == "Bad credentials":
                        self.logger.info("\n\n\n\n\n\n\n POSSIBLY BAD TOKEN \n\n\n\n\n\n\n")
                        self.update_rate_limit(response, bad_credentials=True, platform=platform)
                elif type(page_data) == str:
                    self.logger.info(f"Warning! page_data was string: {page_data}\n")
                    if "<!DOCTYPE html>" in page_data:
                        self.logger.info("HTML was returned, trying again...\n")
                    elif len(page_data) == 0:
                        self.logger.warning("Empty string, trying again...\n")
                    else:
                        try:
                            page_data = json.loads(page_data)
                            success = True
                            break
                        except:
                            pass
                num_attempts += 1
            if not success:
              break

            # Success

            # Determine if continued pagination is needed

            if len(page_data) == 0:
                self.logger.info("Response was empty, breaking from pagination.\n")
                break

            all_data += page_data

            if not forward_pagination:

                # Checking contents of requests with what we already have in the db
                page_insertions, page_updates = self.organize_needed_data(
                    page_data, table_values, list(table.primary_key)[0].name,
                    action_map
                )

                # Reached a page where we already have all tuples
                if len(need_insertion) == 0 and len(need_update) == 0 and \
                        backwards_activation:
                    self.logger.info(
                        "No more pages with unknown tuples, breaking from pagination.\n"
                    )
                    break

                need_insertion += page_insertions
                need_update += page_updates

            # Find last page so we can decrement from there
            if 'last' in response.links and last_page_number == -1:
                if platform == 'github':
                    last_page_number = int(response.links['last']['url'][-6:].split('=')[1])
                elif platform == 'gitlab':
                    last_page_number = int(response.links['last']['url'].split('&')[2].split('=')[1])

                if not forward_pagination and not backwards_activation:
                    page_number = last_page_number
                    backwards_activation = True

            self.logger.info("Analyzation of page {} of {} complete\n".format(page_number,
                int(last_page_number) if last_page_number != -1 else "*last page not known*"))

            if (page_number <= 1 and not forward_pagination) or \
                    (page_number >= last_page_number and forward_pagination):
                self.logger.info("No more pages to check, breaking from pagination.\n")
                break

            #This is probably where we should insert at around ~500 at a time
            #makes sure that stagger is enabled, we have an insertion method, and the insertion happens every 500 pages or so.
            if stagger and insertion_method != None and page_number % insertion_threshold == 0:
                #call insertion method passed as argument.
                staggered_source_prs = {
                    'insert' : need_insertion,
                    'update' : need_update,
                    'all'    : all_data
                }

                #Use the method the subclass needs in order to insert the data.
                insertion_method(staggered_source_prs,action_map)

                #clear the data from memory and avoid duplicate insertions.
                need_insertion = []
                need_update = []
                all_data = []

            page_number = page_number + 1 if forward_pagination else page_number - 1

        if forward_pagination:
            need_insertion, need_update = self.organize_needed_data(
                all_data, table_values, list(table.primary_key)[0].name, action_map
            )

        return {
            'insert': need_insertion,
            'update': need_update,
            'all': all_data
        }

    #TODO: deprecated but still used by many other methods
    def paginate(self, url, duplicate_col_map, update_col_map, table, table_pkey, where_clause="", value_update_col_map={}, platform="github"):
        """ DEPRECATED
            Paginate either backwards or forwards (depending on the value of the worker's
            finishing_task attribute) through all the GitHub or GitLab api endpoint pages.

        :param url: String, the url of the API endpoint we are paginating through, expects
            a curly brace string formatter within the string to format the Integer
            representing the page number that is wanted to be returned
        :param duplicate_col_map: Dictionary, maps the column names of the source data
            to the field names in our database for columns that should be checked for
            duplicates (if source data value == value in existing database row, then this
            element is a duplicate and would not need an insertion). Key is source data
            column name, value is database field name. Example: {'id': 'gh_issue_id'}
        :param update_col_map: Dictionary, maps the column names of the source data
            to the field names in our database for columns that should be checked for
            updates (if source data value != value in existing database row, then an
            update is needed). Key is source data column name, value is database field name.
            Example: {'id': 'gh_issue_id'}
        :param table: String, the name of the table that holds the values to check for
            duplicates/updates against
        :param table_pkey: String, the field name of the primary key of the table in
            the database that we are getting the values for to cross-reference to check
            for duplicates.
        :param where_clause: String, optional where clause to filter the values
            that are queried when preparing the values that will be cross-referenced
            for duplicates/updates
        :param value_update_col_map: Dictionary, sometimes we add a new field to a table,
            and we want to trigger an update of that row in the database even if all of the
            data values are the same and would not need an update ordinarily. Checking for
            a specific existing value in the database field allows us to do this. The key is the
            name of the field in the database we are checking for a specific value to trigger
            an update, the value is the value we are checking for equality to trigger an update.
            Example: {'cntrb_id': None}
        :return: List of dictionaries, all data points from the pages of the specified API endpoint
            each with a 'flag' key-value pair representing the required action to take with that
            data point (i.e. 'need_insertion', 'need_update', 'none')
        """

        update_keys = list(update_col_map.keys()) if update_col_map else []
        update_keys += list(value_update_col_map.keys()) if value_update_col_map else []
        cols_to_query = list(duplicate_col_map.keys()) + update_keys + [table_pkey]
        table_values = self.get_table_values(cols_to_query, [table], where_clause)

        i = 1
        multiple_pages = False
        tuples = []
        while True:
            num_attempts = 0
            success = False
            while num_attempts < 3:
                self.logger.info(f'Hitting endpoint: {url.format(i)}...\n')
                r = requests.get(url=url.format(i), headers=self.headers)

                self.update_rate_limit(r, platform=platform)
                if 'last' not in r.links:
                    last_page = None
                else:
                    if platform == "github":
                        last_page = r.links['last']['url'][-6:].split('=')[1]
                    elif platform == "gitlab":
                        last_page =  r.links['last']['url'].split('&')[2].split("=")[1]
                    self.logger.info("Analyzing page {} of {}\n".format(i, int(last_page) + 1 if last_page is not None else '*last page not known*'))

                try:
                    j = r.json()
                except:
                    j = json.loads(json.dumps(r.text))

                if type(j) != dict and type(j) != str:
                    success = True
                    break
                elif type(j) == dict:
                    self.logger.info("Request returned a dict: {}\n".format(j))
                    if j['message'] == 'Not Found':
                        self.logger.warning("Github repo was not found or does not exist for endpoint: {}\n".format(url))
                        break
                    if j['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                        num_attempts -= 1
                        self.logger.info("rate limit update code goes here")
                        self.update_rate_limit(r, temporarily_disable=True,platform=platform)
                    if j['message'] == 'Bad credentials':
                        self.logger.info("rate limit update code goes here")
                        self.update_rate_limit(r, bad_credentials=True, platform=platform)
                elif type(j) == str:
                    self.logger.info(f'J was string: {j}\n')
                    if '<!DOCTYPE html>' in j:
                        self.logger.info('HTML was returned, trying again...\n')
                    elif len(j) == 0:
                        self.logger.warning('Empty string, trying again...\n')
                    else:
                        try:
                            j = json.loads(j)
                            success = True
                            break
                        except:
                            pass
                num_attempts += 1
            if not success:
                break

            # Find last page so we can decrement from there
            if 'last' in r.links and not multiple_pages and not self.finishing_task:
                if platform == "github":
                    param = r.links['last']['url'][-6:]
                    i = int(param.split('=')[1]) + 1
                elif platform == "gitlab":
                    i = int(r.links['last']['url'].split('&')[2].split("=")[1]) + 1
                self.logger.info("Multiple pages of request, last page is " + str(i - 1) + "\n")
                multiple_pages = True
            elif not multiple_pages and not self.finishing_task:
                self.logger.info("Only 1 page of request\n")
            elif self.finishing_task:
                self.logger.info("Finishing a previous task, paginating forwards ..."
                    " excess rate limit requests will be made\n")

            if len(j) == 0:
                self.logger.info("Response was empty, breaking from pagination.\n")
                break

            # Checking contents of requests with what we already have in the db
            j = self.assign_tuple_action(j, table_values, update_col_map, duplicate_col_map, table_pkey, value_update_col_map)

            if not j:
                self.logger.error("Assigning tuple action failed, moving to next page.\n")
                i = i + 1 if self.finishing_task else i - 1
                continue
            try:
                to_add = [obj for obj in j if obj not in tuples and (obj['flag'] != 'none')]
            except Exception as e:
                self.logger.error("Failure accessing data of page: {}. Moving to next page.\n".format(e))
                i = i + 1 if self.finishing_task else i - 1
                continue
            if len(to_add) == 0 and multiple_pages and 'last' in r.links:
                self.logger.info("{}".format(r.links['last']))
                if platform == "github":
                    page_number = int(r.links['last']['url'][-6:].split('=')[1])
                elif platform == "gitlab":
                    page_number = int(r.links['last']['url'].split('&')[2].split("=")[1])
                if i - 1 != page_number:
                    self.logger.info("No more pages with unknown tuples, breaking from pagination.\n")
                    break

            tuples += to_add

            i = i + 1 if self.finishing_task else i - 1

            # Since we already wouldve checked the first page... break
            if (i == 1 and multiple_pages and not self.finishing_task) or i < 1 or len(j) == 0:
                self.logger.info("No more pages to check, breaking from pagination.\n")
                break

        return tuples

    def new_paginate_endpoint(
        self, url, action_map={}, table=None, where_clause=True, platform='github'
    ):

        page_number = 1
        multiple_pages = False
        need_insertion = []
        need_update = []
        all_data = []
        forward_pagination = True
        backwards_activation = False
        last_page_number = -1
        while True:

            # Multiple attempts to hit endpoint
            num_attempts = 0
            success = False
            while num_attempts < 10:
                self.logger.info("hitting an endpiont")
                #    f"Hitting endpoint: ...\n"
                #    f"{url.format(page_number)} on page number. \n")
                try:
                    response = requests.get(url=url.format(page_number), headers=self.headers)
                except TimeoutError as e:
                    self.logger.info("Request timed out. Sleeping 10 seconds and trying again...\n")
                    time.sleep(10)
                    continue

                self.update_rate_limit(response, platform=platform)

                try:
                    page_data = response.json()
                except:
                    page_data = json.loads(json.dumps(response.text))

                if type(page_data) == list:
                    success = True
                    break
                elif type(page_data) == dict:
                    self.logger.info("Request returned a dict: {}\n".format(page_data))
                    if page_data['message'] == "Not Found":
                        self.logger.warning(
                            "Github repo was not found or does not exist for endpoint: "
                            f"{url.format(page_number)}\n"
                        )
                        break
                    if "You have triggered an abuse detection mechanism." in page_data['message']:
                        num_attempts -= 1
                        self.update_rate_limit(response, temporarily_disable=True,platform=platform)
                    if page_data['message'] == "Bad credentials":
                        self.update_rate_limit(response, bad_credentials=True, platform=platform)
                elif type(page_data) == str:
                    self.logger.info(f"Warning! page_data was string: {page_data}\n")
                    if "<!DOCTYPE html>" in page_data:
                        self.logger.info("HTML was returned, trying again...\n")
                    elif len(page_data) == 0:
                        self.logger.warning("Empty string, trying again...\n")
                    else:
                        try:
                            page_data = json.loads(page_data)
                            success = True
                            break
                        except:
                            pass
                num_attempts += 1
            if not success:
                break

            # Success

            # Determine if continued pagination is needed

            if len(page_data) == 0:
                self.logger.info("Response was empty, breaking from pagination.\n")
                break

            all_data += page_data

            if not forward_pagination:

                # Checking contents of requests with what we already have in the db
                page_insertions, page_updates = self.new_organize_needed_data(
                    page_data, augur_table=table, action_map=action_map
                )

                # Reached a page where we already have all tuples
                if len(need_insertion) == 0 and len(need_update) == 0 and \
                        backwards_activation:
                    self.logger.info(
                        "No more pages with unknown tuples, breaking from pagination.\n"
                    )
                    break

                need_insertion += page_insertions
                need_update += page_updates

            # Find last page so we can decrement from there
            if 'last' in response.links and last_page_number == -1:
                if platform == 'github':
                    last_page_number = int(response.links['last']['url'][-6:].split('=')[1])
                elif platform == 'gitlab':
                    last_page_number = int(response.links['last']['url'].split('&')[2].split('=')[1])

                if not forward_pagination and not backwards_activation:
                    page_number = last_page_number
                    backwards_activation = True

            self.logger.info("Analyzation of page {} of {} complete\n".format(page_number,
                int(last_page_number) if last_page_number != -1 else "*last page not known*"))

            if (page_number <= 1 and not forward_pagination) or \
                    (page_number >= last_page_number and forward_pagination):
                self.logger.info("No more pages to check, breaking from pagination.\n")
                break

            page_number = page_number + 1 if forward_pagination else page_number - 1

        if forward_pagination:
            need_insertion, need_update = self.new_organize_needed_data(
                all_data, augur_table=table, action_map=action_map
            )

        return {
            'insert': need_insertion,
            'update': need_update,
            'all': all_data
        }
