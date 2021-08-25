from requests.api import head
from workers.worker_base import *
import logging
from logging import FileHandler, Formatter, StreamHandler
from workers.worker_git_integration import WorkerGitInterfaceable
from workers.util import read_config
"""
This class serves as an extension for the facade worker to allow it to make api calls and interface with GitHub.
The motivation for doing it this way is because the functionality needed to interface with Github and/or GitLab 
is contained within WorkerGitInterfaceable. This is a problem because facade was migrated into augur from its own 
project and just making it inherit from a new class could have unintended consequences and moreover, the facade worker
doesn't even really need the WorkerGitInterfaceable for too much. This is mainly just to have better parity with the contributor
worker and table. 
"""

#TODO : Make this borrow everything that it can from the facade worker.
#i.e. port, logging, etc
class ContributorInterfaceable(WorkerGitInterfaceable):
    def __init__(self, config={}):
        #first set up logging.
        
        
        self._root_augur_dir = Persistant.ROOT_AUGUR_DIR
        self.augur_config = AugurConfig(self._root_augur_dir)
        
        #Get default logging settings
        self.config = config
        self.config.update(self.augur_config.get_section("Logging"))

        #Get the same logging dir as the facade worker.
        self.config.update({
            'id': "workers.{}.{}".format("contributor_interface", self.config['port_database'])
        })

        #Getting stuck here.
        self.initialize_logging()
        #self.logger = logging.getLogger(self.config["id"])
        #Test logging after init.
        self.logger.info("Facade worker git interface logging set up correctly")
        #self.db_schema = None
        # Get config passed from the facade worker.
        db_user = self.config['user_database']
        db_pass = self.config['password_database']
        db_name = self.config['name_database']
        db_host = self.config['host_database']
        db_port = self.config['port_database']

        DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            db_user, db_pass, db_host, db_port, db_name
        )

        #Use a differant database connection 
        db = s.create_engine(DB_STR, poolclass=s.pool.NullPool,
          connect_args={'options': '-csearch_path={}'.format('augur_data')})
  
        self.db = db


        self.config = {
            'gh_api_key': self.augur_config.get_value('Database', 'key'),
            'gitlab_api_key': self.augur_config.get_value('Database', 'gitlab_api_key')
        }

        self.logger.info("Initializing API key.")
        if 'gh_api_key' in self.config or 'gitlab_api_key' in self.config:
            try:
                self.init_oauths(self.platform)
            except AttributeError:
                self.logger.error("Worker not configured to use API key!")
        else:
            self.oauths = [{'oauth_id': 0}]
        
        
        return

    def initialize_logging(self):
        #Get the log level in upper case from the augur config's logging section.
        self.config['log_level'] = self.config['log_level'].upper()
        if self.config['debug']:
            self.config['log_level'] = 'DEBUG'

        if self.config['verbose']:
            format_string = AugurLogging.verbose_format_string
        else:
            format_string = AugurLogging.simple_format_string

        #Use stock python formatter for stdout
        formatter = Formatter(fmt=format_string)
        #User custom for stderr, Gives more info than verbose_format_string
        error_formatter = Formatter(fmt=AugurLogging.error_format_string)

        worker_dir = AugurLogging.get_log_directories(self.augur_config, reset_logfiles=False) + "/workers/"
        Path(worker_dir).mkdir(exist_ok=True)
        logfile_dir = worker_dir + "/contributor_interface/"
        Path(logfile_dir).mkdir(exist_ok=True)

        #Create more complex sublogs in the logfile directory determined by the AugurLogging class
        server_logfile = logfile_dir + '{}_{}_server.log'.format(self.worker_type, self.config['port_database'])
        collection_logfile = logfile_dir + '{}_{}_collection.log'.format(self.worker_type, self.config['port_database'])
        collection_errorfile = logfile_dir + '{}_{}_collection.err'.format(self.worker_type, self.config['port_database'])
        self.config.update({
            'logfile_dir': logfile_dir,
            'server_logfile': server_logfile,
            'collection_logfile': collection_logfile,
            'collection_errorfile': collection_errorfile
        })

        collection_file_handler = FileHandler(filename=self.config['collection_logfile'], mode="a")
        collection_file_handler.setFormatter(formatter)
        collection_file_handler.setLevel(self.config['log_level'])

        collection_errorfile_handler = FileHandler(filename=self.config['collection_errorfile'], mode="a")
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
    
    #Try to construct the best url to ping GitHub's API for a username given a full name and a email.
    def resolve_user_url_from_email(self,contributor):
      try:
        cmt_cntrb = {
            'fname': contributor['commit_name'].split()[0],
            'lname': contributor['commit_name'].split()[1],
            'email': contributor['commit_email']
        }
        url = 'https://api.github.com/search/users?q={}+in:email+fullname:{}+{}'.format(
            cmt_cntrb['email'], cmt_cntrb['fname'], cmt_cntrb['lname'])
      except:
          try:
            cmt_cntrb = {
                'fname': contributor['commit_name'].split()[0],
                'email': contributor['commit_email']
            }
            url = 'https://api.github.com/search/users?q={}+in:email+fullname:{}'.format(
                cmt_cntrb['email'], cmt_cntrb['fname'])
          except:
            cmt_cntrb = {
                'email': contributor['commit_email']
            }
            url = 'https://api.github.com/search/users?q={}+in:email'.format(
                cmt_cntrb['email'])
      
      return url

    #Hit the endpoint specified by the url and return the json that it returns if it returns a dict.
    #Returns None on failure.
    def request_dict_from_endpoint(self,url,timeout_wait=10):
      self.logger.info(f"Hitting endpoint: {url}")

      attempts = 0
      response_data = None
      success = False

      #This borrow's the logic to safely hit an endpoint from paginate_endpoint.
      while attempts < 10:
        try:
          response = requests.get(url=url, headers=self.headers)
        except TimeoutError:
          self.logger.info(f"User data request for enriching contributor data failed with {attempts} attempts! Trying again...")
          time.sleep(timeout_wait)
          continue
        
        #Make sure we know how many requests our api tokens have.
        self.update_rate_limit(response,platform="github")

        try:
          response_data = response.json()
        except:
          response_data = json.loads(json.dumps(response.text))
        

        if type(response_data) == dict:
          self.logger.info(f"Returned dict: {response_data}")
          success = True
          break
        elif type(response_data) == list:
          self.logger.warning("Wrong type returned, trying again...")
          self.logger.info(f"Returned list: {response_data}")
        elif type(response_data) == str:
          self.logger.info(f"Warning! page_data was string: {response_data}")
          if "<!DOCTYPE html>" in response_data:
            self.logger.info("HTML was returned, trying again...\n")
          elif len(response_data) == 0:
            self.logger.warning("Empty string, trying again...\n")
          else:
            try:
              #Sometimes raw text can be converted to a dict
              response_data = json.loads(response_data)
              success = True
              break
            except:
              pass
        attempts += 1
      if not success:
        return None
      
      return response_data



    #Update the contributors table from the data facade has gathered.
    def insert_facade_contributors(self, repo_id):
        self.logger.info(
            "Beginning process to insert contributors from facade commits for repo w entry info: {}\n".format(repo_id))

        
        #Get all of the commit data's emails and names from the commit table that do not appear in the contributors table
        new_contrib_sql = s.sql.text("""
          SELECT distinct 
              commits.cmt_author_email AS email,
              commits.cmt_author_date AS DATE,
              commits.cmt_author_name AS NAME
          FROM
              commits
          WHERE
              commits.repo_id =:repo_id
              AND NOT EXISTS (
                  SELECT
                      contributors.cntrb_email
                  FROM
                      contributors
                  WHERE
                      contributors.cntrb_email = commits.cmt_author_email
              )
              AND (
                  commits.cmt_author_date, commits.cmt_author_name
              ) IN (
                  SELECT
                      MAX(C.cmt_author_date) AS DATE,
                      C.cmt_author_name
                  FROM
                      commits AS C
                  WHERE
                      C.repo_id =:repo_id
                      AND C.cmt_author_email = commits.cmt_author_email
                  GROUP BY
                      C.cmt_author_name,
                      C.cmt_author_date LIMIT 1
              )
          GROUP BY
              commits.cmt_author_email,
              commits.cmt_author_date,
              commits.cmt_author_name
          UNION
          SELECT
              commits.cmt_committer_email AS email,
              commits.cmt_committer_date AS DATE,
              commits.cmt_committer_name AS NAME
          FROM
              augur_data.commits
          WHERE
              commits.repo_id =:repo_id
              AND NOT EXISTS (
                  SELECT
                      contributors.cntrb_email
                  FROM
                      augur_data.contributors
                  WHERE
                      contributors.cntrb_email = commits.cmt_committer_email
              )
              AND (
                  commits.cmt_committer_date, commits.cmt_committer_name
              ) IN (
                  SELECT
                      MAX(C.cmt_committer_date) AS DATE,
                      C.cmt_committer_name
                  FROM
                      augur_data.commits AS C
                  WHERE
                      C.repo_id = :repo_id
                      AND C.cmt_committer_email = commits.cmt_committer_email
                  GROUP BY
                      C.cmt_committer_name,
                      C.cmt_author_date LIMIT 1
              )
          GROUP BY
              commits.cmt_committer_email,
              commits.cmt_committer_date,
              commits.cmt_committer_name
        """)
        new_contribs = json.loads(pd.read_sql(new_contrib_sql, self.db, params={
                                  'repo_id': repo_id}).to_json(orient="records"))

        #Try to get GitHub API user data from each unique commit email.
        for contributor in new_contribs:
            #Get best combonation of firstname lastname and email to try and get a GitHub username match.
            url = self.resolve_user_url_from_email(contributor)

            login_json = self.request_dict_from_endpoint(url,timeout_wait=30)

            #total_count is the count of username's found by the endpoint.
            if login_json == None or 'total_count' not in login_json:
                self.logger.info(
                    "Search query returned an empty response, moving on...\n")
                continue
            if login_json['total_count'] == 0:
                self.logger.info(
                    "Search query did not return any results, adding 1's to commits table...\n")

                #At this point we know we can't do anything with the email so we make the cntrb_id foreign key 1
                self.db.execute(self.commits_table.update().where(
                  self.commits_table.c.cmt_committer_email==contributor['commit_email']
                ).values({
                  'cmt_ght_author_id' : 1
                }))
                continue

            self.logger.info("When searching for a contributor with info {}, we found the following users: {}\n".format(
                contributor, login_json))

            # Grab first result and make sure it has the highest match score
            match = login_json['items'][0]
            for item in login_json['items']:
                if item['score'] > match['score']:
                    match = item

            url = ("https://api.github.com/users/" + match['login'])

            user_data = self.request_dict_from_endpoint(url)

            if user_data == None:
              self.logger.warning(f"user_data was unable to be reached. Skipping...")
              continue

            # try to add contributor to database
            cntrb = {
              "cntrb_login": user_data['login'],
              "cntrb_created_at": user_data['created_at'],
              "cntrb_email": user_data['email'] if 'email' in user_data else None,
              "cntrb_company": user_data['company'] if 'company' in user_data else None,
              "cntrb_location": user_data['location'] if 'location' in user_data else None,
              # "cntrb_type": , dont have a use for this as of now ... let it default to null
              "cntrb_canonical": user_data['email'] if 'email' in user_data else None,
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
              "cntrb_last_used" : None if 'updated_at' not in user_data else user_data['updated_at'],
              "cntrb_full_name" : None if 'name' not in user_data else user_data['name'],
              "tool_source": self.tool_source,
              "tool_version": self.tool_version,
              "data_source": self.data_source
            }
            # expcpetion: log that the user was already THERE

            try:
              self.db.execute(self.contributors_table.insert().values(cntrb))
            except Exception as e:
              self.logger.info("Ran into likely database collision. Assuming contributor exists in database. Error: {e}")
        

        # sql query used to find corresponding cntrb_id's of emails found in the contributor's table
        resolve_email_to_cntrb_id_sql = s.sql.text("""
          select distinct cntrb_id, contributors.cntrb_email, commits.cmt_author_raw_email
          from 
              contributors, commits
          where 
              contributors.cntrb_email = commits.cmt_author_raw_email
              AND commits.repo_id =:repo_id
          union 
          select distinct cntrb_id, contributors.cntrb_email, commits.cmt_committer_raw_email
          from 
              contributors, commits
          where 
              contributors.cntrb_email = commits.cmt_committer_raw_email
              AND commits.repo_id =:repo_id
        """)

        #sql query to get emails from current repo that already exist in the contributor's table.
        
        #existing_contrib_sql = s.sql.text("""
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
        #""")
        
        #Get a list of dicts that contain the emails and cntrb_id's of commits that appear in the contributor's table.
        existing_cntrb_emails = json.loads(pd.read_sql(resolve_email_to_cntrb_id_sql, self.db, params={
                                           'repo_id': repo_id}).to_json(orient="records"))

        #iterate through all the commits with emails that appear in contributors and give them the relevant cntrb_id.
        for cntrb_email in existing_cntrb_emails:
            self.logger.info(f"These are the emails and cntrb_id's  returned: {cntrb_email}")
            self.db.execute(self.commits_table.update().where(
              self.commits_table.c.cmt_committer_email==cntrb_email['cntrb_email']
            ).values({
              'cmt_ght_author_id' : cntrb_email['cntrb_id']
            }))
        return
        # old method
        """
    commit_cntrbs = json.loads(pd.read_sql(userSQL, self.db, params={'repo_id': repo_id}).to_json(orient="records"))
    self.logger.info("We found {} distinct contributors needing insertion (repo_id = {})".format(
      len(commit_cntrbs), repo_id))
    for cntrb in commit_cntrbs:
        cntrb_tuple = {
                "cntrb_email": cntrb['email'],
                "cntrb_canonical": cntrb['email'],
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source,
                'cntrb_full_name': cntrb['name']
            }
        result = self.db.execute(self.contributors_table.insert().values(cntrb_tuple))
        self.logger.info("Primary key inserted into the contributors table: {}".format(result.inserted_primary_key))
        self.results_counter += 1
        self.logger.info("Inserted contributor: {}\n".format(cntrb['email']))
    """
