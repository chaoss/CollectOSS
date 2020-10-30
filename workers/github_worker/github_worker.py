#SPDX-License-Identifier: MIT
from multiprocessing import Process, Queue
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy as s
import requests, time, logging, json, os
from datetime import datetime
from workers.worker_base import Worker

class GitHubWorker(Worker):
    """ Worker that collects data from the Github API and stores it in our database
    task: most recent task the broker added to the worker's queue
    child: current process of the queue being ran
    queue: queue of tasks to be fulfilled
    config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config={}):

        worker_type = 'github_worker'

        given = [['github_url']]
        models = ['issues']

        data_tables = ['contributors', 'issues', 'issue_labels', 'message',
            'issue_message_ref', 'issue_events','issue_assignees','contributors_aliases',
            'pull_request_assignees', 'pull_request_events', 'pull_request_reviewers', 'pull_request_meta',
            'pull_request_repo']
        operations_tables = ['worker_history', 'worker_job']

        # These 3 are included in every tuple the worker inserts (data collection info)
        self.tool_source = 'GitHub API Worker'
        self.tool_version = '1.0.0'
        self.data_source = 'GitHub API'

        self.finishing_task = True # if we are finishing a previous task, pagination works differenty
        self.platform_id = 25150 # GitHub

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)


    def issues_model(self, entry_info, repo_id):
        """ Data collection function
        Query the GitHub API for issues
        """
        # Get max ids so we know where we are in our insertion and to have the current id when inserting FK's
        self.logger.info("Querying starting ids info...\n")

        self.issue_id_inc = self.get_max_id('issues', 'issue_id')

        self.msg_id_inc = self.get_max_id('message', 'msg_id')

        github_url = entry_info['given']['github_url']

        self.logger.info("Beginning filling the issues model for repo: " + github_url + "\n")

        # Contributors are part of this model, and finding all for the repo saves us 
        #   from having to add them as we discover committers in the issue process
        self.query_github_contributors(entry_info, repo_id)

        # Extract the owner/repo for the endpoint
        path = urlparse(github_url)
        split = path[2].split('/')
        owner = split[1]
        name = split[2]

        # Handle git url case by removing extension
        if ".git" in name:
            name = name[:-4]

        # Set base of endpoint url
        url = "https://api.github.com/repos/{}/{}".format(owner, name)

        issues_url = url + "/issues?per_page=100&state=all&page={}"
        
        # Get issues that we already have stored
        #   Set pseudo key (something other than PK) to 
        #   check dupicates with
        table = 'issues'
        table_pkey = 'issue_id'
        update_col_map = {'comment_count': 'comments', 'issue_state': 'state'} #'updated_at': 'updated_at', 'closed_at': 'closed_at'
        duplicate_col_map = {'gh_issue_id': 'id'}

        #list to hold issues needing insertion
        issues = self.paginate(issues_url, duplicate_col_map, update_col_map, table, table_pkey, 
            'WHERE repo_id = {}'.format(repo_id))
        self.logger.info(issues)
        # Discover and remove duplicates before we start inserting
        self.logger.info("Count of issues needing update or insertion: " + str(len(issues)) + "\n")

        for issue_dict in issues:
            self.logger.info("Begin analyzing the issue with title: " + issue_dict['title'] + "\n")
            
            # Add the FK repo_id to the dict being inserted
            issue_dict['repo_id'] = repo_id

            # Figure out if this issue is a PR
            #   still unsure about this key value pair/what it means
            pr_id = None
            if 'pull_request' in issue_dict:
                self.logger.info("Issue is a PR\n")
                # Right now we are just storing our issue id as the PR id if it is one
                pr_id = self.issue_id_inc
            else:
                self.logger.info("Issue is not a PR\n")

            # Begin on the actual issue...
            issue = {
                "repo_id": issue_dict['repo_id'],
                "reporter_id": self.find_id_from_login(issue_dict['user']['login']),
                "pull_request": pr_id,
                "pull_request_id": pr_id,
                "created_at": issue_dict['created_at'],
                "issue_title": issue_dict['title'],
                "issue_body": issue_dict['body'].replace("0x00", "____") if issue_dict['body'] else None,
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
            if issue_dict['flag'] == 'need_update':
                result = self.db.execute(self.issues_table.update().where(
                    self.issues_table.c.gh_issue_id==issue_dict['id']).values(issue))
                self.logger.info("Updated tuple in the issues table with existing gh_issue_id: {}".format(
                    issue_dict['id']))
                self.issue_id_inc = issue_dict['pkey']
            elif issue_dict['flag'] == 'need_insertion':
                try:
                    result = self.db.execute(self.issues_table.insert().values(issue))
                    self.logger.info("Primary key inserted into the issues table: " + str(result.inserted_primary_key))
                    self.results_counter += 1
                    self.issue_id_inc = int(result.inserted_primary_key[0])
                    self.logger.info("Inserted issue with our issue_id being: {}".format(self.issue_id_inc) + 
                        " and title of: {} and gh_issue_num of: {}\n".format(issue_dict['title'],issue_dict['number']))
                except Exception as e:
                    self.logger.info("When inserting an issue, ran into the following error: {}\n".format(e))
                    self.logger.info(issue)
                    continue

            # Check if the assignee key's value is already recorded in the assignees key's value
            #   Create a collective list of unique assignees
            collected_assignees = issue_dict['assignees']
            if issue_dict['assignee'] not in collected_assignees:
                collected_assignees.append(issue_dict['assignee'])

            # Handles case if there are no assignees
            if collected_assignees[0] is not None:
                self.logger.info("Count of assignees to insert for this issue: " + str(len(collected_assignees)) + "\n")
                for assignee_dict in collected_assignees:
                    if type(assignee_dict) != dict:
                        continue
                    assignee = {
                        "issue_id": self.issue_id_inc,
                        "cntrb_id": self.find_id_from_login(assignee_dict['login']),
                        "tool_source": self.tool_source,
                        "tool_version": self.tool_version,
                        "data_source": self.data_source,
                        "issue_assignee_src_id": assignee_dict['id'],
                        "issue_assignee_src_node": assignee_dict['node_id']
                    }
                    # Commit insertion to the assignee table
                    result = self.db.execute(self.issue_assignees_table.insert().values(assignee))
                    self.logger.info("Primary key inserted to the issues_assignees table: " + str(result.inserted_primary_key))
                    self.results_counter += 1

                    self.logger.info("Inserted assignee for issue id: " + str(self.issue_id_inc) + 
                        " with login/cntrb_id: " + assignee_dict['login'] + " " + str(assignee['cntrb_id']) + "\n")
            else:
                self.logger.info("Issue does not have any assignees\n")

            # Insert the issue labels to the issue_labels table
            for label_dict in issue_dict['labels']:
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
                    "data_source": self.data_source,
                    "label_src_id": label_dict['id'],
                    "label_src_node_id": label_dict['node_id']
                }

                result = self.db.execute(self.issue_labels_table.insert().values(label))
                self.logger.info("Primary key inserted into the issue_labels table: " + str(result.inserted_primary_key))
                self.results_counter += 1

                self.logger.info("Inserted issue label with text: " + label_dict['name'] + "\n")


            #### Messages/comments and events insertion 
            comments_url = url + "/comments?per_page=100&page={}"

            # Get contributors that we already have stored
            #   Set our duplicate and update column map keys (something other than PK) to 
            #   check dupicates/needed column updates with
            table = 'message'
            table_pkey = 'msg_id'
            update_col_map = None #updates for comments not necessary
            duplicate_col_map = {'msg_timestamp': 'created_at'}

            #list to hold contributors needing insertion or update
            issue_comments = self.paginate(comments_url, duplicate_col_map, update_col_map, table, table_pkey, 
                where_clause="WHERE msg_id IN (SELECT msg_id FROM issue_message_ref WHERE issue_id = {})".format(
                    self.issue_id_inc))
                
            self.logger.info("Number of comments needing insertion: {}\n".format(len(issue_comments)))

            for comment in issue_comments:
                try:
                    commenter_cntrb_id = self.find_id_from_login(comment['user']['login'])
                except:
                    commenter_cntrb_id = None
                issue_comment = {
                    "pltfrm_id": self.platform_id,
                    "msg_text": comment['body'],
                    "msg_timestamp": comment['created_at'],
                    "cntrb_id": commenter_cntrb_id,
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }
                try:
                    result = self.db.execute(self.message_table.insert().values(issue_comment))
                    self.logger.info("Primary key inserted into the message table: {}".format(result.inserted_primary_key))
                    self.results_counter += 1
                    self.msg_id_inc = int(result.inserted_primary_key[0])

                    self.logger.info("Inserted issue comment with id: {}\n".format(self.msg_id_inc))
                except Exception as e:
                    self.logger.info("Worker ran into error when inserting a message, likely had invalid characters. error: {}".format(e))

                ### ISSUE MESSAGE REF TABLE ###

                issue_message_ref = {
                    "issue_id": self.issue_id_inc,
                    "msg_id": self.msg_id_inc,
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source,
                    "issue_msg_ref_src_comment_id": comment['id'],
                    "issue_msg_ref_src_node_id": comment['node_id']
                }

                result = self.db.execute(self.issue_message_ref_table.insert().values(issue_message_ref))
                self.logger.info("Primary key inserted into the issue_message_ref table: {}".format(result.inserted_primary_key))
                self.results_counter += 1                
        
            # Base of the url for event endpoints
            url = ("https://api.github.com/repos/" + owner + "/" + name + "/issues/" + str(issue_dict['number']))

            # Get events ready in case the issue is closed and we need to insert the closer's id
            events_url = url + "/events?per_page=100&page={}"
            issue_events = []
            
            # Get events that we already have stored
            #   Set pseudo key (something other than PK) to 
            #   check dupicates with
            pseudo_key_gh = 'url'
            pseudo_key_augur = 'node_url'
            table = 'issue_events'
            event_table_values = self.get_table_values([pseudo_key_augur], [table], "WHERE issue_id = {}".format(self.issue_id_inc))
            
            # Paginate backwards through all the events but get first page in order
            #   to determine if there are multiple pages and if the 1st page covers all
            i = 1
            multiple_pages = False

            while True:
                self.logger.info("Hitting endpoint: " + events_url.format(i) + " ...\n")
                r = requests.get(url=events_url.format(i), headers=self.headers)
                self.update_gh_rate_limit(r)

                # Find last page so we can decrement from there
                if 'last' in r.links and not multiple_pages and not self.finishing_task:
                    param = r.links['last']['url'][-6:]
                    i = int(param.split('=')[1]) + 1
                    self.logger.info("Multiple pages of request, last page is " + str(i - 1) + "\n")
                    multiple_pages = True
                elif not multiple_pages and not self.finishing_task:
                    self.logger.info("Only 1 page of request\n")
                elif self.finishing_task:
                    self.logger.info("Finishing a previous task, paginating forwards ... "
                        "excess rate limit requests will be made\n")

                j = r.json()

                # Checking contents of requests with what we already have in the db
                new_events = self.check_duplicates(j, event_table_values, pseudo_key_gh)
                if len(new_events) == 0 and multiple_pages and 'last' in r.links:
                    if i - 1 != int(r.links['last']['url'][-6:].split('=')[1]):
                        self.logger.info("No more pages with unknown events, breaking from pagination.\n")
                        break
                elif len(new_events) != 0:
                    to_add = [obj for obj in new_events if obj not in issue_events]
                    issue_events += to_add

                i = i + 1 if self.finishing_task else i - 1

                # Since we already wouldve checked the first page... break
                if (i == 1 and multiple_pages and not self.finishing_task) or i < 1 or len(j) == 0:
                    self.logger.info("No more pages to check, breaking from pagination.\n")
                    break

            self.logger.info("Number of events needing insertion: " + str(len(issue_events)) + "\n")

            # If the issue is closed, then we search for the closing event and store the user's id
            cntrb_id = None
            if 'closed_at' in issue_dict:
                for event in issue_events:
                    if str(event['event']) != "closed":
                        self.logger.info("not closed, continuing")
                        continue
                    if not event['actor']:
                        continue
                    cntrb_id = self.find_id_from_login(event['actor']['login'])
                    if cntrb_id is not None:
                        break
                        
                    # Need to hit this single contributor endpoint to get extra created at data...
                    cntrb_url = ("https://api.github.com/users/" + event['actor']['login'])
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
                    result = self.db.execute(self.contributors_table.insert().values(cntrb))
                    self.logger.info("Primary key inserted into the contributors table: {}".format(
                        result.inserted_primary_key))
                    self.results_counter += 1
    
                    self.logger.info("Inserted contributor: " + contributor['login'] + "\n")

            for event in issue_events:
                if event['actor'] is not None:
                    event['cntrb_id'] = self.find_id_from_login(event['actor']['login'])
                    if event['cntrb_id'] is None:
                        self.logger.info("SOMETHING WRONG WITH FINDING ID FROM LOGIN")
                        continue
                        # event['cntrb_id'] = None
                else:
                    continue
                    # event['cntrb_id'] = None

                issue_event = {
                    "issue_event_src_id": event['id'],
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
                self.logger.info("Primary key inserted into the issue_events table: " + str(result.inserted_primary_key))
                self.results_counter += 1

                self.logger.info("Inserted issue event: " + event['event'] + " for issue id: {}\n".format(self.issue_id_inc))

            if cntrb_id is not None:
                update_closing_cntrb = {
                    "cntrb_id": cntrb_id
                }
                result = self.db.execute(self.issues_table.update().where(
                    self.issues_table.c.gh_issue_id==issue_dict['id']).values(issue))
                self.logger.info("Updated tuple in the issues table with contributor that closed it, issue_id: {}\n".format(
                    issue_dict['id']))
            
            self.issue_id_inc += 1

        #Register this task as completed
        self.register_task_completion(entry_info, repo_id, "issues")

