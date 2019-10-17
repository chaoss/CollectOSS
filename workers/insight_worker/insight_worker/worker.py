from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData, and_
import statistics
import logging
import json, time
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
        self.tool_version = '0.0.2' # See __init__.py
        self.data_source = 'Augur API'
        self.refresh = True
        self.send_insights = True
        self.finishing_task = False

        logging.info("Worker initializing...")
        
        specs = {
            "id": self.config['id'],
            "location": self.config['location'],
            "qualifications":  [
                {
                    "given": [["git_url"]],
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

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(self.DB_STR, poolclass = s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})
        
        # produce our own MetaData object
        metadata = MetaData()
        helper_metadata = MetaData()

        # we can reflect it ourselves from a database, using options
        # such as 'only' to limit what tables we look at...
        metadata.reflect(self.db, only=['chaoss_metric_status', 'repo_insights', 'repo_insights_records'])
        helper_metadata.reflect(self.helper_db, only=['worker_history', 'worker_job'])

        # we can then produce a set of mappings from this MetaData.
        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)

        # calling prepare() just sets up mapped classes and relationships.
        Base.prepare()
        HelperBase.prepare()

        # mapped classes are ready
        self.chaoss_metric_status_table = Base.classes['chaoss_metric_status'].__table__
        self.repo_insights_table = Base.classes['repo_insights'].__table__
        self.repo_insights_records_table = Base.classes['repo_insights_records'].__table__

        self.history_table = HelperBase.classes.worker_history.__table__
        self.job_table = HelperBase.classes.worker_job.__table__

        requests.post('http://{}:{}/api/unstable/workers'.format(
            self.config['broker_host'],self.config['broker_port']), json=specs) #hello message


    def update_config(self, config):
        """ Method to update config and set a default
        """
        self.config = {
            'database_connection_string': 'psql://{}:5432/augur'.format(self.config['broker_host']),
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
        repo_git = value['given']['git_url']

        """ Query all repos """
        repoUrlSQL = s.sql.text("""
            SELECT repo_id, repo_group_id FROM repo WHERE repo_git = '{}'
            """.format(repo_git))
        rs = pd.read_sql(repoUrlSQL, self.db, params={})
        try:
            self._queue.put({"git_url": repo_git, 
                "repo_id": int(rs.iloc[0]["repo_id"]), "repo_group_id": int(rs.iloc[0]["repo_group_id"]), "job_type": value['job_type']})
        except Exception as e:
            logging.info("that repo is not in our database, {}".format(e))
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
        self._child = Process(target=self.collect, args=())
        self._child.start()

    def collect(self):
        """ Function to process each entry in the worker's task queue
        Determines what action to take based off the message type
        """
        while True:
            time.sleep(2)
            if not self._queue.empty():
                message = self._queue.get()
            # else:
            #     break
                self.discover_insights(message)

    def discover_insights(self, entry_info):
        """ Data collection function
        Query the github api for contributors and issues (not yet implemented)
        """

        # Update table of endpoints before we query them all
        logging.info("Discovering insights for task with entry info: {}".format(entry_info))
        self.record_model_process(entry_info, 'insights')

        # Set the endpoints we want to discover insights for
        endpoints = [{'cm_info': "issues-new"}, {'cm_info': "code-changes"}, {'cm_info': "code-changes-lines"}, 
            {'cm_info': 'reviews'}]

        """"""

        """ For when we want all endpoints """

        # """ Query all endpoints """
        # endpointSQL = s.sql.text("""
        #     SELECT * FROM chaoss_metric_status WHERE cm_source = 'augur_db'
        #     """)
        # for endpoint in pd.read_sql(endpointSQL, self.db, params={}).to_records():
        #     endpoints.append(endpoint)

        """"""

        # If we are discovering insights for a group vs repo, the base url will change
        if 'repo_group_id' in entry_info and 'repo_id' not in entry_info:
            base_url = 'http://{}:{}/api/unstable/repo-groups/{}/'.format(
                self.config['broker_host'],self.config['broker_port'], entry_info['repo_group_id'])
        else:
            base_url = 'http://{}:{}/api/unstable/repo-groups/9999/repos/{}/'.format(
                self.config['broker_host'],self.config['broker_port'], entry_info['repo_id'])

        # Hit and discover insights for every endpoint we care about
        for endpoint in endpoints:

            # Hit endpoint
            url = base_url + endpoint['cm_info']
            logging.info("Hitting endpoint: " + url + "\n")
            r = requests.get(url=url)
            data = r.json()

            def is_unique_key(key):
                """ Helper method used to find which keys we want to analyze in each data point """
                return 'date' not in key and key != 'repo_group_id' and key != 'repo_id' and key != 'repo_name' and key != 'rg_name'
            
            # Filter out keys that we do not want to analyze (e.g. repo_id)
            raw_values = {}
            unique_keys = None
            if len(data) > 0:
                try:
                    unique_keys = list(filter(is_unique_key, data[0].keys()))
                except Exception as e:
                    logging.info("Length bigger than 0 but cannot get 0th element? : {}, {}".format(data, e))
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
                    score = 0

                    date_filtered_raw_values = []
                    date_filtered_raw_values = date_filtered_data[date_found_index:]
                    logging.info("Raw values: {}".format(date_filtered_raw_values))
                    for dict in date_filtered_raw_values:
                        if (dict[key] > upper and dict[key] - upper > max_difference) or (dict[key] < lower and lower - dict[key] > max_difference):
                            logging.info("Band breached at {}. Marking discovery. dict: {}, key: {}, mean: {}".format(i, dict, key, mean))
                            max_difference = max(dict[key] - upper,lower - dict[key])
                            score = abs(dict[key] - mean) / mean * 100
                            insight = True
                            discovery_index = i
                        i += 1
                    if insight and 'date' in data[0]:

                        ### INSIGHT DISCOVERED ###

                        # Check if new insight has a better score than other insights in its place, use result
                        #   to determine if we continue in the insertion process (0 for no insertion, 1 for record
                        #   insertion, 2 for record and insight data points insertion)
                        instructions = self.clear_insight(entry_info['repo_id'], score, endpoint['cm_info'], key)
                        # self.clear_insight(entry_info['repo_id'], score, endpoint['cm_info'] + ' ({})'.format(key))

                        # Use result from clearing function to determine if we need to insert the record
                        if instructions['record']:

                            # Insert record in records table and send record to slack bot
                            record = {
                                'repo_id': int(entry_info['repo_id']),
                                'ri_metric': endpoint['cm_info'],
                                'ri_field': key,
                                'ri_value': date_filtered_raw_values[discovery_index][key],#date_filtered_raw_values[j][key],
                                'ri_date': date_filtered_raw_values[discovery_index]['date'],#date_filtered_raw_values[j]['date'],
                                'ri_score': score,
                                'ri_detection_method': '95% confidence interval',
                                "tool_source": self.tool_source,
                                "tool_version": self.tool_version,
                                "data_source": self.data_source
                            }
                            result = self.db.execute(self.repo_insights_records_table.insert().values(record))
                            logging.info("Primary key inserted into the repo_insights_records table: {}".format(result.inserted_primary_key))
                            self.insight_results_counter += 1
                            # Send insight to Jonah for slack bot
                            self.send_insight(record, abs(date_filtered_raw_values[discovery_index][key] - mean))

                        # Use result from clearing function to determine if we still need to insert the insight
                        if instructions['insight']:

                            j = 0
                            logging.info("Starting j: {}, discovery_index: {}, data: {}".format(j, discovery_index, date_filtered_data[j]))
                            for tuple in date_filtered_raw_values:
                                try:
                                    data_point = {
                                        'repo_id': int(entry_info['repo_id']),
                                        'ri_metric': endpoint['cm_info'],
                                        'ri_field': key,
                                        'ri_value': tuple[key],#date_filtered_raw_values[j][key],
                                        'ri_date': tuple['date'],#date_filtered_raw_values[j]['date'],
                                        'ri_fresh': 0 if j < discovery_index else 1,
                                        'ri_score': score,
                                        'ri_detection_method': '95% confidence interval',
                                        "tool_source": self.tool_source,
                                        "tool_version": self.tool_version,
                                        "data_source": self.data_source
                                    }
                                    result = self.db.execute(self.repo_insights_table.insert().values(data_point))
                                    logging.info("Primary key inserted into the repo_insights table: " + str(result.inserted_primary_key))

                                    logging.info("Inserted data point for endpoint: {}\n".format(endpoint['cm_info']))
                                    j += 1
                                    logging.info("incremented j: {}, discovery_index: {}, data: {}".format(j, discovery_index, date_filtered_data[j]))
                                except Exception as e:
                                    logging.info("error occurred while storing datapoint: {}".format(repr(e)))
                                    break
                else:
                    logging.info("Key: {} has empty raw_values, should not have key here".format(key))

        self.register_task_completion(entry_info, "insights")

    def record_model_process(self, entry_info, model):

        task_history = {
            "repo_id": entry_info['repo_id'],
            "worker": self.config['id'],
            "job_model": model,
            "oauth_id": self.config['zombie_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Stopped",
            "total_results": self.insight_results_counter
        }
        if self.finishing_task:
            result = self.helper_db.execute(self.history_table.update().where(
                self.history_table.c.history_id==self.history_id).values(task_history))
        else:
            result = self.helper_db.execute(self.history_table.insert().values(task_history))
            logging.info("Record incomplete history tuple: {}".format(result.inserted_primary_key))
            self.history_id = int(result.inserted_primary_key[0])

    def register_task_completion(self, entry_info, model):
        # Task to send back to broker
        task_completed = {
            'worker_id': self.config['id'],
            'job_type': entry_info['job_type'],
            'repo_id': entry_info['repo_id'],
            'git_url': entry_info['git_url']
        }
        # Add to history table
        task_history = {
            "repo_id": entry_info['repo_id'],
            "worker": self.config['id'],
            "job_model": model,
            "oauth_id": self.config['zombie_id'],
            "timestamp": datetime.datetime.now(),
            "status": "Success",
            "total_results": self.insight_results_counter
        }
        self.helper_db.execute(self.history_table.update().where(
            self.history_table.c.history_id==self.history_id).values(task_history))

        logging.info("Recorded job completion for: " + str(task_completed) + "\n")

        # Update job process table
        updated_job = {
            "since_id_str": entry_info['repo_id'],
            "last_count": self.insight_results_counter,
            "last_run": datetime.datetime.now(),
            "analysis_state": 0
        }
        self.helper_db.execute(self.job_table.update().where(
            self.job_table.c.job_model==model).values(updated_job))
        logging.info("Update job process for model: " + model + "\n")

        # Notify broker of completion
        logging.info("Telling broker we completed task: " + str(task_completed) + "\n\n" + 
            "This task inserted: " + str(self.insight_results_counter) + " tuples.\n\n")

        requests.post('http://{}:{}/api/unstable/completed_task'.format(
            self.config['broker_host'],self.config['broker_port']), json=task_completed)

        # Reset results counter for next task
        self.insight_results_counter = 0

    def send_insight(self, insight, units_from_mean):
        try:
            begin_date = datetime.datetime.now() - datetime.timedelta(days=7)
            dict_date = datetime.datetime.strptime(insight['ri_date'], '%Y-%m-%dT%H:%M:%S.%fZ')#2018-08-20T00:00:00.000Z
            if dict_date > begin_date and self.send_insights:
                logging.info("Insight less than 7 days ago date found: {}\n\nSending to Jonah...".format(insight))
                to_send = {
                    'insight': True,
                    'rg_name': insight['rg_name'],
                    'repo_git': insight['repo_git'],
                    'value': insight['ri_value'],
                    'field': insight['ri_field'],
                    'metric': insight['ri_metric'],
                    'units_from_mean': units_from_mean,
                    'detection_method': insight['ri_detection_method']
                }
                requests.post('https://7oksmwzsy7.execute-api.us-east-2.amazonaws.com/dev-1/insight-event', json=to_send)
        except Exception as e:
            logging.info("sending insight to jonah failed: {}".format(e))



    def clear_insight(self, repo_id, new_score, new_metric, new_field):
        logging.info("Checking if insight slots filled...")

        # Dict that will be returned that instructs the rest of the worker where the insight insertion is 
        #   needed (determined by if this new insights score is higher than already stored ones)
        insertion_directions = {'record': False, 'insight': False}

        # Query current record for this
        recordSQL = s.sql.text("""
            SELECT ri_metric, repo_id, ri_score, ri_field
            FROM repo_insights_records
            WHERE repo_id = {}
            AND ri_metric = '{}'
            AND ri_field = '{}'
            ORDER BY ri_score DESC
        """.format(repo_id, new_metric, new_field))
        rec = json.loads(pd.read_sql(recordSQL, self.db, params={}).to_json(orient='records'))
        logging.info("recordsql: {}, \n{}".format(recordSQL, rec))
        # If new score is higher, continue with deletion
        if len(rec) > 0:
            if new_score > rec[0]['ri_score'] or self.refresh:
                insertion_directions['record'] = True
                for record in rec:
                    logging.info("Refresh is on or Insight record found with a greater score than current slot filled for "
                        "repo {} metric {} new score {}, old score {}".format(repo_id, record['ri_metric'], new_score, record['ri_score']))
                    deleteSQL = """
                        DELETE 
                            FROM
                                repo_insights_records I
                            WHERE
                                repo_id = {}
                                AND ri_metric = '{}'
                                AND ri_field = '{}'
                    """.format(record['repo_id'], record['ri_metric'], record['ri_field'])
                    try:
                        result = self.db.execute(deleteSQL)
                    except Exception as e:
                        logging.info("Error occured deleting insight slot: {}".format(e))
        else:
            insertion_directions['record'] = True

        # Query current insights and rank by score
        num_insights_per_repo = 2
        insightSQL = s.sql.text("""
            SELECT distinct(ri_metric),repo_id, ri_score
            FROM repo_insights
            WHERE repo_id = {}
            ORDER BY ri_score ASC
        """.format(repo_id))
        ins = json.loads(pd.read_sql(insightSQL, self.db, params={}).to_json(orient='records'))
        logging.info("This repos insights: {}".format(ins))

        # Determine if inisghts need to be deleted based on if there are more insights than we want stored,
        #   or if the current insights have a lower score
        num_insights = len(ins)
        to_delete = []
        for insight in ins:
            insight['ri_score'] = insight['ri_score'] if insight['ri_score'] else 0.0
            logging.info("{}, {}, {}, {}".format(insight['ri_metric'], new_metric, insight['ri_score'], num_insights_per_repo))
            if (insight['ri_score'] < new_score and num_insights >= num_insights_per_repo) or num_insights > num_insights_per_repo or (insight['ri_metric'] == new_metric and self.refresh):
                num_insights -= 1
                to_delete.append(insight)
                logging.info("condition met, new len: {}, insight score: {}, new_score: {}".format(num_insights,
                    insight['ri_score'], new_score))

        # After psuedo-deletion, determine if insertion of the new insight is needed
        if num_insights < num_insights_per_repo:
            insertion_directions['insight'] = True

        # Delete all insights marked for deletion
        for insight in to_delete:
            logging.info("insight found with a greater score than current slots filled for repo {} new score {}, old score {}".format(repo_id, new_score, insight['ri_score']))
            deleteSQL = """
                DELETE 
                    FROM
                        repo_insights I
                    WHERE
                        repo_id = {}
                        AND ri_metric = '{}'
            """.format(insight['repo_id'], insight['ri_metric'])
            try:
                result = self.db.execute(deleteSQL)
            except Exception as e:
                logging.info("Error occured deleting insight slot: {}".format(e))
        
        return insertion_directions


    def confidence_interval(self, data, timeperiod='week', confidence=.95):
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
            "Hitting endpoint: http://{}:{}/api/unstable/metrics/status ...\n".format(
            self.config['broker_host'],self.config['broker_port']))
        r = requests.get(url='http://{}:{}/api/unstable/metrics/status'.format(
            self.config['broker_host'],self.config['broker_port']))
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
                "cm_info": metric['display_name'],
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

