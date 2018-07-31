import os
import re
import json
import glob
from flask import Response
from bs4 import BeautifulSoup
from augur.util import getFileID, metric_metadata
import pprint
import requests

class Metric(object):
	def __init__(self):
		self.tag = 'n/a'
		self.name = 'n/a'
		self.group = 'n/a'
		self.backend_status = 'undefined'
		self.frontend_status = 'unimplemented'
		self.endpoint = 'n/a'
		self.escaped_endpoint = 'n/a'
		self.source = 'n/a'
		self.metric_type = 'n/a'
		self.url = '/'
		self.is_defined = False

	def setName(self, raw_name):
		self.name = re.sub('/', '-', re.sub(r'-$|\*', '', re.sub('-', ' ', raw_name).title()))

	def setTag(self):
		self.tag = re.sub(r'-$|\*', '', re.sub(' ', '-', self.name).lower())

	def setUrl(self):
	   self.url = 'activity-metrics/' + self.tag + '.md'

# implemented metrics
def copyImplementedMetrics():
	# takes implemented metrics and copies their data to the appropriate metric object
	implemented_metric_tags = [metric.tag for metric in implemented_metrics]
	for group in metrics_by_group:
		for grouped_metric in group:
			if grouped_metric.tag in implemented_metric_tags:
				metric_to_copy = (next((metric for metric in implemented_metrics if metric.tag == grouped_metric.tag)))
				grouped_metric.__dict__ =  metric_to_copy.__dict__.copy()

def createImplementedMetric(metadata):
	metric = Metric()
	metric.name = metadata['metric_name']
	metric.setTag()
	metric.backend_status = 'implemented'
	metric.group = metadata['group']

	if 'source' in metadata:
		metric.source = metadata['source']

	if 'metric_type' in metadata:
	    metric.metric_type = metadata['metric_type']
	else:
	    metric.metric_type = 'metric'

	if 'endpoint' in metadata:
		metric.endpoint = metadata['endpoint']
		metric.frontend_status = frontendStatusExtractor.determineFrontendStatus(metric)
		metric.escaped_endpoint = metadata['escaped_endpoint']

	if determineIfMetricIsDefined(metric.tag):
		metric.setUrl()

	return metric

def buildImplementedMetrics():
	implemented_metrics = []

	for metadata in metric_metadata:
		implemented_metrics.append(createImplementedMetric(metadata))

	return implemented_metrics


# grouped metrics
def extractGroupedMetricNamesFromRemoteFile(remote):

	metric_file = requests.get(remote["remote_url"]).text

	regEx = r'^(?!Name)(.*[^-])(?:\ \|)'
	if remote["has_links"] == True:
		regEx = r'\[(.*?)\]\((?:.*?\.md)\)'

	return re.findall(regEx, metric_file, re.M)

def createGroupedMetricsFromListOfRemotes(remotes_list, group):
	
	remote_names = []

	for remote in remotes_list:
		for name in extractGroupedMetricNamesFromRemoteFile(remote):
			remote_names.append(name)

	remote_metrics = []

	for name in remote_names:
		remote_metrics.append(createMetric(name, group))

	return remote_metrics


# activity metrics
def extractActivityMetricNames():

	activity_metrics_raw_text = requests.get("https://raw.githubusercontent.com/{}/master/activity-metrics-list.md".format(activity_repo_remote)).text

	raw_activity_names = re.findall(r'\|(?:\[|)(.*)\|(?:\]|)(?:\S| )', activity_metrics_raw_text)

	return [re.sub(r'(?:\]\(.*\))', '', name) for name in raw_activity_names if '---' not in name and 'Name' not in name]

def createActivityMetrics(metrics_by_group):

	activity_names = extractActivityMetricNames()

	activity_metrics = []

	for raw_name in activity_names:
		metric = createMetric(raw_name, "activity")

		isUngroupedMetric = False
		for group in metrics_by_group:
			if metric.tag in [metric.tag for metric in group]:
				isUngroupedMetric = True

		if isUngroupedMetric == False:
			activity_metrics.append(metric)

	return activity_metrics

# grouped/activity metric creation
def createMetric(raw_name, group):
	metric = Metric()
	metric.setName(raw_name)
	metric.setTag()
	metric.group = group

	if determineIfMetricIsDefined(metric.tag):
		metric.is_defined = True
		metric.setUrl()
		metric.backend_status = 'unimplemented'

	return metric


# other
def determineIfMetricIsDefined(tag):

	activity_remote_url = "https://raw.githubusercontent.com/{}/master/activity-metrics/".format(activity_repo_remote)

	status_code = requests.get(activity_remote_url + tag + ".md").status_code

	# ipdb.set_trace()

	if status_code == 404:
		return False
	else:
		return True

class FrontendStatusExtractor(object):
	def __init__(self):
		self.api_text =  open("frontend/app/AugurAPI.js", 'r').read()
		self.frontend_card_files = []
		self.endpoint = ""
		self.timeseries_attributes = re.findall(r'(?:(Timeseries)\(repo, )\'(.*)\', \'(.*)\'', self.api_text)
		self.endpoint_attributes = re.findall(r'(?:(Endpoint)\(repo, )\'(.*)\', \'(.*)\'', self.api_text)
		self.git_attributes = re.findall(r'(?:(GitEndpoint)\(repo, )\'(.*)\', \'(.*)\'', self.api_text)
		
	def determineFrontendStatus(self, metric):
		if '/api/unstable/<owner>/<repo>/timeseries/' in metric.endpoint:
			endpoint_attributes = self.timeseries_attributes
			attribute = [attribute[1] for attribute in endpoint_attributes if '/api/unstable/<owner>/<repo>/timeseries/' + attribute[2] == metric.endpoint]

		elif '/api/unstable/<owner>/<repo>/' in metric.endpoint:
			endpoint_attributes = self.endpoint_attributes
			attribute = [attribute[1] for attribute in endpoint_attributes if '/api/unstable/<owner>/<repo>/' + attribute[2] == metric.endpoint]

		elif '/api/unstable/git/' in metric.endpoint:
			endpoint_attributes = self.git_attributes
			attribute = [attribute[1] for attribute in endpoint_attributes if '/api/unstable/git/' + attribute[2] == metric.endpoint]

		status = 'unimplemented'
		if len(attribute) != 0 and attribute[0] in self.api_text:
			status = 'implemented'

		return status


activity_repo_remote = "OSSHealth/wg-gmd"

frontendStatusExtractor = FrontendStatusExtractor()
implemented_metrics = buildImplementedMetrics()

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

diversity_inclusion_metrics = createGroupedMetricsFromListOfRemotes(diversity_inclusion_remotes, "diversity-inclusion")
growth_maturity_decline_metrics = createGroupedMetricsFromListOfRemotes(growth_maturity_decline_remotes, "growth-maturity-decline")
risk_metrics = createGroupedMetricsFromListOfRemotes(risk_remotes, "risk")
value_metrics = createGroupedMetricsFromListOfRemotes(value_remotes, "value")

metrics_by_group = [diversity_inclusion_metrics, growth_maturity_decline_metrics, risk_metrics, value_metrics]

activity_metrics = createActivityMetrics(metrics_by_group)
metrics_by_group.append(activity_metrics)

experimental_metrics = [metric for metric in implemented_metrics if metric.group == "experimental"]
metrics_by_group.append(experimental_metrics)

copyImplementedMetrics()

def create_routes(server):

	@server.app.route("/{}/metrics/status".format(server.api_version))
	def metrics_status():

		metrics_status = []

		for group in metrics_by_group:
			for metric in group:
				metrics_status.append(metric.__dict__)

		return Response(response=json.dumps(metrics_status),
						status=200,
						mimetype="application/json")
