from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
import datetime
import time
import logging
import json
import ast
logging.basicConfig(filename='worker.log', level=logging.INFO)

class CollectorTask:
    """ Worker's perception of a task in its queue
    Holds a message type (EXIT, TASK, etc) so the worker knows how to process the queue entry
    and the github_url given that it will be collecting data for
    """
    def __init__(self, message_type='TASK', entry_info=None):
        self.type = message_type
        self.entry_info = entry_info

def dump_queue(queue):
    """
    Empties all pending items in a queue and returns them in a list.
    """
    result = []
    queue.put("STOP")
    for i in iter(queue.get, 'STOP'):
        result.append(i)
    # time.sleep(.1)
    return result



class GitHubWorker:
    """ Worker that collects data from the Github API and stores it in our database
    task: most recent task the broker added to the worker's queue
    child: current process of the queue being ran
    queue: queue of tasks to be fulfilled
    config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config, task=None):
        logging.info('Worker initializing...')
        self._task = task
        self._child = None
        self._queue = Queue()
        self.config = config
        self.db = None
        self.table = None
        self.API_KEY = self.config['key']
        self.tool_source = 'GitHub API Worker'
        self.tool_version = '0.0.1' # See __init__.py
        self.data_source = 'GitHub API'
        self.results_counter = 0
        self.headers = {'Authorization': 'token %s' % self.config['key']}

        url = "https://api.github.com/users/gabe-heim"
        response = requests.get(url=url, headers=self.headers)
        self.rate_limit = int(response.headers['X-RateLimit-Remaining'])

        
        specs = {
            "id": self.config['id'],
            "location": "http://localhost:51236",
            "qualifications":  [
                {
                    "given": [["git_url"]],
                    "models":["issues"]
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['database']
        )

        #Database connections
        dbschema = 'augur_data'
        self.db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        metadata = MetaData()
        helper_metadata = MetaData()

        metadata.reflect(self.db, only=['contributors', 'issues', 'issue_labels', 'message',
            'issue_message_ref', 'issue_events',
            'issue_assignees'])
        helper_metadata.reflect(self.helper_db, only=['gh_worker_history', 'gh_worker_job'])

        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)

        Base.prepare()
        HelperBase.prepare()

        self.contributors_table = Base.classes.contributors.__table__
        self.issues_table = Base.classes.issues.__table__
        self.issue_labels_table = Base.classes.issue_labels.__table__
        self.issue_events_table = Base.classes.issue_events.__table__
        self.message_table = Base.classes.message.__table__
        self.issues_message_ref_table = Base.classes.issue_message_ref.__table__
        self.issue_assignees_table = Base.classes.issue_assignees.__table__

        self.history_table = HelperBase.classes.gh_worker_history.__table__
        self.job_table = HelperBase.classes.gh_worker_job.__table__


        # Query all repos and last repo id
        repoUrlSQL = s.sql.text("""
            SELECT repo_git, repo_id FROM repo ORDER BY repo_id ASC
            """)

        rs = pd.read_sql(repoUrlSQL, self.db, params={})

        repoIdSQL = s.sql.text("""
            SELECT since_id_str FROM gh_worker_job
            """)

        df = pd.read_sql(repoIdSQL, self.helper_db, params={})
        last_id = int(df.iloc[0]['since_id_str'])
        before_repos = rs.loc[rs['repo_id'].astype(int) <= last_id]
        after_repos = rs.loc[rs['repo_id'].astype(int) > last_id]

        reorganized_repos = after_repos.append(before_repos)
        # logging.info("BEFORE: " + str(before_repos) + " AFTER: " + str(after_repos))
        # logging.info("FIRST REPO TO WORK ON: " + str(reorganized_repos))

        # Reorganize so that the repo after the last repo we completed is first


        # Populate queue
        for index, row in reorganized_repos.iterrows():
            self._queue.put(CollectorTask(message_type='TASK', entry_info=row))



        # Get max ids so we know where we are in our insertion and to have the current id when inserting FK's
        maxIssueCntrbSQL = s.sql.text("""
            SELECT max(issues.issue_id) AS issue_id, max(contributors.cntrb_id) AS cntrb_id
            FROM issues, contributors
        """)
        rs = pd.read_sql(maxIssueCntrbSQL, self.db, params={})

        issue_start = rs.iloc[0]["issue_id"]
        cntrb_start = rs.iloc[0]["cntrb_id"]

        maxMsgSQL = s.sql.text("""
            SELECT max(msg_id) AS msg_id
            FROM message
        """)
        rs = pd.read_sql(maxMsgSQL, self.db, params={})

        msg_start = rs.iloc[0]["msg_id"]

        if issue_start is None:
            issue_start = 25150
        else:
            issue_start = issue_start.item()
        if cntrb_start is None:
            cntrb_start = 25150
        else:
            cntrb_start = cntrb_start.item()
        if msg_start is None:
            msg_start = 25150
        else:
            msg_start = msg_start.item()

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.issue_id_inc = (issue_start + 1)
        self.cntrb_id_inc = (cntrb_start + 1)
        self.msg_id_inc = (msg_start + 1)

        self.run()

        requests.post('http://localhost:5000/api/unstable/workers', json=specs, headers=self.headers) #hello message

    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            'database_connection_string': 'psql://localhost:5433/augur',
            "display_name": "",
            "description": "",
            "required": 1,
            "type": "string"
        }
        self.config.update(config)
        self.API_KEY = self.config['key']

    @property
    def task(self):
        """ Property that is returned when the worker's current task is referenced
        """
        return self._task
    
    @task.setter
    def task(self, value):
        """ entry point for the broker to add a task to the queue
        Adds this task to the queue, and calls method to process queue
        """
        git_url = value['given']['git_url']

        """ Query all repos """
        repoUrlSQL = s.sql.text("""
            SELECT repo_id FROM repo WHERE repo_git = '{}'
            """.format(git_url))
        rs = pd.read_sql(repoUrlSQL, self.db, params={})

        try:
            self._queue.put(CollectorTask(message_type='TASK', entry_info={"git_url": git_url, "repo_id": rs}))
        
        # list_queue = dump_queue(self._queue)
        # logging.info("worker's queue after adding the job: " + list_queue)

        except:
            logging.info("that repo is not in our database")
        
        self._task = value
        self.run()

    def cancel(self):
        """ Delete/cancel current task
        """
        self._task = None

    def run(self):
        """ Kicks off the processing of the queue if it is not already being processed
        Gets run whenever a new task is added
        """
        logging.info("Running...")
        # if not self._child:
        self._child = Process(target=self.collect, args=())
        self._child.start()

    def collect(self):
        """ Function to process each entry in the worker's task queue
        Determines what action to take based off the message type
        """
        while True:
            if not self._queue.empty():
                message = self._queue.get()
            else:
                break

            if message.type == 'EXIT':
                break

            if message.type != 'TASK':
                raise ValueError(f'{message.type} is not a recognized task type')

            if message.type == 'TASK':
                self.query_issues(message.entry_info)

    def query_contributors(self, entry_info):

        """ Data collection function
        Query the GitHub API for contributors
        """
        logging.info("Querying contributors with given entry info: " + str(entry_info) + "\n")

        # Url of repo we are querying for
        url = entry_info['repo_git']

        # Extract owner/repo from the url for the endpoint
        path = urlparse(url)
        split = path[2].split('/')

        owner = split[1]
        name = split[2]

        # Handles git url case by removing the extension
        if ".git" in name:
            name = name[:-4]

        url = ("https://api.github.com/repos/" + owner + "/" + name + "/contributors?page={}")
        contributors = []
        i = 0
        # Paginate through all the contributors
        while True:
            logging.info("Hitting endpoint: " + url.format(i) + " ...\n")
            r = requests.get(url=url.format(i), headers=self.headers)
            self.update_rate_limit(r)
            try:
                j = r.json()
            except Exception as e:
                logging.info("Caught exception: " + str(e) + "....\n")
                logging.info("Some kind of issue CHECKTHIS  " + url + " ...\n")
            else:
                logging.info("JSON seems ill-formed " + str(r) + "....\n")

            if r.status_code != 204:
                contributors = r.json()
            if len(j) == 0:
                break
            contributors += j
            i += 1
        
        
        
        try:
            # Duplicate checking ...
            need_insertion = self.filter_duplicates({'cntrb_login': "login"}, ['contributors'], contributors)
            logging.info("Count of contributors needing insertion: " + str(len(need_insertion)) + "\n")

            for repo_contributor in need_insertion:

                # Need to hit this single contributor endpoint to get extra data including...
                #   created at
                #   i think that's it
                cntrb_url = ("https://api.github.com/users/" + repo_contributor['login'])
                logging.info("Hitting endpoint: " + cntrb_url + " ...\n")
                r = requests.get(url=cntrb_url, headers=self.headers)
                self.update_rate_limit(r)
                contributor = r.json()


                # NEED TO FIGURE OUT IF THIS STUFF IS EVER AVAILABLE
                #    if so, the null case will need to be handled

                # "company": contributor['company'],
                # "location": contributor['location'],
                # "email": contributor['email'],

                # aliasSQL = s.sql.text("""
                #     SELECT canonical_email
                #     FROM contributors_aliases
                #     WHERE alias_email = {}
                # """.format(contributor['email']))
                # rs = pd.read_sql(aliasSQL, self.db, params={})

                canonical_email = None#rs.iloc[0]["canonical_email"]



                cntrb = {
                    "cntrb_login": contributor['login'],
                    "cntrb_created_at": contributor['created_at'],
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
                result = self.db.execute(self.contributors_table.insert().values(cntrb))
                logging.info("PKEY: " + str(result.inserted_primary_key))
                self.results_counter += 1
    
                logging.info("Inserted contributor: " + contributor['login'] + "\n")

            # Increment our global track of the cntrb id for the possibility of it being used as a FK
                self.cntrb_id_inc += 1

        except Exception as e:
            logging.info("Caught exception: " + str(e))
            logging.info("Contributor not defined. Please contact the manufacturers of Soylent Green " + url + " ...\n")
            logging.info("Cascading Contributor Anomalie from missing repo contributor data: " + url + " ...\n")
        else:
            logging.info("Well, that contributor just don't except because we hit the else-block yo")    


    def query_issues(self, entry_info):

        """ Data collection function
        Query the GitHub API for issues
        """
        logging.info("Beginning filling the issues model for repo: " + entry_info['repo_git'] + "\n")
        self.record_model_process('issues')

        # Contributors are part of this model, and finding all for the repo saves us 
        #   from having to add them as we discover committers in the issue process
        self.query_contributors(entry_info)

        url = entry_info['repo_git']

        # Extract the owner/repo for the endpoint
        path = urlparse(url)
        split = path[2].split('/')

        owner = split[1]
        name = split[2]

        # Handle git url case by removing extension
        if ".git" in name:
            name = name[:-4]

        url = ("https://api.github.com/repos/" + owner + "/" + name + "/issues?page={}&?state=all")
        issues = []
        i = 0
        # Paginate through all the issues
        while True:
            logging.info("Hitting endpoint: " + url.format(i) + " ...\n")
            r = requests.get(url=url.format(i), headers=self.headers)
            self.update_rate_limit(r)
            j = r.json()
            if len(j) == 0:
                break
            issues += j
            i += 1

        # Discover and remove duplicates before we start inserting
        need_insertion = self.filter_duplicates({'gh_issue_id': 'id'}, ['issues'], issues)
        logging.info("Count of issues needing insertion: " + str(len(need_insertion)) + "\n")

        for issue_dict in need_insertion:

            logging.info("Begin analyzing the issue with title: " + issue_dict['title'] + "\n")
            # Add the FK repo_id to the dict being inserted
            issue_dict['repo_id'] = entry_info['repo_id']

            # Figure out if this issue is a PR
            #   still unsure about this key value pair/what it means
            pr_id = None
            if "pull_request" in issue_dict:
                logging.info("it is a PR\n")
                # Right now we are just storing our issue id as the PR id if it is one
                pr_id = self.issue_id_inc
            else:
                logging.info("it is not a PR\n")

            # Begin on the actual issue...

            # Base of the url for comment and event endpoints
            url = ("https://api.github.com/repos/" + owner + "/" + name + "/issues/" + str(issue_dict['number']))

            # Get events ready in case the issue is closed and we need to insert the closer's id
            events_url = (url + "/events?page={}")
            issue_events = []
            i = 0
            # Paginate through all the issues
            while True:
                logging.info("Hitting endpoint: " + events_url.format(i) + " ...\n")
                r = requests.get(url=events_url.format(i), headers=self.headers)
                self.update_rate_limit(r)
                j = r.json()
                if len(j) == 0:
                    break
                issue_events += j
                i += 1
            
            # If the issue is closed, then we search for the closing event and store the user's id
            cntrb_id = None
            if 'closed_at' in issue_dict:
                for event in issue_events:
                    if event['event'] == 'closed':
                        logging.info('event-issue '  ' event seems missing somethinga '  + "..... \n") 
                        cntrb_id = self.find_id_from_login(event['actor']['login'])
            
            issue = {
                "repo_id": issue_dict['repo_id'],
                "reporter_id": self.find_id_from_login(issue_dict['user']['login']),
                "pull_request": pr_id,
                "pull_request_id": pr_id,
                "created_at": issue_dict['created_at'],
                "issue_title": issue_dict['title'],
                "issue_body": issue_dict['body'],
                "cntrb_id": cntrb_id,
                "comment_count": issue_dict['comments'],
                "updated_at": issue_dict['updated_at'],
                "closed_at": issue_dict['closed_at'],
                "repository_url": issue_dict['repository_url'],
                "issue_url": issue_dict['url'],
                "labels_url": issue_dict['labels_url'],
                "comments_url": issue_dict['comments_url'],
                "events_url": issue_dict['events_url'],
                "html_url": issue_dict['html_url'],
                "issue_state": issue_dict['state'],
                "issue_node_id": issue_dict['node_id'],
                "gh_issue_id": issue_dict['id'],
                "gh_issue_number": issue_dict['number'],
                "gh_user_id": issue_dict['user']['id'],
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source
            }

            # Commit insertion to the issues table
            result = self.db.execute(self.issues_table.insert().values(issue))
            logging.info("PKEY: " + str(result.inserted_primary_key))
            self.results_counter += 1

            logging.info("Inserted issue with our issue_id being: " + str(self.issue_id_inc) + 
                " and title of: " + issue_dict['title'] + " and gh_issue_num of: " + str(issue_dict['number']) + "\n")

            self.issue_id_inc = int(result.inserted_primary_key[0])

            # Just to help me figure out cases where a..nee vs a..nees shows up
            if "assignee" in issue_dict and "assignees" in issue_dict:
                logging.info("assignee and assignees here\n")
            elif "assignees" in issue_dict:
                logging.info("multiple assignees and no single one\n")
            elif "assignee" in issue_dict:
                logging.info("single assignees and no multiples\n")

            # Check if the assignee key's value is already recorded in the assignees key's value
            #   Create a collective list of unique assignees
            collected_assignees = issue_dict['assignees']
            if issue_dict['assignee'] not in collected_assignees:
                collected_assignees.append(issue_dict['assignee'])
            logging.info("Count of assignees for this issue: " + str(len(collected_assignees)) + "\n")

            # Handles case if there are no assignees
            if collected_assignees[0] is not None:
                for assignee_dict in collected_assignees:

                    assignee = {
                        "issue_id": self.issue_id_inc,
                        "cntrb_id": self.find_id_from_login(assignee_dict['login']),
                        "tool_source": self.tool_source,
                        "tool_version": self.tool_version,
                        "data_source": self.data_source
                    }
                    # Commit insertion to the assignee table
                    result = self.db.execute(self.issue_assignees_table.insert().values(assignee))
                    logging.info("PKEY: " + str(result.inserted_primary_key))
                    self.results_counter += 1

                    logging.info("Inserted assignee for issue id: " + str(self.issue_id_inc) + 
                        " with login/cntrb_id: " + assignee_dict['login'] + " " + str(assignee['cntrb_id']) + "\n")


            

            # Insert the issue labels to the issue_labels table
            for label_dict in issue_dict['labels']:
                logging.info(str(label_dict))
                desc = None
                if 'description' in label_dict:
                    desc = label_dict['description']
                label = {
                    "issue_id": self.issue_id_inc,
                    "label_text": label_dict["name"],
                    "label_description": desc,
                    "label_color": label_dict['color'],
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                result = self.db.execute(self.issue_labels_table.insert().values(label))
                logging.info("PKEY: " + str(result.inserted_primary_key))
                self.results_counter += 1

                logging.info("Inserted issue label with text: " + label_dict['name'] + "\n")


            #### Messages/comments and events insertion (we collected events above but never inserted them)

            comments_url = (url + "/comments?page={}")
            issue_comments = []
            i = 0
            # Paginate through all the issue comments
            while True:
                logging.info("Hitting endpoint: " + comments_url.format(i) + " ...\n")
                r = requests.get(url=comments_url.format(i), headers=self.headers)
                self.update_rate_limit(r)
                j = r.json()
                if len(j) == 0:
                    break
                issue_comments += j
                i += 1

            # Add the FK of our cntrb_id to each comment dict to be inserted
            logging.info("length of commit comments " + str(len(issue_comments)))
            if len(issue_comments) != 0:
                for comment in issue_comments:
                    comment['cntrb_id'] = self.find_id_from_login(comment['user']['login'])

            # Filter duplicates before insertion
            comments_need_insertion = self.filter_duplicates({'msg_timestamp': 'created_at', 'cntrb_id': 'cntrb_id'}, ['message'], issue_comments)
    
            logging.info("Number of comments needing insertion: " + str(len(comments_need_insertion)))

            


            logging.info(str(comments_need_insertion))
            for comment in comments_need_insertion:
                issue_comment = {
                    "pltfrm_id": 25150,
                    "msg_text": comment['body'],
                    "msg_timestamp": comment['created_at'],
                    "cntrb_id": self.find_id_from_login(comment['user']['login']),
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                result = self.db.execute(self.message_table.insert().values(issue_comment))
                logging.info("PKEY: " + str(result.inserted_primary_key))
                self.results_counter += 1

                logging.info("Inserted issue comment: " + comment['body'] + "\n")

                ### ISSUE MESSAGE REF TABLE ###

                issue_message_ref = {
                    "issue_id": self.issue_id_inc,
                    "msg_id": self.msg_id_inc,
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                result = self.db.execute(self.issues_message_ref_table.insert().values(issue_message_ref))
                logging.info("PKEY: " + str(result.inserted_primary_key))
                self.results_counter += 1

                logging.info("Inserted issue comment with msg_id of: " + str(self.msg_id_inc) + "\n")

                self.msg_id_inc += 1


            for event in issue_events:
                if event['actor'] is not None:
                    event['cntrb_id'] = self.find_id_from_login(event['actor']['login'])
                    if event['cntrb_id'] is None:
                        logging.info("SOMETHING WRONG WITH FINDING ID FROM LOGIN")
                        event['cntrb_id'] = 1
                else:
                    event['cntrb_id'] = 1

            events_need_insertion = self.filter_duplicates({'node_id': 'node_id'}, ['issue_events'], issue_events)
        
            logging.info("Number of events needing insertion: " + str(len(events_need_insertion)))

            for event in issue_events:
                issue_event = {
                    "issue_id": self.issue_id_inc,
                    "node_id": event['node_id'],
                    "node_url": event['url'],
                    "cntrb_id": event['cntrb_id'],
                    "created_at": event['created_at'],
                    "action": event["event"],
                    "action_commit_hash": event["commit_id"],
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                result = self.db.execute(self.issue_events_table.insert().values(issue_event))
                logging.info("PKEY: " + str(result.inserted_primary_key))
                self.results_counter += 1

                logging.info("Inserted issue event: " + event['event'] + " " + str(self.issue_id_inc) + "\n")
            


            self.issue_id_inc += 1

        #Register this task as completed
        self.register_task_completion(entry_info, "issues")
            
            
    def filter_duplicates(self, cols, tables, og_data):
        need_insertion = []

        table_str = tables[0]
        del tables[0]
        for table in tables:
            table_str += ", " + table
        for col in cols.keys():
            colSQL = s.sql.text("""
                SELECT {} FROM {}
                """.format(col, table_str))
            values = pd.read_sql(colSQL, self.db, params={})

            for obj in og_data:
                if values.isin([obj[cols[col]]]).any().any():
                    logging.info("value of tuple exists: " + str(obj[cols[col]]) + "\n")
                elif obj not in need_insertion:
                    need_insertion.append(obj)
        logging.info("While filtering duplicates, we reduced the data size from " + str(len(og_data)) + 
            " to " + str(len(need_insertion)) + "\n")
        return need_insertion

    def find_id_from_login(self, login):
        idSQL = s.sql.text("""
            SELECT cntrb_id FROM contributors WHERE cntrb_login = '{}'
            """.format(login))
        rs = pd.read_sql(idSQL, self.db, params={})
        data_list = [list(row) for row in rs.itertuples(index=False)] 
        try:
            return data_list[0][0]
        except:
            logging.info("contributor needs to be added...")
            cntrb_url = ("https://api.github.com/users/" + login)

            r = requests.get(url=cntrb_url, headers=self.headers)
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

            # aliasSQL = s.sql.text("""
            #     SELECT canonical_email
            #     FROM contributors_aliases
            #     WHERE alias_email = {}
            # """.format(contributor['email']))
            # rs = pd.read_sql(aliasSQL, self.db, params={})

            canonical_email = None#rs.iloc[0]["canonical_email"]

            cntrb = {
                "cntrb_login": contributor['login'],
                "cntrb_email": email,
                "cntrb_company": company,
                "cntrb_location": location,
                "cntrb_created_at": contributor['created_at'],                
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
            result = self.db.execute(self.contributors_table.insert().values(cntrb))
            logging.info("PKEY: " + str(result.inserted_primary_key))
            self.results_counter += 1

            logging.info("Inserted contributor: " + contributor['login'] + "\n")
            self.cntrb_id_inc += 1
            self.find_id_from_login(login)
            pass

    def update_rate_limit(self, response):
        # self.rate_limit -= 1
        # logging.info("OUR TRACK OF LIMIT: " + str(self.rate_limit) + " ACTUAL: " + str(response.headers['X-RateLimit-Remaining']))
        self.rate_limit = int(response.headers['X-RateLimit-Remaining'])
        logging.info("Updated rate limit, you have: " + str(self.rate_limit) + " requests remaining.\n")
        if self.rate_limit <= 0:

            # url = "https://api.github.com/users/gabe-heim"
            # response = requests.get(url=url, headers=self.headers)
            reset_time = response.headers['X-RateLimit-Reset']
            time_diff = datetime.datetime.fromtimestamp(int(reset_time)) - datetime.datetime.now()
            logging.info("Rate limit exceeded, waiting " + str(time_diff.total_seconds()) + " seconds.\n")
            time.sleep(time_diff.total_seconds())
            self.rate_limit = int(response.headers['X-RateLimit-Limit'])
        
    def register_task_completion(self, entry_info, model):

        #add to history table
        task_completed = entry_info.to_dict()
        task_completed['worker_id'] = self.config['id']

        task_history = {
            "repo_id": entry_info['repo_id'],
            "worker": self.config['id'],
            "job_model": entry_info['repo_git'],
            "oauth_id": self.config['zombie_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Success",
            "total_results": self.results_counter
        }
        self.helper_db.execute(self.history_table.insert().values(task_history))
        logging.info("Recorded job completion for model: " + model + "\n")
        logging.info(task_completed)

        #update job process table
        updated_job = {
            "since_id_str": entry_info['repo_id'],
            "last_count": self.results_counter,
            "last_run": datetime.datetime.now(),
            "analysis_state": 0
        }
        self.helper_db.execute(self.job_table.update().where(self.job_table.c.job_model==model).values(updated_job))
        logging.info("Update job process for model: " + model + "\n")

        # Notify broker of completion
        logging.info("Telling broker we completed task: " + str(task_completed) + "\n" + 
            "This task inserted: " + str(self.results_counter) + " tuples.\n\n")

        requests.post('http://localhost:5000/api/unstable/completed_task', json=task_completed, headers=self.headers)

        # Reset results counter for next task
        self.results_counter = 0

    def record_model_process(self, model):
        updated_job = {
            "oauth_id": self.config['zombie_id'],
            "analysis_state": '1'
        }
        self.helper_db.execute(self.job_table.update().where(self.job_table.c.job_model==model).values(updated_job))
        logging.info("Update job process for model: " + model + "\n")
            

        
