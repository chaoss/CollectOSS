import re
import json
import glob
import requests
from augur.util import metric_metadata

class FrontendStatusExtractor(object):
	def __init__(self):
		self.api_text =  open("frontend/app/AugurAPI.js", 'r').read()
		self.frontend_card_files = []
		self.endpoint = ""
		self.timeseries_attributes = re.findall(r'(?:(Timeseries)\(repo, )\'(.*)\', \'(.*)\'', self.api_text)
		self.endpoint_attributes = re.findall(r'(?:(Endpoint)\(repo, )\'(.*)\', \'(.*)\'', self.api_text)
		self.git_attributes = re.findall(r'(?:(GitEndpoint)\(repo, )\'(.*)\', \'(.*)\'', self.api_text)
		
	def determineFrontendStatus(self, endpoint):

		attribute = ''

		if '/api/unstable/<owner>/<repo>/timeseries/' in endpoint:
			endpoint_attributes = self.timeseries_attributes
			attribute = [attribute[1] for attribute in endpoint_attributes if '/api/unstable/<owner>/<repo>/timeseries/' + attribute[2] == endpoint]

		elif '/api/unstable/<owner>/<repo>/' in endpoint:
			endpoint_attributes = self.endpoint_attributes
			attribute = [attribute[1] for attribute in endpoint_attributes if '/api/unstable/<owner>/<repo>/' + attribute[2] == endpoint]

		elif '/api/unstable/git/' in endpoint:
			endpoint_attributes = self.git_attributes
			attribute = [attribute[1] for attribute in endpoint_attributes if '/api/unstable/git/' + attribute[2] == endpoint]

		status = 'unimplemented'
		if len(attribute) != 0 and attribute[0] in self.api_text:
			status = 'implemented'

		return status

class Metric(object):

	def __init__(self):
		self.ID = 'none'
		self.tag = 'none'
		self.name = 'none'
		self.group = 'none'
		self.backend_status = 'undefined'
		self.frontend_status = 'unimplemented'
		self.endpoint = 'none'
		self.source = 'none'
		self.metric_type = 'none'
		self.url = '/'
		self.is_defined = 'false'

class GroupedMetric(Metric):
	
	def __init__(self, raw_name, group, defined_tags):
		Metric.__init__(self)	
		self.name = re.sub('/', '-', re.sub(r'-$|\*', '', re.sub('-', ' ', raw_name).title()))
		self.tag = re.sub(' ', '-', self.name).lower()
		self.ID = self.source + '-' + self.tag 
		self.group = group

		if self.tag in defined_tags:
			self.is_defined = 'true'
			self.url = 'activity-metrics/' + self.tag + '.md'
			self.backend_status = 'unimplemented'

class ImplementedMetric(Metric):

	frontend_status_extractor = FrontendStatusExtractor()

	def __init__(self, metadata, defined_tags):
		Metric.__init__(self)	

		self.ID = metadata['ID']
		self.tag = metadata['tag']
		self.name = metadata['metric_name']
		self.group = metadata['group']
		self.backend_status = 'implemented'
		self.endpoint = metadata['endpoint']
		self.frontend_status = self.frontend_status_extractor.determineFrontendStatus(self.endpoint)
		self.source = metadata['source']

		if 'metric_type' in metadata:
			self.metric_type = metadata['metric_type']
		else:
			self.metric_type = 'metric'

		if self.tag in defined_tags:
			self.url = 'activity-metrics/' + self.tag + '.md'
			self.is_defined = 'true'

class MetricsStatus(object):

	diversity_inclusion_remotes = [
		{ "remote_url": "https://raw.githubusercontent.com/chaoss/wg-diversity-inclusion/master/goal_communication.md", "has_links": True },
		{ "remote_url": "https://raw.githubusercontent.com/chaoss/wg-diversity-inclusion/master/goal_contribution.md", "has_links": True },
		{ "remote_url": "https://raw.githubusercontent.com/chaoss/wg-diversity-inclusion/master/goal_events.md", "has_links": False },
		{ "remote_url": "https://raw.githubusercontent.com/chaoss/wg-diversity-inclusion/master/goal_governance.md", "has_links": False },
		{ "remote_url": "https://raw.githubusercontent.com/chaoss/wg-diversity-inclusion/master/goal_leadership.md", "has_links": False },
		{ "remote_url": "https://raw.githubusercontent.com/chaoss/wg-diversity-inclusion/master/goal_project_places.md", "has_links": True },
		{ "remote_url": "https://raw.githubusercontent.com/chaoss/wg-diversity-inclusion/master/goal_recognition.md", "has_links": False }
	]	

	growth_maturity_decline_remotes = [
		{ "remote_url": "https://raw.githubusercontent.com/OSSHealth/wg-gmd/master/2_Growth-Maturity-Decline.md", "has_links": True },
	]

	risk_remotes = [
		{ "remote_url": "https://raw.githubusercontent.com/OSSHealth/wg-gmd/master/3_Risk.md", "has_links": False },
	]

	value_remotes = [
		{ "remote_url": "https://raw.githubusercontent.com/OSSHealth/wg-gmd/master/4_Value.md", "has_links": False },
	]

	def __init__(self, githubapi):
		self.__githubapi = githubapi.api

		self.groups = []
		self.sources = []
		self.metric_types = []

		self.defined_tags = []
		self.implemented_metrics = []

		self.raw_metrics_status = []
		self.metrics_status_with_metadata = []

	def create_metrics_status(self):
		self.activity_repo_remote = "OSSHealth/wg-gmd"

		self.getDefinedMetricTags()

		self.buildImplementedMetrics()

		self.diversity_inclusion_metrics = self.createGroupedMetricsFromListOfRemotes(self.diversity_inclusion_remotes, "diversity-inclusion")
		self.growth_maturity_decline_metrics = self.createGroupedMetricsFromListOfRemotes(self.growth_maturity_decline_remotes, "growth-maturity-decline")
		self.risk_metrics = self.createGroupedMetricsFromListOfRemotes(self.risk_remotes, "risk")
		self.value_metrics = self.createGroupedMetricsFromListOfRemotes(self.value_remotes, "value")

		self.metrics_by_group = [self.diversity_inclusion_metrics, self.growth_maturity_decline_metrics, self.risk_metrics, self.value_metrics]

		self.activity_metrics = self.createActivityMetrics()
		self.metrics_by_group.append(self.activity_metrics)

		self.experimental_metrics = [metric for metric in self.implemented_metrics if metric.group == "experimental"]
		self.metrics_by_group.append(self.experimental_metrics)

		self.copyImplementedMetrics()

		self.getRawMetricsStatus()
		self.getMetricsStatusWithMetadata()

		self.getMetricGroups()
		self.getMetricSources()
		self.getMetricTypes()

	# implemented metrics
	def copyImplementedMetrics(self):
		# takes implemented metrics and copies their data to the appropriate metric object
		# I'm sorry
		implemented_metric_tags = [metric.tag for metric in self.implemented_metrics]
		for group in self.metrics_by_group:
			if group is not self.experimental_metrics: #experimental metrics don't need to be copied, since they don't have a definition
				for grouped_metric in group:
					if grouped_metric.tag in implemented_metric_tags:
						metric = next(metric for metric in self.implemented_metrics if metric.tag == grouped_metric.tag)
						grouped_metric.__dict__ = metric.__dict__.copy()

	def buildImplementedMetrics(self):
		for metric in metric_metadata:
			if "ID" in metric.keys():
				self.implemented_metrics.append(ImplementedMetric(metric, self.defined_tags))

	# grouped metrics
	def extractGroupedMetricNamesFromRemoteFile(self, remote):

		metric_file = requests.get(remote["remote_url"]).text

		regEx = r'^(?!Name)(.*[^-])(?:\ \|)'
		if remote["has_links"] == True:
			regEx = r'\[(.*?)\]\((?:.*?\.md)\)'

		return re.findall(regEx, metric_file, re.M)

	def createGroupedMetricsFromListOfRemotes(self, remotes_list, group):
		
		remote_names = []

		for remote in remotes_list:
			for name in self.extractGroupedMetricNamesFromRemoteFile(remote):
				remote_names.append(name)

		remote_metrics = []

		for name in remote_names:
			remote_metrics.append(GroupedMetric(name, group, self.defined_tags))

		return remote_metrics

	# activity metrics
	def extractActivityMetricNames(self):

		activity_metrics_raw_text = requests.get("https://raw.githubusercontent.com/{}/master/activity-metrics-list.md".format(self.activity_repo_remote)).text

		raw_activity_names = re.findall(r'\|(?:\[|)(.*)\|(?:\]|)(?:\S| )', activity_metrics_raw_text)

		return [re.sub(r'(?:\]\(.*\))', '', name) for name in raw_activity_names if '---' not in name and 'Name' not in name]

	def createActivityMetrics(self):

		activity_names = self.extractActivityMetricNames()
		activity_metrics = []

		for raw_name in activity_names:
			metric = GroupedMetric(raw_name, "activity", self.defined_tags)

			isUngroupedMetric = False
			for group in self.metrics_by_group:
				if metric.tag in [metric.tag for metric in group]:
					isUngroupedMetric = True

			if isUngroupedMetric == False:
				activity_metrics.append(metric)

		return activity_metrics

	# other
	def getDefinedMetricTags(self):

		activity_files = self.__githubapi.get_repo(self.activity_repo_remote).get_dir_contents("activity-metrics")
		self.defined_tags = []

		for file in activity_files:
			self.defined_tags.append(re.sub(".md", '', file.name))

	def getMetricGroups(self):
		for group in [metric['group'] for metric in self.raw_metrics_status]:
			group = group.lower()
			if group not in self.groups and group != "none":
				self.groups.append(group) 

	def getMetricSources(self):
		for source in [metric['source'] for metric in self.raw_metrics_status]:
			source = source.lower()
			if source not in self.sources and source != "none":
				self.sources.append(source)

	def getMetricTypes(self):
		for metric_type in [metric['metric_type'] for metric in self.raw_metrics_status]:
			metric_type = metric_type.lower()
			if metric_type not in self.metric_types and metric_type != "none":
				self.metric_types.append(metric_type) 

	def getRawMetricsStatus(self):
		for group in self.metrics_by_group:
			for metric in group:
				self.raw_metrics_status.append(metric.__dict__)

	def getMetricsStatusWithMetadata(self):
		self.metrics_status_with_metadata = json.dumps({
		      "groups": json.dumps(self.groups),
		      "sources": json.dumps(self.sources),
		      "metric_types": json.dumps(self.metric_types),
		      "metrics_status": json.dumps(self.raw_metrics_status)
		})	

