import base64
import logging
import os
import re
import sys
import time
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse

import pandas as pd
import requests
import sqlalchemy as s
from github import Github
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base

logging.basicConfig(filename='worker.log', level=logging.INFO, filemode='w')


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


class MetricStatusWorker:
    def __init__(self, config, task=None):
        self._task = task
        self._child = None
        self._queue = Queue()
        self._maintain_queue = Queue()
        self.config = config
        self.db = None
        self.table = None
        self.API_KEY = self.config['key']
        self.tool_source = 'Metric Status Worker'
        self.tool_version = '0.0.1'
        self.data_source = 'GitHub API'
        self.results_counter = 0
        self.working_on = None


        # url = 'https://api.github.com'
        # response = requests.get(url, headers=self.headers)
        # self.rate_limit = int(response.headers['X-RateLimit-Remaining'])

        specs = {
            "id": "com.augurlabs.core.chaoss_metric_status",
            "location": "http://localhost:51238",
            "qualifications":  [
                {
                    "given": [],
                    "models":["chaoss_metric_status"]
                }
            ],
            "config": [self.config]
        }

        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user'], self.config['password'], self.config['host'], self.config['port'], self.config['database']
        )

        logging.info("Making database connections...")

        dbschema = 'augur_data'
        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
                                  connect_args={'options': '-csearch_path={}'.format(dbschema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
                                         connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        metadata = MetaData()
        helper_metadata = MetaData()

        metadata.reflect(self.db, only=['chaoss_metric_status'])
        # helper_metadata.reflect(self.helper_db)

        Base = automap_base(metadata=metadata)

        Base.prepare()

        self.chaoss_metric_status_table =Base.classes['chaoss_metric_status'].__table__

        # logging.info('Getting max repo_info_id...')
        # max_repo_info_id_sql = s.sql.text("""
        #     SELECT MAX(repo_info_id) AS repo_info_id
        #     FROM repo_info
        # """)
        # rs = pd.read_sql(max_repo_info_id_sql, self.db)

        # repo_info_start_id = int(
        #     rs.iloc[0]['repo_info_id']) if rs.iloc[0]['repo_info_id'] is not None else 1

        # if repo_info_start_id == 1:
        #     self.info_id_inc = repo_info_start_id
        # else:
        #     self.info_id_inc = repo_info_start_id + 1

        # requests.post('http://localhost:5000/api/unstable/workers', json=specs)
        try:
            requests.post('http://localhost:{}/api/unstable/workers'.format(
                self.config['broker_port']), json=specs)
        except requests.exceptions.ConnectionError:
            logging.error('Cannot connect to the broker')
            sys.exit('Cannot connect to the broker! Quitting...')

    @property
    def task(self):
        """ Property that is returned when the worker's current task is referenced """
        return self._task

    @task.setter
    def task(self, value):  
        try:
            if value['job_type'] == 'UPDATE':
                self._queue.put(CollectorTask('TASK', {}))
            elif value['job_type'] == 'MAINTAIN':
                self._maintain_queue.put(CollectorTask('TASK', {}))

            if 'focused_task' in value:
                if value['focused_task'] == 1:
                    self.finishing_task = True
        except Exception as e:
            logging.error("Error: {},".format(str(e)))

        self._task = CollectorTask('TASK', {})
        self.run()

    def cancel(self):
        """ Delete/cancel current task """
        self._task = None

    def run(self):
        logging.info("Running...")
        if self._child is None:
            self._child = Process(target=self.collect, args=())
            self._child.start()
            requests.post("http://localhost:{}/api/unstable/add_pids".format(
                self.config['broker_port']), json={'pids': [self._child.pid, os.getpid()]})

    def collect(self):
        while True:
            if not self._queue.empty():
                message = self._queue.get()
                self.working_on = 'UPDATE'
            elif not self._maintain_queue.empty():
                message = self._maintain_queue.get()
                logging.info("Popped off message: {}".format(str(message.entry_info)))
                self.working_on = "MAINTAIN"
            else:
                break


            if message.type == 'EXIT':
                break
            if message.type != 'TASK':
                raise ValueError(
                    f'{message.type} is not a recognized task type')

            if message.type == 'TASK':
                self.update_metrics(message.entry_info)

    def update_metrics(self, entry_info):
        """ Data colletction function
        Query the github api for metric status
        """
        status = MetricsStatus(self.API_KEY)
        metrics = status.update_metrics()
        
        # convert to dict
        dict_metrics = []
        for metric in metrics:
            metric_info = {
                'cm_group': metric.group,
                'cm_source': metric.html_url,
                'cm_type': 'metric',
                'cm_backend_status': metric.backend_status,
                'cm_frontend_status': metric.frontend_status,
                'cm_api_endpoint_repo': metric.endpoint_repo,
                'cm_api_endpoint_rg': metric.endpoint_group,
                'cm_defined': metric.defined,
                'cm_name': metric.display_name,
                'cm_working_group': metric.group,
                'cm_info': re.sub('_', '-', metric.tag),
                'cm_working_group_focus_area': metric.focus_area,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            dict_metrics.append(metric_info)
        
        self.update_exist_metrics(dict_metrics)
        need_insertion = self.filter_duplicates(dict_metrics)
        logging.info("Count of contributors needing insertion: " + str(len(need_insertion)) + "\n")
        for metric in need_insertion:
            result = self.db.execute(self.chaoss_metric_status_table.insert().values(metric))
            logging.info("Primary key inserted into the metrics table: " + str(result.inserted_primary_key))
            self.results_counter += 1
    
        self.register_task_completion()

            
    def filter_duplicates(self, og_data): 
        need_insertion = []
        colSQL = s.sql.text("""
            SELECT * FROM chaoss_metric_status
        """)
        values = pd.read_sql(colSQL, self.db)
        for obj in og_data:
            location = values.loc[ (values['cm_name']==obj['cm_name'] ) & ( values['cm_working_group']==obj['cm_working_group'])]
            if not location.empty:
                logging.info("value of tuple exists: " + str(obj['cm_name']))
            else:
                need_insertion.append(obj)
        
        logging.info("While filtering duplicates, we reduced the data size from " + str(len(og_data)) + 
                " to " + str(len(need_insertion)) + "\n")

        return need_insertion
    
    def update_exist_metrics(self, metrics):
        need_update = []
        need_insert = []

        for metric in metrics:
            result = self.db.execute(self.chaoss_metric_status_table.update().where((self.chaoss_metric_status_table.c.cm_name == metric['cm_name'])&(self.chaoss_metric_status_table.c.cm_group == metric['cm_group']) & ((self.chaoss_metric_status_table.c.cm_api_endpoint_repo != metric['cm_api_endpoint_repo']) | (self.chaoss_metric_status_table.c.cm_api_endpoint_rg != metric['cm_api_endpoint_rg'])|(self.chaoss_metric_status_table.c.cm_source != metric['cm_source']))
            ).values(metric))

            if result.rowcount:
                logging.info("Update Metric {}-{}".format(metric['cm_group'], metric['cm_name']))

    def register_task_completion(self):
        task_completed = {
            'worker_id': self.config['id'],
            'job_type': self.working_on,
        }

        logging.info("Telling broker we completed task: " + str(task_completed) + "\n" +
            "This task inserted: " + str(self.results_counter) + " tuples.\n\n")

        requests.post('http://localhost:{}/api/unstable/completed_task'.format(
            self.config['broker_port']), json=task_completed)
        self.results_counter = 0




class FrontendStatusExtractor(object):
    def __init__(self):
        self.api_text = open(os.path.abspath((os.path.dirname(os.path.dirname(os.getcwd()))) + '/frontend/src/AugurAPI.ts'), 'r').read()
        self.attributes = re.findall(
            r'(?:(addRepoMetric|addRepoGroupMetric)\(repo, )\'(.*)\', \'(.*)\'', self.api_text)
        self.endpoints = list(dict.fromkeys(
            [attribute[2] for attribute in self.attributes]))

    def determine_frontend_status(self, metric):
        tag = re.sub('_', '-', metric.tag)
        if tag in self.endpoints:
            metric.frontend_status = 'implemented'
        else:
            metric.frontend_status = 'unimplemented'


class BackendStatusExtractor(object):
    def __init__(self):
        self.api_text = open(os.path.abspath(os.path.dirname(os.path.dirname(os.getcwd())) + '/augur/datasources/augur_db/routes.py'), 'r').read()

        self.attributes = re.findall(
            r'server\.addRepoMetric\([\n]?.*\,\s?\'(.*)\'\)', self.api_text)
                
        self.endpoints = list(dict.fromkeys(
            [attribute for attribute in self.attributes]))

    def determine_backend_status(self, metric):
        tag = re.sub('_', '-', metric.tag)
        if tag in self.endpoints:
            metric.backend_status = 'implemented'
            metric.endpoint_group = '/repo_groups/<repo_group_id>/{}'.format(
                tag)
            metric.endpoint_repo = '/repo_groups/<repo_group_id>/repo/<repo_id>/{}'.format(
                tag)
        else:
            metric.backend_status = 'unimplemented'



class Metric:
    def __init__(self, tag, display_name, focus_area):
        self.tag = tag
        self.display_name = display_name  # cm_name
        self.group = None  # cm_group
        self.source = None  # cm_source
        self.backend_status = 'unimplemented'  # cm_backend_status
        self.frontend_status = 'unimplemented'  # cm_frontend_status
        self.endpoint_group = None  # cm_api_endpoint_rg
        self.endpoint_repo = None  # cm_api_endpoint_repo
        self.html_url = None
        self.defined = False
        self.focus_area = focus_area


class MetricsStatus:
    def __init__(self, github_api):
        self.github = Github(github_api)
        self.repo_groups = [('chaoss/wg-evolution', 'focus_areas'), ('chaoss/wg-diversity-inclusion', 'focus-areas'),
                            ('chaoss/wg-value', 'focus-areas'), ('chaoss/wg-common', 'focus-areas'), ('chaoss/wg-risk', 'focus-areas')]

    def update_metrics(self):
        tag_url_map = {}
        metrics = []
        frontend_extractor = FrontendStatusExtractor()
        beackend_extractor = BackendStatusExtractor()
        # check metric defined or not
        for group in self.repo_groups:
            group_name = re.sub('chaoss/', '',group[0])
            tag_url_map = self.find_defined_metrics(group[0])
            cur_metrics = self.find_metrics_from_focus_area(group[0], group[1])
            for metric in cur_metrics:
                frontend_extractor.determine_frontend_status(metric)
                beackend_extractor.determine_backend_status(metric)
                metric.group = group_name
                if metric.tag in tag_url_map.keys():
                    metric.defined = True
                    metric.html_url = tag_url_map[metric.tag]
                
            metrics.extend(cur_metrics)

        return metrics

    def find_defined_metrics(self, repo_name):
        # return map {tag: html_url}

        repo = self.github.get_repo(repo_name)
        contents = repo.get_contents("")
        md_files = {}
        while len(contents) > 1:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            elif '.md' in file_content.name:
                name = re.sub('.md', '', file_content.name)
                md_files[name.lower()] = file_content.html_url

        return md_files

    def find_metrics_from_focus_area(self, repo_name, focus_area_path):
        focus_areas = self.github.get_repo(
            repo_name).get_dir_contents(focus_area_path)
        metrics = []
        for area in focus_areas:
            # get focus area name from filename
            # focus_area_name = re.sub('.md','',re.sub('-', ' ',area.name))
            focus_area_name = None
            focus_area_name_splited = [a.capitalize() for a in re.sub(
                '.md', '', re.sub('[_]|[-]', ' ', area.name)).split()]
            focus_area_name = ' '.join(focus_area_name_splited)

            # extract structure :focus_area_name/readme.md
            if area.type == 'dir':
                tmp = self.github.get_repo(
                    repo_name).get_dir_contents(area.path)
                readme = [a for a in tmp if 'readme' in a.name.lower()]
                if len(readme) == 0:
                    continue
                else:
                    area = readme[0]
            elif 'readme' in area.name.lower() or 'changelog' in area.name.lower():
                continue

            # decode content; github api return encoded content
            decoded_content = base64.b64decode(area.content).decode('utf-8')
            metric_name_tag = self.parse_table(
                decoded_content) or self.parse_list(decoded_content)

            for name, tag in metric_name_tag.items():
                add_metric = Metric(tag, name,focus_area_name)
                metrics.append(add_metric)

            if metric_name_tag is None:
                continue

        return metrics

    def parse_table(self, md_content):
        # group 0 is header, group 2 is |---|--|, and group 3 is table content
        tables = re.findall(
            r'^(\|?[^\n]+\|[^\n]+\|?\r?\n)((?:\|?\s*:?[-]+\s*:?)+\|?)(\n(?:\|?[^\n]+\|[^\n]+\|?\r?\n?)*)?$', md_content, re.MULTILINE)

        if not tables:
            return None

        box = []
        metrics_name_link = {}
        for table in tables:
            # get metric name by 'metric_name' index in column
            metric_index, length_in_row = self.get_metric_index_in_table_row(
                table[0])
            table_content = [x.strip()
                             for x in table[2].replace('\n', '|').split('|')]
            # remove two empty str
            table_content.pop(0)
            table_content.pop()

            raw_metrics = [table_content[a] for a in range(
                metric_index, len(table_content), length_in_row)]

            for raw_metric in raw_metrics:
                metric_name, metric_link = self.is_has_link(
                    raw_metric, md_content)
                metric_name = re.sub('[\[]|[\]]','', metric_name)
                metrics_name_link[metric_name] = self.link_to_tag(
                    metric_name, str(metric_link))

        return metrics_name_link

    def get_metric_index_in_table_row(self, row):
        header_names = [x.strip().lower() for x in row.split('|')]
        # print(header_names)
        index = None
        if 'metric' in header_names:
            index = header_names.index('metric')
        elif 'name' in header_names:
            index = header_names.index('name')

        return index, len(header_names)

    def parse_list(self, md_content):
        matched_lists = re.findall(r'[-]\s+(.+)\n', md_content)
        metric_names = {}
        # print(matched_lists)
        for matched in matched_lists:
            # print(matched)
            metirc_name = re.sub(r'.+:\s', '', matched)
            metirc_name, metric_link = self.is_has_link(
                metirc_name, md_content)
            metric_name = re.sub('[\[]|[\]]','', metirc_name)
            metric_names[metirc_name] = self.link_to_tag(
                metirc_name, metric_link)
        return metric_names

    def is_has_link(self, s, md_content):
        # remove leading whitespace if exist
        s = s.strip()
        pattern_inline = re.compile(r'\[([^\[\]]+)\]\(([^)]+)')
        match = pattern_inline.match(s)

        if match:
            return match.group(1), match.group(2)

        pattern_ref = re.compile(r'\[([^\[\]]+)\]\[([^]]+)')
        match2 = pattern_ref.match(s)

        if match2:
            link = match2.group(2)
            p = re.compile(r'\n\[' + link + r'\]:\s+(.+)\n')
            res = p.search(md_content, re.DOTALL)
            if res:
                return match2.group(1), res.group(1)
        else:
            return s, 'undefined'

    def link_to_tag(self, name, s):

        # generate tag if undefined metric
        if s == 'undefined':
            return re.sub(' ', '-', name.lower())

        pattern = re.compile(r'\/?([a-zA-Z_-]+)(\.md)?$')
        m = pattern.search(s)
        if m:
            return re.sub('.md', '', m.group(1).lower())
        else:
            return re.sub(' ', '-', name)
