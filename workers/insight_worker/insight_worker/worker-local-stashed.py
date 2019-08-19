from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
import statistics
import logging
import json
import numpy as np
import scipy.stats
import datetime
logging.basicConfig(filename='worker.log', filemode='w', level=logging.INFO)

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

class InsightWorker:
    """ Worker that collects data from the Github API and stores it in our database
    task: most recent task the broker added to the worker's queue
    child: current process of the queue being ran
    queue: queue of tasks to be fulfilled
    config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config, task=None):
        self._task = task
        self._child = None
        self._queue = Queue()
        self.config = config
        self.db = None
        self.tool_source = 'Insight Worker'
        self.tool_version = '0.0.1' # See __init__.py
        self.data_source = 'Augur API'

        logging.info("Worker initializing...")
        
        specs = {
            "id": "com.augurlabs.core.insight_worker",
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["repo_git"]],
                    "models":["insights"]
                }
            ],
            "config": [self.config]
        }

        self.metric_results_counter = 0
        self.insight_results_counter = 0

        """
        Connect to GHTorrent
        
        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
        """
        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['database']
        )

        dbschema='augur_data' # Searches left-to-right
        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        
        # produce our own MetaData object
        metadata = MetaData()

        # we can reflect it ourselves from a database, using options
        # such as 'only' to limit what tables we look at...
        metadata.reflect(self.db, only=['chaoss_metric_status', 'repo_insights'])

        # we can then produce a set of mappings from this MetaData.
        Base = automap_base(metadata=metadata)

        # calling prepare() just sets up mapped classes and relationships.
        Base.prepare()

        # mapped classes are ready
        self.chaoss_metric_status_table = Base.classes['chaoss_metric_status'].__table__
        self.repo_insights_table = Base.classes['repo_insights'].__table__

        requests.post('http://localhost:{}/api/unstable/workers'.format(
            self.config['broker_port']), json=specs) #hello message

        # Query all repos and last repo id
        repoUrlSQL = s.sql.text("""
                SELECT repo_git, repo_id FROM repo ORDER BY repo_id DESC
            """)
        rs = pd.read_sql(repoUrlSQL, self.db, params={}).to_records()
        pop_off = 0
        i = 0
        while i < pop_off:
            rs = rs[1:]
            i += 1
        for row in rs:
            self._queue.put({'repo_id': row['repo_id'], 'repo_git': row['repo_git']})
        self.run()
        # self.discover_insights({'repo_id': 21000, 'repo_git': 'https://github.com/rails/rails.git'})

    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            'database_connection_string': 'psql://localhost:5432/augur',
            "display_name": "",
            "description": "",
            "required": 1,
            "type": "string"
        }
        self.config.update(config)

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
        repo_git = value['given']['repo_git']

        """ Query all repos """
        repoUrlSQL = s.sql.text("""
            SELECT repo_id, repo_group_id FROM repo WHERE repo_git = '{}'
            """.format(repo_git))
        rs = pd.read_sql(repoUrlSQL, self.db, params={})
        try:
            self._queue.put(CollectorTask(message_type='TASK', entry_info={"repo_git": repo_git, 
                "repo_id": rs.iloc[0]["repo_id"], "repo_group_id": rs.iloc[0]["repo_group_id"]}))
        except:
            print("that repo is not in our database")
        if self._queue.empty(): 
            if 'github.com' in repo_git:
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
        logging.info("Running...\n")
        if not self._child:
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
            self.discover_insights(message)

    def discover_insights(self, entry_info):
        """ Data collection function
        Query the github api for contributors and issues (not yet implemented)
        """
        # Update table of endpoints before we query them all
        # self.update_metrics()
        logging.info("Discovering insights for task with entry info: {}".format(entry_info))

        lengthSQL = s.sql.text("""
            SELECT DISTINCT(cms_id) FROM repo_insights WHERE repo_id = {}
        """.format(entry_info['repo_id']))
        ins = pd.read_sql(lengthSQL, self.db, params={})
        logging.info(len(ins.index))
        if len(ins.index) < 3:
    
            # """ Query all endpoints """
            endpointSQL = s.sql.text("""
                SELECT * FROM chaoss_metric_status WHERE cm_source = 'augur_db'
                """)
            endpoints = [{'cm_info': "issues-new", 'cm_name': 'New Issues'}, {'cm_info': "code-changes", 
                'cm_name': 'Commit Count'}, {'cm_info': "code-changes-lines", 'cm_name': 'Lines of Code Changed'}, 
                {'cm_info': "reviews", 'cm_name': 'Pull Requests'}]
            for endpoint in pd.read_sql(endpointSQL, self.db, params={}).to_records():
                endpoints.append(endpoint)

            if 'repo_group_id' in entry_info:
                base_url = 'http://localhost:{}/api/unstable/repo-groups/{}'.format(
                    self.config['broker_port'], entry_info['repo_group_id'])
            else:
                base_url = 'http://localhost:{}/api/unstable/repo-groups/9999/repos/{}/'.format(
                    self.config['broker_port'], entry_info['repo_id'])

            num_insights_per_repo = 3
            cms_id = len(ins.index) + 1
            for endpoint in endpoints:
                url = base_url + endpoint['cm_info']
                logging.info("Hitting endpoint: " + url + "\n")
                r = requests.get(url=url)
                data = r.json()

                def is_unique_key(key):
                    return 'date' not in key and key != 'repo_group_id' and key != 'repo_id' and key != 'repo_name' and key != 'rg_name'
                raw_values = {}

                if len(data) > 0:
                    try:
                        unique_keys = list(filter(is_unique_key, data[0].keys()))
                    except:
                        logging.info("Length bigger than 0 but cannot get 0th element? : {}".format(data))
                else:
                    logging.info("Endpoint with url: {} returned an empty response. Moving on to next endpoint.\n".format(url))
                    continue

                # ci after past year insights after 90 days
                # num issues, issue comments, num commits, num pr, comments pr
                logging.info("Found the following unique keys for this endpoint: {}".format(unique_keys))
                date_filtered_data = []
                i = 0
                not_timeseries = False
                for dict in data:
                    begin_date = datetime.datetime.now()
                    # Subtract 1 year and leap year check
                    try:
                        begin_date = begin_date.replace(year=begin_date.year-1)
                    except ValueError:
                        begin_date = begin_date.replace(year=begin_date.year-1, day=begin_date.day-1)
                    begin_date = begin_date.strftime('%Y-%m-%d')
                    try:
                        if dict['date'] > begin_date:
                            date_filtered_data = data[i:]
                            logging.info("data 365 days ago date found: {}, {}".format(dict['date'], begin_date))
                            break
                    except:
                        logging.info("Endpoint {} is not a timeseries, moving to next".format(endpoint))
                        not_timeseries = True
                        break
                    i += 1
                if not_timeseries:
                    continue

                date_found_index = None
                date_found = False
                x = 0
                begin_date = datetime.datetime.now() - datetime.timedelta(days=90)
                for dict in date_filtered_data:
                    dict_date = datetime.datetime.strptime(dict['date'], '%Y-%m-%dT%H:%M:%S.%fZ')#2018-08-20T00:00:00.000Z
                    if dict_date > begin_date and not date_found:
                        date_found = True
                        date_found_index = x
                        logging.info("raw values 90 days ago date found: {}, {}".format(dict['date'], begin_date))
                    x += 1
                    for key in unique_keys:
                        try:
                            trash = int(dict[key]) * 2 + 1
                            raw_values[key].append(int(dict[key]))
                        except:
                            try:
                                trash = int(dict[key]) * 2 + 1
                                raw_values[key] = [int(dict[key])]
                            except:
                                logging.info("Key: {} is non-numerical, moving to next key.".format(key))

                for key in raw_values.keys():
                    if len(raw_values[key]) > 0:
                        confidence = 0.95
                        mean, lower, upper = self.confidence_interval(raw_values[key], confidence=confidence)
                        logging.info("Upper: {}, middle: {}, lower: {}".format(upper, mean, lower))
                        i = 0
                        discovery_index = None
                        insight = False
                        max_difference = 0
                        score = 0.0


                        date_filtered_raw_values = []
                        date_filtered_raw_values = raw_values[key][date_found_index:]
                        
                        for value in date_filtered_raw_values:
                            if value > upper and value - upper > max_difference and i != 0:
                                logging.info("Upper band breached. Marking discovery.")
                                max_difference = value - upper
                                score = (max_difference - mean) / mean * 100
                                insight = True
                                discovery_index = i
                                break
                            if value < lower and lower - value > max_difference and i != 0:
                                logging.info("Lower band breached. Marking discovery.")
                                max_difference = lower - value
                                score = (max_difference - mean) / mean * 100
                                insight = True
                                discovery_index = i
                                break
                            i += 1
                        if insight and 'date' in data[0]:
                            self.clear_insight(entry_info['repo_id'], cms_id)
                            # j = discovery_index - 50 if discovery_index >= 50 else 0
                            j = 0
                            # upper_index = discovery_index + 50 if discovery_index >= 50 else 99
                            logging.info("Starting j: {}, discovery_index: {}, data: {}".format(j, discovery_index, date_filtered_data[j]))
                            # while j <= upper_index:
                            for tuple in date_filtered_data:
                                try:
                                    data_point = {
                                        'repo_id': int(entry_info['repo_id']),
                                        'ri_metric': endpoint['cm_name'] + ' ({})'.format(key),
                                        'ri_value': tuple[key],#date_filtered_data[j][key],
                                        'ri_date': tuple['date'],#date_filtered_data[j]['date'],
                                        'cms_id': cms_id,
                                        'ri_fresh': 0 if j < discovery_index else 1,
                                        'ri_score': score,
                                        "tool_source": self.tool_source,
                                        "tool_version": self.tool_version,
                                        "data_source": self.data_source
                                    }
                                    result = self.db.execute(self.repo_insights_table.insert().values(data_point))
                                    logging.info("Primary key inserted into the repo_insights table: " + str(result.inserted_primary_key))
                                    self.insight_results_counter += 1

                                    logging.info("Inserted data point for endpoint: {}\n".format(endpoint['cm_name']))
                                    j += 1
                                    logging.info("incremented j: {}, discovery_index: {}, data: {}".format(j, discovery_index, date_filtered_data[j]))
                                except Exception as e:
                                    logging.info("error occurred while storing datapoint: {}".format(repr(e)))
                                    break
                            cms_id += 1
                            if cms_id > num_insights_per_repo:
                                logging.info("Have successfully stored {} insights for repo: {}, breaking from discovery loop".format(
                                    num_insights_per_repo, entry_info['repo_id']))
                                break
                    else:
                        logging.info("Key: {} has empty raw_values, should not have key here".format(key))
                        if cms_id > num_insights_per_repo:
                            logging.info("Have successfully stored {} insights for repo: {}, breaking from discovery loop".format(
                                num_insights_per_repo, entry_info['repo_id']))
                            break
                if cms_id > num_insights_per_repo:
                    logging.info("Have successfully stored {} insights for repo: {}, breaking from discovery loop".format(
                        num_insights_per_repo, entry_info['repo_id']))
                    break

        # HIGHEST PERCENTAGE STUFF, WILL MOVE TO NEW METHOD
            # greatest_week_name = greatest_month_name = insights[0]['cm_name']
            # greatest_week_val = abs(insights[0]['change_week'])
            # greatest_month_val = abs(insights[0]['change_month'])

            # for insight in insights:
            #     if abs(insight['change_week']) > greatest_week:
            #         greatest_week_name = insight['cm_name']
            #         greatest_week_val = insight['change_week']

            #     if abs(insight['change_month']) > greatest_month:
            #         greatest_month_name = insight['cm_name']
            #         greatest_month_val = insight['change_month']

            # logging.info("The endpoint with the greatest percent change in the last week was {} with {}%%".format(greatest_week_name, greatest_week_val))
            # logging.info("The endpoint with the greatest percent change in the last month was {} with {}%%".format(greatest_month_name, greatest_month_val))




            # data[0]['repo_id'] = entry_info['repo_id']
            # metrics = []
            # for obj in data:
            #     metrics.append(obj['tag'])

            
            # self.db.execute(self.table.insert().values(data[0]))
            # requests.post('http://localhost:{}/api/completed_task'.format(
                # self.config['broker_port']), json=entry_info['repo_git'])
        else:
            logging.info("there are 303 or more tuples for repo: {}, skipping this task".format(entry_info))

    def clear_insight(self, repo_id, cms_id):
        logging.info("Checking if insight slot filled...")
        insightSQL = s.sql.text("""
            SELECT *
            FROM repo_insights
            WHERE repo_id = {} AND cms_id = {}
        """.format(repo_id, cms_id))
        ins = pd.read_sql(insightSQL, self.db, params={})
        if len(ins.index) > 0:
            logging.info("insight slot filled for repo {} slot {}".format(repo_id, cms_id))
            try:
                result = self.repo_insights_table.delete().where(self.repo_insights_table.c.repo_id==repo_id and self.repo_insights_table.c.cms_id==cms_id)
                result.execute()
                logging.info(str(result))
                logging.info(str(result.fetchall()))
            except:
                self.repo_insights_table.delete().where(self.repo_insights_table.c.repo_id==repo_id and self.repo_insights_table.c.cms_id==cms_id)



    def confidence_interval(self, data, timeperiod='week', confidence=.8):
        """ Method to find high activity issues in the past specified timeperiod """
        a = 1.0 * np.array(data)
        logging.info("np array: {}".format(a))
        n = len(a)
        m, se = np.mean(a), scipy.stats.sem(a)
        logging.info("Mean: {}, standard error: {}".format(m, se))
        h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
        logging.info("H: {}".format(h))
        return m, m-h, m+h


    def update_metrics(self):
        logging.info("Preparing to update metrics ...\n\n" + 
            "Hitting endpoint: http://localhost:{}/api/unstable/metrics/status ...\n".format(
            self.config['broker_port']))
        r = requests.get(url='http://localhost:{}/api/unstable/metrics/status'.format(
            self.config['broker_port']))
        data = r.json()

        active_metrics = [metric for metric in data if metric['backend_status'] == 'implemented']

        # Duplicate checking ...
        need_insertion = self.filter_duplicates({'cm_api_endpoint_repo': "endpoint"}, ['chaoss_metric_status'], active_metrics)
        logging.info("Count of contributors needing insertion: " + str(len(need_insertion)) + "\n")

        for metric in need_insertion:

            tuple = {
                "cm_group": metric['group'],
                "cm_source": metric['data_source'],
                "cm_type": metric['metric_type'],
                "cm_backend_status": metric['backend_status'],
                "cm_frontend_status": metric['frontend_status'],
                "cm_defined": True if metric['is_defined'] == 'true' else False,
                "cm_api_endpoint_repo": metric['endpoint'],
                "cm_api_endpoint_rg": None,
                "cm_name": metric['display_name'],
                "cm_working_group": metric['group'],
                "cm_info": metric['tag'],
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": metric['data_source']
            }
            # Commit metric insertion to the chaoss metrics table
            result = self.db.execute(self.chaoss_metric_status_table.insert().values(tuple))
            logging.info("Primary key inserted into the metrics table: " + str(result.inserted_primary_key))
            self.metric_results_counter += 1

            logging.info("Inserted metric: " + metric['display_name'] + "\n")

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

    def greatest_percentage(self):

        querySQL = s.sql.text("""
            SELECT cm_info FROM chaoss_metric_status WHERE data_collection_date = now() - interval '? days'
            """)

        data_now = pd.read_sql(querySQL, self.db, params={0})
        data_week = pd.read_sql(querySQL, self.db, params={7})
        data_month = pd.read_sql(querySQL, self.db, params={30})

        """ Testing query functionality """
        # print("\n\nNOW\n\n", data_now)
        # print("\n\nWEEK\n\n", data_week)
        # print("\n\nMONTH\n\n", data_month)

        """ Determine these subscripts """
        # change_week = (data_now[] - data_week[])/data_now[]
        # change_month = (data_now[] - data_month[])/data_now[]

        new_insight = {
            "cm_name": data['cm_name'],
            "change_week": change_week,
            "change_month": change_month,
        }

        return new_insight

