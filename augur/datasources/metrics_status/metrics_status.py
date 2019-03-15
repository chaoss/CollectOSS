#SPDX-License-Identifier: MIT
"""
Analyzes Augur source and CHAOSS repos to determine metric implementation status
"""

import re
import copy
from abc import ABC
import requests
from augur.util import metric_metadata

import pprint
pp = pprint.PrettyPrinter()

class FrontendStatusExtractor(object):

    def __init__(self):
        self.api_text = open("frontend/app/AugurAPI.js", 'r').read()
        self.attributes = re.findall(r'(?:(GitEndpoint|Endpoint|Timeseries)\(repo, )\'(.*)\', \'(.*)\'', self.api_text)
        self.timeseries = [attribute for attribute in self.attributes if attribute[0] == "Timeseries"]
        self.endpoints = [attribute for attribute in self.attributes if attribute[0] == "Endpoint"]
        self.git_endpoints = [attribute for attribute in self.attributes if attribute[0] == "GitEndpoint"]

    def determine_frontend_status(self, metric):
        attribute = None

        if metric.metric_type == "timeseries":
            attribute = next((attribute for attribute in self.timeseries if "/api/unstable/<owner>/<repo>/timeseries/{}".format(attribute[2]) == metric.endpoint), None)

        elif metric.metric_type == "metric":
            attribute = next((attribute for attribute in self.endpoints if "/api/unstable/<owner>/<repo>/{}".format(attribute[2]) == metric.endpoint), None)

        elif metric.metric_type == "git":
            attribute = next((attribute for attribute in self.git_endpoints if "/api/unstable/git/{}".format(attribute[2]) == metric.endpoint), None)

        if attribute is not None:
            metric.frontend_status = 'implemented'
            metric.chart_mapping = attribute[1]
        else:
            metric.frontend_status = 'unimplemented'

class Metric(ABC):

    def __init__(self):
        self.ID = 'none'
        self.tag = 'none'
        self.display_name = 'none'
        self.group = 'none'
        self.backend_status = 'unimplemented'
        self.frontend_status = 'unimplemented'
        self.chart_mapping = "none"
        self.endpoint = 'none'
        self.data_source = 'none'
        self.metric_type = 'none'
        self.documentation_url = '/'
        self.is_defined = 'false'

class GroupedMetric(Metric):

    def __init__(self, raw_name, group):
        Metric.__init__(self)
        self.display_name = re.sub('/', '-', re.sub(r'-$|\*', '', re.sub('-', ' ', raw_name).title()))
        self.tag = re.sub(' ', '-', self.display_name).lower()
        self.ID = re.sub(r'-$|\*', '', self.data_source + '-' + self.tag)
        self.group = group

class ImplementedMetric(Metric):

    def __init__(self, metadata, frontend_status_extractor):
        Metric.__init__(self)

        self.ID = metadata['ID']
        self.tag = metadata['tag']
        self.display_name = metadata['metric_name']
        self.backend_status = 'implemented'
        self.data_source = metadata['source']
        self.group = "experimental"

        if 'metric_type' in metadata:
            self.metric_type = metadata['metric_type']
        else:
            self.metric_type = 'metric'

        if 'endpoint' in metadata:
            self.endpoint = metadata['endpoint']
            frontend_status_extractor.determine_frontend_status(self)

class MetricsStatus(object):

    diversity_inclusion_urls = [
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_communication.md", "has_links": True},
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_contribution.md", "has_links": True},
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_events.md", "has_links": False},
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_governance.md", "has_links": False},
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_leadership.md", "has_links": False},
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_project_places.md", "has_links": True},
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_recognition.md", "has_links": False}
    ]

    growth_maturity_decline_urls = [
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/2_Growth-Maturity-Decline.md", "has_links": True},
    ]

    risk_urls = [
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/3_Risk.md", "has_links": False},
    ]

    value_urls = [
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/4_Value.md", "has_links": False},
    ]

    activity_urls = [
        {"raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/activity-metrics-list.md", "has_links": False},
    ]

    activity_repo = "augurlabs/metrics"

    def __init__(self, githubapi):
        self.__githubapi = githubapi.api

        #TODO: don't hardcode this
        self.groups = {
            "diversity-inclusion": "Diversity and Inclusion",
            "growth-maturity-decline": "Growth, Maturity, and Decline",
            "risk": "Risk",
            "value": "Value",
            "activity": "Activity",
            "experimental": "Experimental",
            "all": "All"
        }

        self.implemented_metrics = []

        self.diversity_inclusion_metrics = []
        self.growth_maturity_decline_metrics = []
        self.risk_metrics = []
        self.value_metrics = []
        self.activity_metrics = []

        self.metrics_by_group = []

        self.metrics_status = []

        self.data_sources = []
        self.metric_types = []
        self.tags = {}
        self.metadata = []

    def create_metrics_status(self):

        self.build_implemented_metrics()

        self.diversity_inclusion_metrics = self.create_grouped_metrics(self.diversity_inclusion_urls, "diversity-inclusion")
        self.growth_maturity_decline_metrics = self.create_grouped_metrics(self.growth_maturity_decline_urls, "growth-maturity-decline")
        self.risk_metrics = self.create_grouped_metrics(self.risk_urls, "risk")
        self.value_metrics = self.create_grouped_metrics(self.value_urls, "value")

        self.metrics_by_group = [self.diversity_inclusion_metrics, self.growth_maturity_decline_metrics, self.risk_metrics, self.value_metrics]

        self.activity_metrics = self.create_activity_metrics()
        self.metrics_by_group.append(self.activity_metrics)

        self.create_experimental_metrics()
        self.metrics_by_group.append(self.experimental_metrics)

        self.copy_implemented_metrics()

        self.find_defined_metrics()

        self.build_metrics_status()

        self.build_metadata()

    def build_implemented_metrics(self):
        frontend_status_extractor = FrontendStatusExtractor()
        for metric in metric_metadata:
            if "ID" in metric.keys():
                self.implemented_metrics.append(ImplementedMetric(metric, frontend_status_extractor))

    def extract_grouped_metric_names(self, remote):
        metric_file = requests.get(remote["raw_content_url"]).text

        reg_ex_pattern = r'^(?!Name)(.*[^-])(?:\ \|)'
        if remote["has_links"]:
            reg_ex_pattern = r'\[(.*?)\]\((?:.*?\.md)\)'
        return re.findall(reg_ex_pattern, metric_file, re.M)

    def create_grouped_metrics(self, remotes_list, group):
        remote_names = []

        for remote in remotes_list:
            for name in self.extract_grouped_metric_names(remote):
                remote_names.append(name)

        remote_metrics = []

        for name in remote_names:
            remote_metrics.append(GroupedMetric(name, group))

        return remote_metrics

    def create_activity_metrics(self):
        activity_metrics_raw_text = requests.get(self.activity_urls[0]["raw_content_url"]).text

        raw_activity_names = re.findall(r'\|(?:\[|)(.*)\|(?:\]|)(?:\S| )', activity_metrics_raw_text)

        activity_names = [re.sub(r'(?:\]\(.*\))', '', name) for name in raw_activity_names if '---' not in name and 'Name' not in name]

        activity_metrics = []

        for raw_name in activity_names:
            activity_metric = GroupedMetric(raw_name, "activity")

            tags = []

            for group in self.metrics_by_group:
                for grouped_metric in group:
                    tags.append(grouped_metric.tag)

                is_not_grouped_metric = False
                if activity_metric.tag in tags:
                    is_not_grouped_metric = True

            if is_not_grouped_metric:
                activity_metrics.append(activity_metric)

        return activity_metrics

    def create_experimental_metrics(self):
        tags = []
        for group in self.metrics_by_group:
            for metric in group:
                tags.append(metric.tag)

        self.experimental_metrics = [metric for metric in self.implemented_metrics if metric.tag not in tags]

    def copy_implemented_metrics(self):
        # takes implemented metrics and copies their data to the appropriate metric object
        # I am so very sorry
        # TODO: burn this into the ground
        for group in enumerate(self.metrics_by_group):
            if group[1] is not self.experimental_metrics:
                for grouped_metric in group[1]:
                    defined_implemented_metrics = [metric for metric in self.implemented_metrics if grouped_metric.tag == metric.tag]
                    if defined_implemented_metrics != []:
                        for metric in defined_implemented_metrics:
                            metric.group = group[1][0].group
                            group[1].append(metric)
                            self.implemented_metrics.remove(metric)
                        grouped_metric.ID = 'n/a'
                self.metrics_by_group[group[0]] = [metric for metric in group[1] if metric.ID != 'n/a']

    def find_defined_metrics(self):
        activity_files = self.__githubapi.get_repo(self.activity_repo).get_dir_contents("activity-metrics")
        defined_tags = [re.sub(".md", '', file.name) for file in activity_files]

        for group in self.metrics_by_group:
            for metric in group:
                if metric.tag in defined_tags:
                    metric.is_defined = 'true'
                    metric.documentation_url = "https://github.com/{}/blob/wg-gmd/activity-metrics/{}.md".format(MetricsStatus.activity_repo, metric.tag)

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
