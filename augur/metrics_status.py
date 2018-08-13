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
		self.group = 'experimental'
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
		self.ID = re.sub(r'-$|\*', '', self.source + '-' + self.tag)
		self.group = group

		if self.tag in defined_tags:
			self.is_defined = 'true'
			self.url = "https://github.com/{}/blob/wg-gmd/activity-metrics/{}.md".format(MetricsStatus.activity_repo, self.tag)
			self.backend_status = 'unimplemented'

class ImplementedMetric(Metric):

	frontend_status_extractor = FrontendStatusExtractor()

	def __init__(self, metadata, defined_tags):
		Metric.__init__(self)	

		self.ID = metadata['ID']
		self.tag = metadata['tag']
		self.name = metadata['metric_name']
		self.backend_status = 'implemented'
		self.source = metadata['source']

		if 'endpoint' in metadata:
			self.endpoint = metadata['endpoint']
			self.frontend_status = self.frontend_status_extractor.determineFrontendStatus(self.endpoint)

		if 'metric_type' in metadata:
			self.metric_type = metadata['metric_type']
		else:
			self.metric_type = 'metric'

		if self.tag in defined_tags:
			self.url = "https://github.com/{}/blob/wg-gmd/activity-metrics/{}.md".format(MetricsStatus.activity_repo, self.tag)
			self.is_defined = 'true'

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

		self.defined_tags = []
		self.implemented_metrics = []

		self.raw_metrics_status = []
		self.metadata = []

	def create_metrics_status(self):

		self.getDefinedMetricTags()

		self.buildImplementedMetrics()

		self.diversity_inclusion_metrics = self.createGroupedMetricsFromListOfRemotes(self.diversity_inclusion_urls, "diversity-inclusion")
		self.growth_maturity_decline_metrics = self.createGroupedMetricsFromListOfRemotes(self.growth_maturity_decline_urls, "growth-maturity-decline")
		self.risk_metrics = self.createGroupedMetricsFromListOfRemotes(self.risk_urls, "risk")
		self.value_metrics = self.createGroupedMetricsFromListOfRemotes(self.value_urls, "value")

		self.metrics_by_group = [self.diversity_inclusion_metrics, self.growth_maturity_decline_metrics, self.risk_metrics, self.value_metrics]

		self.activity_metrics = self.createActivityMetrics()
		self.metrics_by_group.append(self.activity_metrics)

		self.experimental_metrics = [metric for metric in self.implemented_metrics if metric.group == "experimental"]
		self.metrics_by_group.append(self.experimental_metrics)

		self.copyImplementedMetrics()

		self.getRawMetricsStatus()

		self.getMetadata()

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
						for key in metric.__dict__.keys():
							if key != 'group': #don't copy the group over, since the metrics are already grouped
								grouped_metric.__dict__[key] = metric.__dict__[key]

	def buildImplementedMetrics(self):
		for metric in metric_metadata:
			if "ID" in metric.keys():
				self.implemented_metrics.append(ImplementedMetric(metric, self.defined_tags))

	# grouped metrics
	def extractGroupedMetricNamesFromRemoteFile(self, remote):
		metric_file = requests.get(remote["raw_content_url"]).text

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
		
	def createActivityMetrics(self):
		activity_metrics_raw_text = requests.get(self.activity_urls[0]["raw_content_url"]).text

		raw_activity_names = re.findall(r'\|(?:\[|)(.*)\|(?:\]|)(?:\S| )', activity_metrics_raw_text)

		activity_names = [re.sub(r'(?:\]\(.*\))', '', name) for name in raw_activity_names if '---' not in name and 'Name' not in name]

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
		activity_files = self.__githubapi.get_repo(self.activity_repo).get_dir_contents("activity-metrics")
		self.defined_tags = []

		for file in activity_files:
			self.defined_tags.append(re.sub(".md", '', file.name))

	def getMetricSources(self):
		for source in [metric['source'] for metric in self.raw_metrics_status]:
			source = source.lower()
			if source not in self.sources and source != "none":
				self.sources.append(source)
			self.sources.append("all")

	def getMetricTypes(self):
		for metric_type in [metric['metric_type'] for metric in self.raw_metrics_status]:
			metric_type = metric_type.lower()
			if metric_type not in self.metric_types and metric_type != "none":
				self.metric_types.append(metric_type) 
			self.metric_types.append("all")

	def getMetricTags(self):
		for tag in [(metric['tag'], metric['group']) for metric in self.raw_metrics_status]:
			# tag[0] = tag[0].lower()
			if tag[0] not in [tag[0] for tag in self.tags] and tag[0] != "none":
				self.tags[tag[0]] = tag[1]

	def getRawMetricsStatus(self):
		for group in self.metrics_by_group:
			for metric in group:
				self.raw_metrics_status.append(metric.__dict__)

	def getMetadata(self):
		self.getMetricSources()
		self.getMetricTypes()
		self.getMetricTags()

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

