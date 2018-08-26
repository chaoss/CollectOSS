#SPDX-License-Identifier: MIT
"""
Analyzes Augur source and CHAOSS repos to determine metric implementation status
"""

import re
import json
import glob
import requests
from augur.util import metric_metadata

class FrontendStatusExtractor(object):

	def __init__(self):
		self.api_text =  open("frontend/app/AugurAPI.js", 'r').read()
		self.attributes = re.findall(r'(?:(GitEndpoint|Endpoint|Timeseries)\(repo, )\'(.*)\', \'(.*)\'', self.api_text)
		self.timeseries_attributes = [attribute for attribute in self.attributes if attribute[0] == "Timeseries"]
		self.endpoint_attributes = [attribute for attribute in self.attributes if attribute[0] == "Endpoint"]
		self.git_endpoint_attributes = [attribute for attribute in self.attributes if attribute[0] == "GitEndpoint"]
		
	def determine_frontend_status(self, endpoint, metric_type):
		attribute = None

		if metric_type is "timeseries":
			attribute = next((attribute[1] for attribute in self.timeseries_attributes if attribute[2] in endpoint), None)

		elif metric_type is "metric":
			attribute = next((attribute[1] for attribute in self.endpoint_attributes if attribute[2] in endpoint), None)

		elif metric_type is "git":
			attribute = next((attribute[1] for attribute in self.git_endpoint_attributes if attribute[2] in endpoint), None)

		if attribute is not None:
			status = 'implemented'
		else:
			status = 'unimplemented'

		return status

class Metric(object):

	def __init__(self):
		self.ID = 'none'
		self.tag = 'none'
		self.name = 'none'
		self.group = 'none'
		self.backend_status = 'unimplemented'
		self.frontend_status = 'unimplemented'
		self.endpoint = 'none'
		self.source = 'none'
		self.metric_type = 'none'
		self.url = '/'
		self.is_defined = 'false'

class GroupedMetric(Metric):

	def __init__(self, raw_name, group):
		Metric.__init__(self)	
		self.name = re.sub('/', '-', re.sub(r'-$|\*', '', re.sub('-', ' ', raw_name).title()))
		self.tag = re.sub(' ', '-', self.name).lower()
		self.ID = re.sub(r'-$|\*', '', self.source + '-' + self.tag)
		self.group = group

class ImplementedMetric(Metric):

	def __init__(self, metadata, frontend_status_extractor):
		Metric.__init__(self)	

		self.ID = metadata['ID']
		self.tag = metadata['tag']
		self.name = metadata['metric_name']
		self.backend_status = 'implemented'
		self.source = metadata['source']
		self.group = "experimental"

		if 'metric_type' in metadata:
			self.metric_type = metadata['metric_type']
		else:
			self.metric_type = 'metric'

		if 'endpoint' in metadata:
			self.endpoint = metadata['endpoint']
			self.frontend_status = frontend_status_extractor.determine_frontend_status(self.endpoint, self.metric_type)

class MetricsStatus(object):

	diversity_inclusion_urls = [
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_communication.md", "has_links": True },
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_contribution.md", "has_links": True },
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_events.md", "has_links": False },
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_governance.md", "has_links": False },
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_leadership.md", "has_links": False },
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_project_places.md", "has_links": True },
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/goal_recognition.md", "has_links": False }
	]	

	growth_maturity_decline_urls = [
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/2_Growth-Maturity-Decline.md", "has_links": True },
	]

	risk_urls = [
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/3_Risk.md", "has_links": False },
	]

	value_urls = [
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/4_Value.md", "has_links": False },
	]

	activity_urls = [
		{ "raw_content_url": "https://raw.githubusercontent.com/augurlabs/metrics/wg-gmd/activity-metrics-list.md", "has_links": False },
	]

	activity_repo = "augurlabs/metrics"

	def __init__(self, githubapi):
		self.__githubapi = githubapi.api

		self.groups = {
	        "diversity-inclusion": "Diversity and Inclusion",
	        "growth-maturity-decline": "Growth, Maturity, and Decline",
	        "risk": "Risk",
	        "value": "Value",
	        "activity": "Activity",
	        "experimental": "Experimental",
	        "all": "All"
	    },

		self.sources = []
		self.metric_types = []
		self.tags = {}

		self.implemented_metrics = []

		self.raw_metrics_status = []
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

		self.get_raw_metrics_status()

		self.get_metadata()

	def build_implemented_metrics(self):
		frontend_status_extractor = FrontendStatusExtractor()
		for metric in metric_metadata:
			if "ID" in metric.keys():
				self.implemented_metrics.append(ImplementedMetric(metric, frontend_status_extractor))

	def extract_grouped_metric_names(self, remote):
		metric_file = requests.get(remote["raw_content_url"]).text

		regEx = r'^(?!Name)(.*[^-])(?:\ \|)'
		if remote["has_links"] == True:
			regEx = r'\[(.*?)\]\((?:.*?\.md)\)'

		return re.findall(regEx, metric_file, re.M)

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
			metric = GroupedMetric(raw_name, "activity")

			is_grouped_metric = True
			for group in self.metrics_by_group:
				if metric.tag not in [metric.tag for metric in group]:
					is_grouped_metric = False

			if is_grouped_metric == False:
				activity_metrics.append(metric)

		return activity_metrics

	def create_experimental_metrics(self):
		tags = []
		for group in self.metrics_by_group:
			for metric in group:
				tags.append(metric.tag)

		self.experimental_metrics = [metric for metric in self.implemented_metrics if metric.tag not in tags]

	def copy_implemented_metrics(self):
		# takes implemented metrics and copies their data to the appropriate metric object
		# I'm sorry
		implemented_metric_tags = [metric.tag for metric in self.implemented_metrics]
		for group in self.metrics_by_group:
			if group is not self.experimental_metrics: #experimental metrics don't need to be copied, since they don't have a definition
				for grouped_metric in group:
					if grouped_metric.tag in implemented_metric_tags:
						metric = next(metric for metric in self.implemented_metrics if metric.tag == grouped_metric.tag)
						for key in metric.__dict__.keys():
							if key != 'group': #don't copy the group over, since the metrics are already grouped
								grouped_metric.__dict__[key] = metric.__dict__[key]

	def find_defined_metrics(self):
		activity_files = self.__githubapi.get_repo(self.activity_repo).get_dir_contents("activity-metrics")
		defined_tags = [re.sub(".md", '', file.name) for file in activity_files]

		for group in self.metrics_by_group:
			for metric in group:
				if metric.tag in defined_tags:
					metric.is_defined = 'true'
					metric.url = "https://github.com/{}/blob/wg-gmd/activity-metrics/{}.md".format(MetricsStatus.activity_repo, metric.tag)

	def get_raw_metrics_status(self):
		for group in self.metrics_by_group:
			for metric in group:
				self.raw_metrics_status.append(metric.__dict__)

	def get_metadata(self):
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
			"sources": self.sources,
			"metric_types": self.metric_types,
			"tags": self.tags
		}

	def get_metric_sources(self):
		for source in [metric['source'] for metric in self.raw_metrics_status]:
			source = source.lower()
			if source not in self.sources and source != "none":
				self.sources.append(source)
		self.sources.append("all")

	def get_metric_types(self):
		for metric_type in [metric['metric_type'] for metric in self.raw_metrics_status]:
			metric_type = metric_type.lower()
			if metric_type not in self.metric_types and metric_type != "none":
				self.metric_types.append(metric_type) 
		self.metric_types.append("all")

	def get_metric_tags(self):
		for tag in [(metric['tag'], metric['group']) for metric in self.raw_metrics_status]:
			# tag[0] = tag[0].lower()
			if tag[0] not in [tag[0] for tag in self.tags] and tag[0] != "none":
				self.tags[tag[0]] = tag[1]
