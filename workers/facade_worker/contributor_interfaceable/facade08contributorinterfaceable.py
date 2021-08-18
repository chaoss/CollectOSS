from requests.api import head
from workers.worker_base import *

from workers.worker_git_integration import WorkerGitInterfaceable

#TODO : Make this borrow everything that it can from the facade worker.
#i.e. port, logging, etc
class ContributorInterfaceable(WorkerGitInterfaceable):
    def __init__(self, config={}):
        self.db_schema = None
        # Get configured collection logger
        self.config.update(config)

        self.data_tables = ['contributors', 'contributors_aliases', 'contributor_affiliations',
                            'issue_events', 'pull_request_events', 'issues', 'message', 'issue_assignees',
                            'pull_request_assignees', 'pull_request_reviewers', 'pull_request_meta', 'pull_request_repo']

        self._root_augur_dir = Persistant.ROOT_AUGUR_DIR

        self.config = {
            'worker_type': "contributor_interface",
            'host': self.augur_config.get_value('Server', 'host'),
            'gh_api_key': self.augur_config.get_value('Database', 'key'),
            'gitlab_api_key': self.augur_config.get_value('Database', 'gitlab_api_key')
        }

        worker_port = self.config['port']
        while True:
            try:
                r = requests.get('http://{}:{}/AUGWOP/heartbeat'.format(
                    self.config['host'], worker_port)).json()
                if 'status' in r:
                    if r['status'] == 'alive':
                        worker_port += 1
            except:
                break

        # add credentials to db config. Goes to databaseable
        self.config.update({
            'port': worker_port,
            'id': "workers.{}.{}".format("contributor_interface", worker_port),
            'capture_output': False,
            'location': 'http://{}:{}'.format(self.config['host'], worker_port),
            'port_broker': self.augur_config.get_value('Server', 'port'),
            'host_broker': self.augur_config.get_value('Server', 'host'),
            'host_database': self.augur_config.get_value('Database', 'host'),
            'port_database': self.augur_config.get_value('Database', 'port'),
            'user_database': self.augur_config.get_value('Database', 'user'),
            'name_database': self.augur_config.get_value('Database', 'name'),
            'password_database': self.augur_config.get_value('Database', 'password')
        })

        self.initialize_logging()

        # Clear log contents from previous runs
        open(self.config["server_logfile"], "w").close()
        open(self.config["collection_logfile"], "w").close()

        self.logger = logging.getLogger(self.config["id"])

        self.initialize_database_connections()
        self.init_oauths()
        self.logger.info(
            'Worker (PID: {}) initializing...'.format(str(os.getpid())))

        self.tool_source = "contributor_interface"
        self.tool_version = "0.1"
        self.data_source = "contributor_interface"

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

    def request_dict_from_endpoint(self,url):
      self.logger.info(f"Hitting endpoint: {url}")

      attempts = 0
      response_data = None
      success = False

      while attempts < 10:
        try:
          response = requests.get(url=url, headers=self.headers)
        except TimeoutError:
          self.logger.info(f"User data request for enriching contributor data failed with {attempts} attempts! Trying again...")
          time.sleep(10)
          continue

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
              response_data = json.loads(response_data)
              success = True
              break
            except:
              pass
        attempts += 1
      if not success:
        return None
      
      return response_data



      
    def insert_facade_contributors(self, entry_info, repo_id):
        self.logger.info(
            "Beginning process to insert contributors from facade commits for repo w entry info: {}\n".format(entry_info))

        # sql query used 
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

        existing_contrib_sql = s.sql.text("""
          select distinct contributors.cntrb_email, commits.cmt_author_raw_email
          from 
              contributors, commits
          where 
              contributors.cntrb_email = commits.cmt_author_raw_email
              AND commits.repo_id =:repo_id
          union 
          select distinct contributors.cntrb_email, commits.cmt_committer_raw_email
          from 
              contributors, commits
          where 
              contributors.cntrb_email = commits.cmt_committer_raw_email
              AND commits.repo_id =:repo_id
        """)

        existing_cntrb_emails = json.loads(pd.read_sql(existing_contrib_sql, self.db, params={
                                           'repo_id': repo_id}).to_json(orient="records"))

        for cntrb_email in existing_cntrb_emails:
            pass
            # query database with 'cntrb_email' and get the 'cntb_id'
            # find all commits in commits table with 'cntrb_email'
            # update 'cntrb_id' to each commit

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

        for contributor in new_contribs:
            url = self.resolve_user_url_from_email(contributor)

            login_json = self.request_dict_from_endpoint(url)

            if 'total_count' not in login_json:
                self.logger.info(
                    "Search query returned an empty response, moving on...\n")
                continue
            if login_json['total_count'] == 0:
                self.logger.info(
                    "Search query did not return any results, adding 1's to commits table...\n")
                # find all commits in commits table with 'cntrb_email'
                # update 'cntrb_id' to each commit
                continue

            self.logger.info("When searching for a contributor with info {}, we found the following users: {}\n".format(
                contributor, login_json))

            # Grab first result and make sure it has the highest match score
            match = login_json['items'][0]
            for item in login_json['items']:
                if item['score'] > match['score']:
                    match = item

            url = ("https://api.github.com/users/" + match['login'])

            
            # try to add contributor to database
            # expcpetion: log that the user was already THERE

            # get the cntrb_id based on the logging
            # find all commits in commits table with 'cntrb_email'
            # update 'cntrb_id' to each commit

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
