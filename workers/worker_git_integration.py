#Get everything that the base depends on.
from workers.worker_base import *
import sqlalchemy as s

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
        if self.config['offline_mode'] is False:
            self.connect_to_broker()

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


        if platform == 'github':
            cntrb = {
                'cntrb_login': contributor['login'] if 'login' in contributor else None,
                'cntrb_email': contributor['email'] if 'email' in contributor else None,
                'cntrb_company': contributor['company'] if 'company' in contributor else None,
                'cntrb_location': contributor['location'] if 'location' in contributor else None,
                'cntrb_created_at': contributor['created_at'] if 'created_at' in contributor else None,
                'cntrb_canonical': None,
                'gh_user_id': contributor['id'] if 'id' in contributor else None,
                'gh_login': contributor['login'] if 'login' in contributor else None,
                'gh_url': contributor['url'] if 'url' in contributor else None,
                'gh_html_url': contributor['html_url'] if 'html_url' in contributor else None,
                'gh_node_id': contributor['node_id'] if 'node_id' in contributor else None,
                'gh_avatar_url': contributor['avatar_url'] if 'avatar_url' in contributor else None,
                'gh_gravatar_id': contributor['gravatar_id'] if 'gravatar_id' in contributor else None,
                'gh_followers_url': contributor['followers_url'] if 'followers_url' in contributor else None,
                'gh_following_url': contributor['following_url'] if 'following_url' in contributor else None,
                'gh_gists_url': contributor['gists_url'] if 'gists_url' in contributor else None,
                'gh_starred_url': contributor['starred_url'] if 'starred_url' in contributor else None,
                'gh_subscriptions_url': contributor['subscriptions_url'] if 'subscriptions_url' in contributor else None,
                'gh_organizations_url': contributor['organizations_url'] if 'organizations_url' in contributor else None,
                'gh_repos_url': contributor['repos_url'] if 'repos_url' in contributor else None,
                'gh_events_url': contributor['events_url'] if 'events_url' in contributor else None,
                'gh_received_events_url': contributor['received_events_url'] if 'received_events_url' in contributor else None,
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
                'cntrb_canonical': None,
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

    #Blatently only for api key usage
    def init_oauths(self, platform='github'):

        self.oauths = []
        self.headers = None
        self.logger.info("Trying initialization.")
        # Make a list of api key in the config combined w keys stored in the database
        # Select endpoint to hit solely to retrieve rate limit
        #   information from headers of the response
        # Adjust header keys needed to fetch rate limit information from the API responses
        if platform == 'github':
            url = "https://api.github.com/users/gabe-heim"
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

        self.logger.info(f"table_values_cntrb type: {type(table_values_cntrb)}")
        self.logger.info(f"table_values_cntrb keys: {table_values_cntrb[0].keys()}")

        source_data = expanded_source_df.to_dict(orient='records')

        self.logger.info(f"source_data type: {type(source_data)}")
        self.logger.info(f"source_data keys: {source_data[0].keys()}")

        #This returns the max id + 1 so we undo that here.
        cntrb_id_offset = self.get_max_id(self.contributors_table, 'cntrb_id') - 1

        # loop through data to test if it is already in the database
        for index, data in enumerate(source_data):

            self.logger.info(f"Enriching {index} of {len(source_data)}")

            # create an array of gh_user_ids that are in the database
            gh_user_ids = []
            for row in table_values_cntrb:
              if row:
                gh_user_ids.append(row['gh_user_id'])
              
            # self.logger.info(f"Users gh_user_id: {data['user.id']}")
            # in_user_ids = False
            # if data['user.id'] in gh_user_ids:
            #     in_user_ids = True
            # self.logger.info(f"{data['user.id']} is in gh_user_ids")

            # self.logger.info(f"gh_user_ids len: {len(gh_user_ids)}")
            # self.logger.info(f"table_values_cntrb len: {len(table_values_cntrb)}")

            #self.logger.info(f"cntrb logins length: {len(cntrb_logins)}")
            #if user.id is in the database then there is no need to add the contributor
            if data[f'{prefix}id'] in gh_user_ids:

                self.logger.info("{} found in database".format(data[f'{prefix}id']))

                #gets the dict from the table_values_cntrb that contains data['user.id']
                user_id_row = list(filter(lambda x: x['gh_user_id'] == data[f'{prefix}id'], table_values_cntrb))[0]

                #assigns the cntrb_id to the source data to be returned to the workers
                data['cntrb_id'] = user_id_row['cntrb_id']
                self.logger.info(f"cntrb_id {data['cntrb_id']} found in database and assigned to enriched data")

            #contributor is not in the database
            else:

              self.logger.info("{} not in database, making api call".format(data[f'{prefix}id']))

              url = ("https://api.github.com/users/" + data[f'{prefix}login'])

              attempts = 0

              while attempts < 10:
                try:
                  attempts += 1
                  self.logger.info("Hitting endpoint: " + url + " ...\n")
                  response = requests.get(url=url , headers=self.headers)
                  break
                except TimeoutError:
                  self.logger.info(f"User data request for enriching contributor data failed with {attempts} attempts! Trying again...")
                  time.sleep(10)
                  continue
              
                try:
                  self.logger.info("Hitting endpoint: " + url + " ...\n")
                  response = requests.get(url=url , headers=self.headers)
                except Exception as e:
                  self.logger.error(f"Unable to hit the endpoint {url}")
                  raise e

                try:
                    contributor = response.json()
                except:
                    contributor = json.loads(json.dumps(response.text))

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
                "gh_login": contributor['login'],
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
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source
                }

                #insert new contributor into database
                self.db.execute(self.contributors_table.insert().values(cntrb))

                # increment cntrb_id offset
                # keeps track of the next cntrb_id primary key without making extra db queries
                cntrb_id_offset += 1

                #assigns the cntrb_id to the source data to be returned to the workers
                data['cntrb_id'] = cntrb_id_offset
                self.logger.info(f"cntrb_id {data['cntrb_id']} found with api call and assigned to enriched data")
                # add cntrb_id to data and append it to table_values_cntrb
                # so duplicate cntrbs within the same data set aren't added
                #cntrb['cntrb_id'] = cntrb_id_offset


                cntrb_data = {
                'cntrb_id': cntrb_id_offset,
                'gh_node_id': cntrb['gh_node_id'],
                'cntrb_login': cntrb['cntrb_login'],
                'gh_user_id': cntrb['gh_user_id']
                }
                table_values_cntrb.append(cntrb_data)

        self.logger.info(
          "Contributor id enrichment successful, result has "
          f"{len(source_data)} data points.\n"
        )
        return source_data







        # source_cntrb_insert, _ = self.organize_needed_data(
        #     expanded_source_df.to_dict(orient='records'), table_values=table_values_cntrb,
        #     action_map=cntrb_action_map
        # )

        # cntrb_insert = [
        #     {
        #         'cntrb_login': contributor[f'{prefix}login'],
        #         'cntrb_created_at': None if (
        #             f'{prefix}created_at' not in contributor
        #         ) else contributor[f'{prefix}created_at'],
        #         'cntrb_email': None if f'{prefix}email' not in contributor else contributor[f'{prefix}email'],
        #         'cntrb_company': None if f'{prefix}company' not in contributor else contributor[f'{prefix}company'],
        #         'cntrb_location': None if (
        #             f'{prefix}location' not in contributor
        #         ) else contributor[f'{prefix}location'],
        #         'gh_user_id': None if (
        #             not contributor[f'{prefix}id']
        #         ) else int(float(contributor[f'{prefix}id'])),
        #         'gh_login': contributor[f'{prefix}login'],
        #         'gh_url': contributor[f'{prefix}url'],
        #         'gh_html_url': contributor[f'{prefix}html_url'],
        #         'gh_node_id': contributor[f'{prefix}node_id'], #valid for dup check
        #         'gh_avatar_url': contributor[f'{prefix}avatar_url'],
        #         'gh_gravatar_id': contributor[f'{prefix}gravatar_id'],
        #         'gh_followers_url': contributor[f'{prefix}followers_url'],
        #         'gh_following_url': contributor[f'{prefix}following_url'],
        #         'gh_gists_url': contributor[f'{prefix}gists_url'],
        #         'gh_starred_url': contributor[f'{prefix}starred_url'],
        #         'gh_subscriptions_url': contributor[f'{prefix}subscriptions_url'],
        #         'gh_organizations_url': contributor[f'{prefix}organizations_url'],
        #         'gh_repos_url': contributor[f'{prefix}repos_url'],
        #         'gh_events_url': contributor[f'{prefix}events_url'],
        #         'gh_received_events_url': contributor[f'{prefix}received_events_url'],
        #         'gh_type': contributor[f'{prefix}type'],
        #         'gh_site_admin': contributor[f'{prefix}site_admin'],
        #         'tool_source': self.tool_source,
        #         'tool_version': self.tool_version,
        #         'data_source': self.data_source
        #     } for contributor in source_cntrb_insert if contributor[f'{prefix}login']
        # ]
        #
        # try:
        #     self.bulk_insert(self.contributors_table, cntrb_insert)
        # except s.exc.IntegrityError:
        #     self.logger.info("Unique Violation in contributors table! ")
        #
        # # Query db for inserted cntrb pkeys and add to shallow level of data
        #
        # # Query
        # cntrb_pk_name = list(self.contributors_table.primary_key)[0].name
        # session = s.orm.Session(self.db)
        # inserted_pks = pd.DataFrame(
        #     session.query(
        #         self.contributors_table.c[cntrb_pk_name], self.contributors_table.c.cntrb_login,
        #         self.contributors_table.c.gh_node_id
        #     ).distinct(self.contributors_table.c.cntrb_login).order_by(
        #         self.contributors_table.c.cntrb_login, self.contributors_table.c[cntrb_pk_name]
        #     ).all(), columns=[cntrb_pk_name, 'cntrb_login', 'gh_node_id']
        # ).to_dict(orient='records')
        # session.close()
        #
        # # Prepare for merge
        # source_columns = sorted(list(source_df.columns))
        # necessary_columns = sorted(list(set(source_columns + cntrb_action_map['insert']['source'])))
        # (source_table, inserted_pks_table), metadata, session = self._setup_postgres_merge(
        #     [
        #         expanded_source_df[necessary_columns].to_dict(orient='records'),
        #         inserted_pks
        #     ], sort=True
        # )
        # final_columns = [cntrb_pk_name] + sorted(list(set(necessary_columns)))
        #
        # # Merge
        # source_pk = pd.DataFrame(
        #     session.query(
        #         inserted_pks_table.c.cntrb_id, source_table
        #     ).join(
        #         source_table,
        #         eval(
        #             ' and '.join(
        #                 [
        #                     (
        #                         f"inserted_pks_table.c['{table_column}'] "
        #                         f"== source_table.c['{source_column}']"
        #                     ) for table_column, source_column in zip(
        #                         cntrb_action_map['insert']['augur'],
        #                         cntrb_action_map['insert']['source']
        #                     )
        #                 ]
        #             )
        #         )
        #     ).all(), columns=final_columns
        # )
        #
        # # Cleanup merge
        # source_pk = self._eval_json_columns(source_pk)
        # self._close_postgres_merge(metadata, session)

        self.logger.info(
            "Contributor id enrichment successful, result has "
            f"{len(source_pk)} data points.\n"
        )

        return source_pk.to_dict(orient='records')

    def query_github_contributors(self, entry_info, repo_id):

        """ Data collection function
        Query the GitHub API for contributors
        """
        self.logger.info(f"Querying contributors with given entry info: {entry_info}\n")

        ## It absolutely doesn't matter if the contributor has already contributoed to a repo. it only matters that they exist in our table, and
        ## if the DO, then we DO NOT want to insert them again in any GitHub Method.
        github_url = entry_info['given']['github_url'] if 'github_url' in entry_info['given'] else entry_info['given']['git_url']

        # Extract owner/repo from the url for the endpoint
        owner, name = self.get_owner_repo(github_url)

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
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }
                #dup check
                #TODO: add additional fields to check if needed.
                existingMatchingContributors = self.db.execute(
                    self.sql.select(
                        [self.contributors_table.c.gh_node_id]
                    ).where(
                        self.contributors_table.c.gh_node_id==cntrb["gh_node_id"]
                    ).fetchall()
                )

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
                    self.results_counter += 1

                    self.logger.info("Inserted contributor: " + contributor['login'] + "\n")

                    # Increment our global track of the cntrb id for the possibility of it being used as a FK
                    self.cntrb_id_inc = int(result.inserted_primary_key[0])

            except Exception as e:
                self.logger.error("Caught exception: {}".format(e))
                self.logger.error("Cascading Contributor Anomalie from missing repo contributor data: {} ...\n".format(cntrb_url))
                continue


    def query_github_contributors_bulk(self, entry_info, repo_id):

        """ Data collection function
        Query the GitHub API for contributors
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

    def query_github_contributors_fast(self, entry_info, repo_id):
        """ Data collection function
        Query the GitHub API for contributors
        """
        self.logger.info(f"Querying contributors with given entry info: {entry_info}")

        github_url = (
            entry_info['given']['github_url'] if 'github_url' in entry_info['given']
            else entry_info['given']['git_url']
        )

        contributors_url = (
            f"https://api.github.com/repos/{self.owner}/{self.name}/"
            "contributors?per_page=100&page={}"
        )

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

        source_contributors = self.paginate_endpoint(
            contributors_url, action_map=action_map, table=self.contributors_table
        )

        contributors_insert = [
            {
                'cntrb_login': contributor['login'],
                'cntrb_created_at': (
                    contributor['created_at'] if 'created_at' in contributor else None
                ),
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
            } for contributor in source_contributors['insert']
        ]

        self.bulk_insert(
            self.contributors_table, update=source_contributors['update'],
            unique_columns=action_map['insert']['augur'],
            insert=contributors_insert, update_columns=action_map['update']['augur']
        )

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
        self.logger.info(
            f"Updated rate limit, you have: {self.oauths[0]['rate_limit']} requests remaining."
        )
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
            url = "https://api.github.com/users/gabe-heim"

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

    #TODO: figure out if changing this typo breaks anything
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
        self.logger.info(
            f"Updated rate limit, you have: {self.oauths[0]['rate_limit']} requests remaining."
        )
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
            url = "https://api.github.com/users/gabe-heim"

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


    #Indexerror somewhere
    def multi_thread_urls(self, all_urls, max_attempts=5, platform='github'):
        """
        :param all_urls: list of tuples
        """

        if not len(all_urls):
            self.logger.info("No urls to multithread, returning blank list.\n")
            return []

        def load_url(url, extra_data={}):
            try:
                html = requests.get(url, stream=True, headers=self.headers)
                return html, extra_data
            except requests.exceptions.RequestException as e:
                self.logger.info(e, url)

        self.logger.info("Beginning to multithread API endpoints.")

        start = time.time()

        all_data = []
        valid_url_count = len(all_urls)

        partitions = math.ceil(len(all_urls) / 600)
        self.logger.info(f"{len(all_urls)} urls to process. Trying {partitions} partitions. " +
            f"Using {max(multiprocessing.cpu_count()//8, 1)} threads.")
        for urls in numpy.array_split(all_urls, partitions):
            attempts = 0
            self.logger.info(f"Total data points collected so far: {len(all_data)}")
            while len(urls) > 0 and attempts < max_attempts:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=max(multiprocessing.cpu_count()//8, 1)
                ) as executor:
                    # Start the load operations and mark each future with its URL
                    future_to_url = {executor.submit(load_url, *url): url for url in urls}
                    self.logger.info("Multithreaded urls and returned status codes:")
                    count = 0
                    for future in concurrent.futures.as_completed(future_to_url):

                        if count % 100 == 0:
                            self.logger.info(
                                f"Processed {len(all_data)} / {valid_url_count} urls. "
                                f"{len(urls)} remaining in this partition."
                            )
                        count += 1

                        url = future_to_url[future]
                        try:
                            response, extra_data = future.result()

                            if response.status_code != 200:
                                self.logger.info(
                                    f"Url: {url[0]} ; Status code: {response.status_code}"
                                )

                            if response.status_code == 403 or response.status_code == 401: # 403 is rate limit, 404 is not found, 401 is bad credentials
                                self.update_rate_limit(response, platform=platform)
                                continue

                            elif response.status_code == 200:
                                try:
                                    page_data = response.json()
                                except:
                                    page_data = json.loads(json.dumps(response.text))

                                page_data = [{**data, **extra_data} for data in page_data]
                                all_data += page_data

                                if 'last' in response.links and "&page=" not in url[0]:
                                    urls += [
                                        (url[0] + f"&page={page}", extra_data) for page in range(
                                            2, int(response.links['last']['url'].split('=')[-1]) + 1
                                        )
                                    ]
                                try:
                                    self.logger.info(f"urls boundry issue? for {urls} where they are equal to {url}.")

                                    urls = numpy.delete(urls, numpy.where(urls == url), axis=0)
                                except:
                                    self.logger.info(f"ERROR with axis = 0 - Now attempting without setting axis for numpy.delete for {urls} where they are equal to {url}.")
                                    urls = numpy.delete(urls, numpy.where(urls == url))

                            elif response.status_code == 404:
                                urls = numpy.delete(urls, numpy.where(urls == url), axis=0)
                                self.logger.info(f"Not found url: {url}\n")
                            else:
                                self.logger.info(
                                    f"Unhandled response code: {response.status_code} {url}\n"
                                )

                        except Exception as e:
                            self.logger.info(
                                f"{url} generated an exception: {traceback.format_exc()}\n"
                            )

                attempts += 1

        self.logger.info(
            f"Processed {valid_url_count} urls and got {len(all_data)} data points "
            f"in {time.time() - start} seconds thanks to multithreading!\n"
        )
        return all_data


    #insertion_method and stagger are arguments that allow paginate_endpoint to insert at around ~500 pages at a time.
    def paginate_endpoint(
        self, url, action_map={}, table=None, where_clause=True, platform='github', in_memory=True, stagger=False, insertion_method=None, insertion_threshold=500
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
                page_insertions, page_updates = self.organize_needed_data(
                    page_data, table_values, list(table.primary_key)[0].name,
                    action_map, in_memory=True
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
                all_data, table_values, list(table.primary_key)[0].name, action_map,
                in_memory=in_memory
            )

        return {
            'insert': need_insertion,
            'update': need_update,
            'all': all_data
        }

    #TODO: deprecated but still used by the issues worker.
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