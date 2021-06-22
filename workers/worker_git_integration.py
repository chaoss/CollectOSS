#WORK IN PROGRESS NOT TO BE USED AT ALL IN PRESENT STATE

#Get everything that the base depends on.
from workers.worker_base import *


#This is a worker base subclass that adds the ability to query github/gitlab with the api key
class WorkerGitInterfaceable(Worker):
    def __init__(self, worker_type, config={}, given=[], models=[], data_tables=[], operations_tables=[], platform="github"):
        super().___init__(worker_type, config, given, models, data_tables, operations_tables)

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

        try:
            self.tool_source
            self.tool_version
            self.data_source
        except:
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


        while True:
            try:
                r = requests.get(url=cntrb_url, headers=self.headers)
                break
            except TimeoutError as e:
                self.logger.info("Request timed out. Sleeping 10 seconds and trying again...\n")
                time.sleep(30)

        self.update_rate_limit(r)
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
            return data

        self.logger.info(f"Enriching contributor ids for {len(data)} data points...")

        source_df = pd.DataFrame(data)
        expanded_source_df = self._add_nested_columns(
            source_df.copy(), [key] + action_map_additions['insert']['source']
        )

        # Insert cntrbs that are not in db

        cntrb_action_map = {
            'insert': {
                'source': [key] + action_map_additions['insert']['source'],
                'augur': ['cntrb_login'] + action_map_additions['insert']['augur']
            }
        }
        source_cntrb_insert, _ = self.new_organize_needed_data(
            expanded_source_df.to_dict(orient='records'), augur_table=self.contributors_table,
            action_map=cntrb_action_map
        )

        cntrb_insert = [
            {
                'cntrb_login': contributor[f'{prefix}login'],
                'cntrb_created_at': None if (
                    f'{prefix}created_at' not in contributor
                ) else contributor[f'{prefix}created_at'],
                'cntrb_email': None if f'{prefix}email' not in contributor else contributor[f'{prefix}email'],
                'cntrb_company': None if f'{prefix}company' not in contributor else contributor[f'{prefix}company'],
                'cntrb_location': None if (
                    f'{prefix}location' not in contributor
                ) else contributor[f'{prefix}location'],
                'gh_user_id': None if (
                    not contributor[f'{prefix}id']
                ) else int(float(contributor[f'{prefix}id'])),
                'gh_login': contributor[f'{prefix}login'],
                'gh_url': contributor[f'{prefix}url'],
                'gh_html_url': contributor[f'{prefix}html_url'],
                'gh_node_id': contributor[f'{prefix}node_id'],
                'gh_avatar_url': contributor[f'{prefix}avatar_url'],
                'gh_gravatar_id': contributor[f'{prefix}gravatar_id'],
                'gh_followers_url': contributor[f'{prefix}followers_url'],
                'gh_following_url': contributor[f'{prefix}following_url'],
                'gh_gists_url': contributor[f'{prefix}gists_url'],
                'gh_starred_url': contributor[f'{prefix}starred_url'],
                'gh_subscriptions_url': contributor[f'{prefix}subscriptions_url'],
                'gh_organizations_url': contributor[f'{prefix}organizations_url'],
                'gh_repos_url': contributor[f'{prefix}repos_url'],
                'gh_events_url': contributor[f'{prefix}events_url'],
                'gh_received_events_url': contributor[f'{prefix}received_events_url'],
                'gh_type': contributor[f'{prefix}type'],
                'gh_site_admin': contributor[f'{prefix}site_admin'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            } for contributor in source_cntrb_insert if contributor[f'{prefix}login']
        ]

        self.bulk_insert(self.contributors_table, cntrb_insert)

        # Query db for inserted cntrb pkeys and add to shallow level of data

        # Query
        cntrb_pk_name = list(self.contributors_table.primary_key)[0].name
        session = s.orm.Session(self.db)
        inserted_pks = pd.DataFrame(
            session.query(
                self.contributors_table.c[cntrb_pk_name], self.contributors_table.c.cntrb_login,
                self.contributors_table.c.gh_node_id
            ).distinct(self.contributors_table.c.cntrb_login).order_by(
                self.contributors_table.c.cntrb_login, self.contributors_table.c[cntrb_pk_name]
            ).all(), columns=[cntrb_pk_name, 'cntrb_login', 'gh_node_id']
        ).to_dict(orient='records')
        session.close()

        # Prepare for merge
        source_columns = sorted(list(source_df.columns))
        necessary_columns = sorted(list(set(source_columns + cntrb_action_map['insert']['source'])))
        (source_table, inserted_pks_table), metadata, session = self._setup_postgres_merge(
            [
                expanded_source_df[necessary_columns].to_dict(orient='records'),
                inserted_pks
            ], sort=True
        )
        final_columns = [cntrb_pk_name] + sorted(list(set(necessary_columns)))

        # Merge
        source_pk = pd.DataFrame(
            session.query(
                inserted_pks_table.c.cntrb_id, source_table
            ).join(
                source_table,
                eval(
                    ' and '.join(
                        [
                            (
                                f"inserted_pks_table.c['{table_column}'] "
                                f"== source_table.c['{source_column}']"
                            ) for table_column, source_column in zip(
                                cntrb_action_map['insert']['augur'],
                                cntrb_action_map['insert']['source']
                            )
                        ]
                    )
                )
            ).all(), columns=final_columns
        )

        # Cleanup merge
        source_pk = self._eval_json_columns(source_pk)
        self._close_postgres_merge(metadata, session)

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
