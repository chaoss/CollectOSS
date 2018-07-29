import os
import re
import json
import glob
from flask import Response
from bs4 import BeautifulSoup
from augur.util import getFileID

import pprint
pp = pprint.PrettyPrinter()

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

def printMetricGroup(group, level='quiet'):
    if level == 'quiet':
        pp.pprint([metric.tag for metric in group])

    if level == 'verbose':
        pp.pprint([("Name: {} \n Tag: {} \nBackend Status: {} \nFrontend Status: {} \nEndpoint: {} \nUrl: {} \nDefined: {}".format(metric.name, metric.tag, metric.backend_status, metric.frontend_status, metric.escaped_endpoint, metric.url, metric.is_defined)) for metric in group])

def createDefinedMetricTags():
    defined_metric_tags = []

    for filename in glob.iglob('docs/metrics/upstream/activity-metrics/*.md'):
        defined_metric_tags.append(getFileID(filename))

    return defined_metric_tags

def extractGroupedMetricNamesFromFile(filename):
    metric_file = open(filename, 'r')

    regEx = r'^(?!Name)(.*[^-])(?:\ \|)'
    if filename == 'docs/metrics/upstream/2_Growth-Maturity-Decline.md':
        regEx = r'\[(.*?)\]\((?:.*?\.md)\)'

    return re.findall(regEx, metric_file.read(), re.M)

def extractActivityMetricNames():
    activity_file = open('docs/metrics/upstream/activity-metrics-list.md', 'r')
    raw_activity_names = re.findall(r'\|(?:\[|)(.*)\|(?:\]|)(?:\S| )', activity_file.read())
    return [re.sub(r'(?:\]\(.*\))', '', name) for name in raw_activity_names if '---' not in name and 'Name' not in name]

def createActivityMetrics(metric_groups):
    activity_names = extractActivityMetricNames()
    
    activity_metrics = []

    for name in activity_names:
        metric = createActivityMetric(name)

        isUngroupedMetric = False
        for group in metric_groups:
            if metric.tag in [metric.tag for metric in group]:
                isUngroupedMetric = True

        if isUngroupedMetric == False:
            activity_metrics.append(metric)

    return activity_metrics

def createGroupedMetrics(filename):
    metric_names = extractGroupedMetricNamesFromFile(filename)

    metrics = []
    for raw_name in metric_names:
        metrics.append(createGroupedMetric(raw_name))

    return metrics

def createGroupedMetric(raw_name):
    metric = Metric()
    metric.setName(raw_name)
    metric.setTag()

    if metric.tag in defined_metric_tags:
        metric.is_defined = True
        metric.setUrl()
        metric.backend_status = 'unimplemented'

    return metric

def createImplementedMetric(metadata):
    metric = Metric()
    metric.name = metadata['metric_name']
    metric.setTag()
    metric.backend_status = 'implemented'
    metric.group = metadata['group']
    # metric.frontend_status = util.determineFrontendStatus(metric.endpoint)

    if 'source' in metadata:
        metric.source = metadata['source']

    if 'endpoint' in metadata:
        metric.endpoint = metadata['endpoint']
        metric.frontend_status = "broken"
        # metric.frontend_status = determineFrontendStatus(metric.endpoint)
        metric.escaped_endpoint = metadata['escaped_endpoint']

    if 'metric_type' in metadata:
        metric.metric_type = metadata['metric_type']
    else:
        metric.metric_type = 'metric'

    if metric.tag in defined_metric_tags:
        metric.setUrl()

    return metric

def createActivityMetric(raw_name): 
    metric = Metric()

    metric.setName(raw_name)
    metric.setTag()

    if metric.tag in defined_metric_tags:
        metric.is_defined = True
        metric.setUrl()
        metric.backend_status = "unimplemented"

    return metric

def copyImplementedMetrics():
    # takes implemented metrics and copies their data to the appropriate metric object
    implemented_metric_tags = [metric.tag for metric in implemented_metrics]
    for group in metric_groups:
        for grouped_metric in group:
            if grouped_metric.tag in implemented_metric_tags:
                metric_to_copy = (next((metric for metric in implemented_metrics if metric.tag == grouped_metric.tag)))
                grouped_metric.__dict__ =  metric_to_copy.__dict__.copy()

def buildImplementedMetrics():
    implemented_metrics = []
    implemented_metric_metadata = []

    with open('docs/metrics/output/metadata.json', 'r') as metadata:
    	implemented_metric_metadata = json.load(metadata)

    for metric in implemented_metric_metadata:
        implemented_metrics.append(createImplementedMetric(metric))

    return implemented_metrics

def writeStatusToFile():
    status = []
    status_json = open('docs/metrics/output/status.json', 'w')

    for group in metric_groups:
        for metric in group:
            status.append(metric.__dict__)

    json.dump(status, status_json, indent=4)

def fileExists(path):
    return os.path.exists(path)

class frontendExtractor(object):
    def __init__(self, endpoint):
        self.api = None
        self.endpoint_attributes = None
        self.frontend_card_files = []
        self.endpoint = endpoint

def extractEndpointsAndAttributes(extractor, type):
        if fileExists('../../frontend/app/AugurAPI.js'):
            extractor.api = open("../../frontend/app/AugurAPI.js", 'r')
            extractor.frontend_card_files = ['../../frontend/app/components/DiversityInclusionCard.vue', 
                       '../../frontend/app/components/GrowthMaturityDeclineCard.vue', 
                       '../../frontend/app/components/RiskCard.vue', 
                       '../../frontend/app/components/ValueCard.vue',
                       '../../frontend/app/components/BaseRepoActivityCard.vue',
                       '../../frontend/app/components/ExperimentalCard.vue',
                       '../../frontend/app/components/GitCard.vue']

        if fileExists('frontend/app/AugurAPI.js'):
            extractor.api = open("frontend/app/AugurAPI.js", 'r')
            extractor.frontend_card_files = ['frontend/app/components/DiversityInclusionCard.vue', 
                       'frontend/app/components/GrowthMaturityDeclineCard.vue', 
                       'frontend/app/components/RiskCard.vue', 
                       'frontend/app/components/ValueCard.vue',
                       'frontend/app/components/BaseRepoActivityCard.vue',
                       'frontend/app/components/ExperimentalCard.vue',
                       'frontend/app/components/GitCard.vue']

        if type is 'timeseries':
            extractor.endpoint_attributes = re.findall(r'(?:(Timeseries)\(repo, )\'(.*)\', \'(.*)\'', extractor.api.read())
        if type is 'metric':
            extractor.endpoint_attributes = re.findall(r'(?:(Endpoint)\(repo, )\'(.*)\', \'(.*)\'', extractor.api.read())
        if type is 'git':
            extractor.endpoint_attributes = re.findall(r'(?:(GitEndpoint)\(repo, )\'(.*)\', \'(.*)\'', extractor.api.read())
        return extractor

def determineFrontendStatus(endpoint):
    fe = frontendExtractor(endpoint)

    if '/api/unstable/<owner>/<repo>/timeseries/' in endpoint:
        extractor = extractEndpointsAndAttributes(fe, 'timeseries')
        attribute = [attribute[1] for attribute in extractor.endpoint_attributes if '/api/unstable/<owner>/<repo>/timeseries/' + attribute[2] == endpoint]

    elif '/api/unstable/<owner>/<repo>/' in endpoint:
        extractor = extractEndpointsAndAttributes(fe, 'metric')
        attribute = [attribute[1] for attribute in extractor.endpoint_attributes if '/api/unstable/<owner>/<repo>/' + attribute[2] == endpoint]

    elif '/api/unstable/git/' in endpoint:
        extractor = extractEndpointsAndAttributes(fe, 'git')
        attribute = [attribute[1] for attribute in extractor.endpoint_attributes if '/api/unstable/git/' + attribute[2] == endpoint]

    status = 'unimplemented'
    for card in extractor.frontend_card_files:
        card = open(card, 'r').read()
        if len(attribute) != 0 and attribute[0] in card:
            status = 'implemented'
            break

    return status

defined_metric_tags = createDefinedMetricTags()
implemented_metrics = buildImplementedMetrics()

diversity_inclusion_metrics = createGroupedMetrics('docs/metrics/upstream/1_Diversity-Inclusion.md')
growth_maturity_decline_metrics = createGroupedMetrics('docs/metrics/upstream/2_Growth-Maturity-Decline.md')
risk_metrics = createGroupedMetrics('docs/metrics/upstream/3_Risk.md')
value_metrics = createGroupedMetrics('docs/metrics/upstream/4_Value.md')
metric_groups = [diversity_inclusion_metrics, growth_maturity_decline_metrics, risk_metrics, value_metrics]

activity_metrics = createActivityMetrics(metric_groups)
metric_groups.append(activity_metrics)

experimental_metrics = [metric for metric in implemented_metrics if metric.group == "experimental"]
metric_groups.append(experimental_metrics)

copyImplementedMetrics()
writeStatusToFile()

def create_routes(server):

	@server.app.route("/{}/metrics/status".format(server.api_version))
	def metrics_status():

		metrics = []

		for group in metric_groups:
			for metric in group:
				metrics.append(metric.__dict__)

		return Response(response=json.dumps(metrics),
		                status=200,
		                mimetype="application/json")
