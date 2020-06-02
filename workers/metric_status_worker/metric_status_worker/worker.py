import base64
import logging
import os
import re
import sys
import json
import time
from abc import ABC
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse

import pandas as pd
import requests
import sqlalchemy as s
from github import Github
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from workers.worker_base import Worker

class MetricStatusWorker(Worker):
    def __init__(self, config, task=None):
        given = [['git_url']]
        models = ['chaoss_metric_status']

        data_tables = ['chaoss_metric_status']
        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(config, given, models, data_tables, operations_tables)

        # These 3 are included in every tuple the worker inserts (data collection info)
        self.tool_source = 'Metric Status Worker'
        self.tool_version = '0.0.1'
        self.data_source = 'GitHub API'

    def chaoss_metric_status_model(self, entry_info, repo_id):
        """ Data colletction function
        Query the github api for metric status
        """
        status = MetricsStatus(self.API_KEY)
        status.create_metrics_status()
        metrics = status.metrics_status

    # convert to dict
        dict_metrics = []
        for metric in metrics:
            metric_info = {
                'cm_group': metric['group'],
                'cm_source': metric['data_source'],
                'cm_type': metric['metric_type'],
                'cm_backend_status': metric['backend_status'],
                'cm_frontend_status': metric['frontend_status'],
                'cm_api_endpoint_repo': metric['endpoint_repo'],
                'cm_api_endpoint_rg': metric['endpoint_group'],
                'cm_defined': metric['is_defined'],
                'cm_name': metric['display_name'],
                'cm_working_group': metric['group'],
                'cm_info':  metric['tag'],
                'cm_working_group_focus_area': metric['focus_area'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
            }
            dict_metrics.append(metric_info)

        need_insertion = self.filter_duplicates({'cm_api_endpoint_repo': "cm_api_endpoint_repo", 'cm_backend_status':'cm_api_endpoint_rg'}, ['chaoss_metric_status'],
                                                dict_metrics)
        logging.info("Count of contributors needing insertion: " + str(len(need_insertion)) + "\n")
        for metric in need_insertion:
            result = self.db.execute(self.chaoss_metric_status_table.insert().values(metric))
            logging.info("Primary key inserted into the metrics table: " + str(result.inserted_primary_key))
            self.results_counter += 1

        register_task_completion(self, entry_info, repo_id, 'chaoss_metric_status')


    def update_exist_metrics(self, metrics):
        need_update = []
        need_insert = []

        for metric in metrics:
            result = self.db.execute(self.chaoss_metric_status_table.update().where((self.chaoss_metric_status_table.c.cm_name == metric['cm_name'])&(self.chaoss_metric_status_table.c.cm_group == metric['cm_group']) & ((self.chaoss_metric_status_table.c.cm_api_endpoint_repo != metric['cm_api_endpoint_repo']) | (self.chaoss_metric_status_table.c.cm_api_endpoint_rg != metric['cm_api_endpoint_rg'])|(self.chaoss_metric_status_table.c.cm_source != metric['cm_source']))
            ).values(metric))

            if result.rowcount:
                logging.info("Update Metric {}-{}".format(metric['cm_group'], metric['cm_name']))


class FrontendStatusExtractor(object):

    def __init__(self):
        pass
        self.api_text = open(os.path.abspath(os.path.dirname(os.path.dirname(os.getcwd()))) +
                             "/frontend/src/AugurAPI.ts", 'r').read()
        self.attributes = re.findall(
            r'(?:(GitEndpoint|Endpoint|Timeseries|addRepoMetric|addRepoGroupMetric)\()\'(.*)\', \'(.*)\'',
            self.api_text)
        self.timeseries = [
            attribute for attribute in self.attributes if attribute[0] == "Timeseries"]
        self.endpoints = [
            attribute for attribute in self.attributes if attribute[0] == "Endpoint"]
        self.git_endpoints = [
            attribute for attribute in self.attributes if attribute[0] == "GitEndpoint"]
        self.repo_metrics = [
            attribute for attribute in self.attributes if attribute[0] == 'addRepoMetric']
        self.group_metric = [
            attribute for attribute in self.attributes if attribute[0] == 'addRepoMetric']

    def determine_frontend_status(self, metric):
        metric.frontend_status = 'unimplemented'
        attribute = None

        if metric.metric_type == "timeseries":
            attribute = next((attribute for attribute in self.timeseries if
                              "/api/unstable/<owner>/<repo>/timeseries/{}".format(attribute[2]) == metric.endpoint_repo),
                             None)

        elif metric.metric_type == "metric":
            attribute = next((attribute for attribute in self.endpoints if
                              "/api/unstable/<owner>/<repo>/{}".format(attribute[2]) == metric.endpoint_repo), None)
            if not attribute:
                attribute = next((attribute for attribute in self.repo_metrics if
                              "/api/unstable/repo-groups/<repo_group_id>/repos/<repo_id>/{}".format(
                                  attribute[2]) == metric.endpoint_repo), None)
            if not attribute and metric.endpoint_group:
                attribute = next((attribute for attribute in self.repo_metrics if
                              "/api/unstable/repo-groups/<repo_group_id>/{}".format(attribute[2]) == metric.endpoint_group), None)

        elif metric.metric_type == "git":
            attribute = next((attribute for attribute in self.git_endpoints if
                              "/api/unstable/git/{}".format(attribute[2]) == metric.endpoint_repo), None)

        if attribute is not None:
            metric.frontend_status = 'implemented'
            metric.chart_mapping = attribute[1]
        else:
            metric.frontend_status = 'unimplemented'


class Metric(ABC):

    def __init__(self):
        self.ID = None
        self.tag = None
        self.display_name = None
        self.group = None
        self.backend_status = 'unimplemented'
        self.frontend_status = 'unimplemented'
        self.chart_mapping = None
        self.data_source = None
        self.metric_type = None
        self.documentation_url = None
        self.is_defined = False
        self.focus_area = None
        self.endpoint_group = None
        self.endpoint_repo = None


class GroupedMetric(Metric):

    def __init__(self, display_name, group, tag, focus_area):
        Metric.__init__(self)
        self.display_name = display_name
        self.tag = tag
        self.ID = re.sub(r'-$|\*', '', 'none' + '-' + self.tag)
        self.group = group
        self.focus_area = focus_area


class ImplementedMetric(Metric):

    def __init__(self, metadata, frontend_status_extractor):
        Metric.__init__(self)

        self.ID = metadata['ID']
        self.tag = metadata['tag']
        self.display_name = metadata['metric_name']
        self.backend_status = 'implemented'
        self.data_source = metadata['source']
        self.group = "experimental"
        self.endpoint_group = None
        self.endpoint_repo = None


        if 'metric_type' in metadata:
            self.metric_type = metadata['metric_type']
        else:
            self.metric_type = 'metric'

        if 'endpoint' in metadata:
            if 'group_endpoint' in metadata:
                self.endpoint_group = metadata['group_endpoint']
            if 'repo_endpoint' in metadata:
                self.endpoint_repo = metadata['repo_endpoint']
            else:
                self.endpoint_repo = metadata['endpoint']
            frontend_status_extractor.determine_frontend_status(self)


class MetricsStatus(object):
    wg_evolution = {
        "repo": "chaoss/wg-evolution",
        "focus_area": "focus_areas",
        "name": 'evolution'
    }

    wg_diversity_inclusion = {
        "repo": "chaoss/wg-diversity-inclusion",
        "focus_area": "focus-areas",
        "name": "diversity-inclusion"
    }

    wg_value = {
        "repo": "chaoss/wg-value",
        "focus_area": 'focus-areas',
        "name": "value"
    }

    wg_common = {
        "repo": "chaoss/wg-common",
        "focus_area": "focus-areas",
        "name": "common"
    }

    wg_risk = {
        "repo": "chaoss/wg-risk",
        "focus_area": "focus-areas",
        "name": "risk"
    }

    def __init__(self, githubapi):
        self.__githubapi = githubapi
        self.github = Github(self.__githubapi)

        # TODO: don't hardcode this
        self.groups = {
            "evolution": "Evolution",
            "diversity-inclusion": "Diversity and Inclusion metrics",
            "value": "Value",
            "risk": "Risk",
            "common": "Common",
            "experimental": "Experimental",
            "all": "All"
        }

        self.implemented_metrics = []

        self.evo_metrics = []
        self.di_metrics = []
        self.risk_metrics = []
        self.value_metrics = []
        self.common_metrics = []
        self.experimental_metrics = []

        self.metrics_by_group = []

        self.metrics_status = []

        self.data_sources = []
        self.metric_types = []
        self.tags = {}
        self.metadata = []

    def create_metrics_status(self):

        self.build_implemented_metrics()

        self.evo_metrics = self.create_grouped_metrics(
            self.wg_evolution, "evolution")
        self.risk_metrics = self.create_grouped_metrics(self.wg_risk, "risk")
        self.common_metrics = self.create_grouped_metrics(
            self.wg_common, 'common')
        self.di_metrics = self.create_grouped_metrics(
            self.wg_diversity_inclusion, 'diversity-inclusion')
        self.value_metrics = self.create_grouped_metrics(
            self.wg_value, 'value')

        self.metrics_by_group = [self.evo_metrics, self.risk_metrics,
                                 self.common_metrics, self.di_metrics, self.value_metrics]

        self.create_experimental_metrics()
        self.metrics_by_group.append(self.experimental_metrics)
        #
        self.copy_implemented_metrics()

        self.find_defined_metrics()

        self.build_metrics_status()

        # self.build_metadata()

    def build_implemented_metrics(self):
        frontend_status_extractor = FrontendStatusExtractor()

        r = requests.get(
            url='http://{}:{}/api/unstable/batch/metadata'.format(
                self.config['broker_host'],self.config['broker_port']))
        data = json.loads(r.text)

        for metric in data:
            if "ID" in metric.keys():
                self.implemented_metrics.append(
                    ImplementedMetric(metric, frontend_status_extractor))

    def create_grouped_metrics(self, group, group_name):
        metrics = self.find_metrics_from_focus_area(
            group['repo'], group['focus_area'])

        remote_metrics = []
        for metric in metrics:
            remote_metrics.append(GroupedMetric(metric.display_name, group['name'], metric.tag,
                                                metric.focus_area))

        return remote_metrics

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
                add_metric = Metric()
                add_metric.display_name = name
                add_metric.tag = tag
                add_metric.focus_area = focus_area_name

                metrics.append(add_metric)

            if metric_name_tag is None:
                continue

        return metrics

    def parse_table(self, md_content):
        # group 0 is header, group 2 is |---|--|, and group 3 is table content
        tables = re.findall(
            r'^(\|?[^\n]+\|[^\n]+\|?\r?\n)((?:\|?\s*:?[-]+\s*:?)+\|?)(\n(?:\|?[^\n]+\|[^\n]+\|?\r?\n?)*)?$', md_content,
            re.MULTILINE)

        if not tables:
            return None

        box = []
        metrics_name_tag = {}
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
                metric_name = re.sub('[\[]|[\]]', '', metric_name)
                if not metric_link:
                    metric_link = re.sub(' ', '-', metric_name).lower()
                metrics_name_tag[metric_name] = self.link_to_tag(
                    metric_name, str(metric_link))

        return metrics_name_tag

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
            metirc_name = re.sub('[\[]|[\]]', '', metirc_name)
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
            return s, None

    def link_to_tag(self, name, s):

        # generate tag if undefined metric
        if not s:
            return re.sub(' ', '-', name.lower())

        pattern = re.compile(r'\/?([a-zA-Z_-]+)(\.md)?$')
        m = pattern.search(s)
        if m:
            return re.sub('_', '-', re.sub('.md', '', m.group(1).lower()))
        else:
            return re.sub(' ', '-', re.sub('\(s\)', 's', name))

    def create_experimental_metrics(self):
        tags = []
        for group in self.metrics_by_group:
            for metric in group:
                tags.append(metric.tag)

        self.experimental_metrics = [
            metric for metric in self.implemented_metrics if metric.tag not in tags]

    def copy_implemented_metrics(self):
        # takes implemented metrics and copies their data to the appropriate metric object
        # I am so very sorry
        # TODO: burn this into the ground
        for group in enumerate(self.metrics_by_group):
            if group[1] is not self.experimental_metrics:
                for grouped_metric in group[1]:
                    defined_implemented_metrics = [
                        metric for metric in self.implemented_metrics if grouped_metric.tag == metric.tag]
                    if defined_implemented_metrics != []:
                        for metric in defined_implemented_metrics:
                            metric.group = group[1][0].group
                            metric.focus_area = grouped_metric.focus_area
                            group[1].append(metric)
                            self.implemented_metrics.remove(metric)
                        grouped_metric.ID = 'n/a'
                self.metrics_by_group[group[0]] = [
                    metric for metric in group[1] if metric.ID != 'n/a']

    def find_defined_metrics(self):
        # return map {tag: html_url}
        repo_names = [self.wg_common['repo'], self.wg_evolution['repo'],
                      self.wg_diversity_inclusion['repo'], self.wg_risk['repo'], self.wg_value['repo']]

        md_files = {}

        for repo_name in repo_names:
            repo = self.github.get_repo(repo_name)
            contents = repo.get_contents("")

            while len(contents) > 1:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                elif '.md' in file_content.name:
                    name = re.sub(
                        '_', '-', re.sub('.md', '', file_content.name))
                    md_files[name.lower()] = file_content.html_url

        for group in self.metrics_by_group:
            for metric in group:
                if metric.tag in md_files.keys():
                    metric.is_defined = True
                    metric.documentation_url = md_files[metric.tag]

    def build_metrics_status(self):
        for group in self.metrics_by_group:
            for metric in group:
                self.metrics_status.append(metric.__dict__)

    def build_metadata(self):
        self.get_metric_sources()
        self.get_metric_types()
        self.get_metric_tags()

        self.metadata = {
            "remotes": {
                "diversity_inclusion_urls": self.diversity_inclusion_urls,
                "growth_maturity_decline_urls": self.growth_maturity_decline_urls,
                "risk_urls": self.risk_urls,
                "value_urls": self.value_urls,
                "activity_repo_urls": self.activity_urls
            },
            "groups": self.groups,
            "data_sources": self.data_sources,
            "metric_types": self.metric_types,
            "tags": self.tags
        }

    def get_metric_sources(self):
        for data_source in [metric['data_source'] for metric in self.metrics_status]:
            data_source = data_source.lower()
            if data_source not in self.data_sources and data_source != "none":
                self.data_sources.append(data_source)
        self.data_sources.append("all")

    def get_metric_types(self):
        for metric_type in [metric['metric_type'] for metric in self.metrics_status]:
            metric_type = metric_type.lower()
            if metric_type not in self.metric_types and metric_type != "none":
                self.metric_types.append(metric_type)
        self.metric_types.append("all")

    def get_metric_tags(self):
        for tag in [(metric['tag'], metric['group']) for metric in self.metrics_status]:
            # tag[0] = tag[0].lower()
            if tag[0] not in [tag[0] for tag in self.tags] and tag[0] != "none":
                self.tags[tag[0]] = tag[1]