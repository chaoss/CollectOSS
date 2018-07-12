import os
import re
import json
import glob
import webbrowser
import augur
from flask import Flask, request, Response
from augur.server import metrics as implemented_metric_metadata
from augur.server import Server

import pprint
pp = pprint.PrettyPrinter()

class Metric(object):
    def __init__(self):
        self.tag = ''
        self.name = ''
        self.group = ''
        self.backend_status = 'undefined'
        self.frontend_status = 'unimplemented'
        self.endpoint = ''
        self.escaped_endpoint = ''
        self.source = ''
        self.metric_type = ''
        self.url = '/'
        self.is_defined = False

    def setName(self, raw_name):
        self.name = re.sub(r'-$|\*', '', re.sub('-', ' ', raw_name).title())

    def setTag(self):
        self.tag = re.sub(r'-$|\*', '', re.sub(' ', '-', self.name).lower())

    def setUrl(self):
       self.url = 'activity-metrics/' + self.tag + '.md'

    def createHTMLSafeEndpoint(self):
        self.escaped_endpoint = re.sub(">", "&gt;", re.sub("<", "&lt;", self.endpoint))

def printMetricGroup(group, level='quiet'):
    if level == 'quiet':
        pp.pprint([metric.tag for metric in group])

    if level == 'verbose':
        pp.pprint([("Name: {} \n Tag: {} \nBackend Status: {} \nFrontend Status: {} \nEndpoint: {} \nUrl: {} \nDefined: {}".format(metric.name, metric.tag, metric.backend_status, metric.frontend_status, metric.escaped_endpoint, metric.url, metric.is_defined)) for metric in group])

def getFileID(path):
    return os.path.splitext(os.path.basename(path))[0]

def createDefinedMetricTags():
    defined_metric_tags = []

    for filename in glob.iglob('upstream/activity-metrics/*.md'):
        defined_metric_tags.append(getFileID(filename))

    return defined_metric_tags

defined_metric_tags = createDefinedMetricTags()

def extractGroupedMetricNamesFromFile(filename):
    metric_file = open(filename, 'r')

    regEx = r'^(?!Name)(.*[^-])(?:\ \|)'
    if filename == 'upstream/2_Growth-Maturity-Decline.md':
        regEx = r'\[(.*?)\]\((?:.*?\.md)\)'

    return re.findall(regEx, metric_file.read(), re.M)

def extractActivityMetricNames():
    activity_file = open('upstream/activity-metrics-list.md', 'r')
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
    metric.frontend_status = metadata['frontend_status']

    if 'source' in metadata:
        metric.source = metadata['source']

    if 'endpoint' in metadata:
        metric.endpoint = metadata['endpoint']
        metric.createHTMLSafeEndpoint()

    if 'metric_type' in metadata:
        metric.metric_type = metadata['metric_type']

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

def copyImplementedMetricsIntoGroups():
    # takes implemented metrics and copies their data to the appropriate metric object
    implemented_metric_tags = [metric.tag for metric in implemented_metrics]
    for group in metric_groups:
        for grouped_metric in group:
            if grouped_metric.tag in implemented_metric_tags:
                metric_to_copy = (next((metric for metric in implemented_metrics if metric.tag == grouped_metric.tag)))
                grouped_metric.__dict__ =  metric_to_copy.__dict__.copy()

metric_files = ['upstream/1_Diversity-Inclusion.md', 'upstream/2_Growth-Maturity-Decline.md', 'upstream/3_Risk.md', 'upstream/4_Value.md']

metric_type_by_file = {
    'upstream/1_Diversity-Inclusion.md': 'diversity-inclusion',
    'upstream/2_Growth-Maturity-Decline.md': 'growth-maturity-decline',
    'upstream/3_Risk.md': 'risk',
    'upstream/4_Value.md': 'value',
}

app = augur.Application("../../augur.config.json")
sources = augur.data_sources()
sv = Server()
implemented_metrics = []

for metric in implemented_metric_metadata:
    implemented_metrics.append(createImplementedMetric(metric))

diversity_inclusion_metrics = createGroupedMetrics('upstream/1_Diversity-Inclusion.md')
growth_maturity_decline_metrics = createGroupedMetrics('upstream/2_Growth-Maturity-Decline.md')
risk_metrics = createGroupedMetrics('upstream/3_Risk.md')
value_metrics = createGroupedMetrics('upstream/4_Value.md')
metric_groups = [diversity_inclusion_metrics, growth_maturity_decline_metrics, risk_metrics, value_metrics]
experimental_metrics = [metric for metric in implemented_metrics if metric.group == "experimental"]

activity_metrics = createActivityMetrics(metric_groups)
metric_groups.append(activity_metrics)

copyImplementedMetricsIntoGroups()

class HTMLBuilder(object):

    def __init__(self):
        self.html = """"""

    color_by_backend_status = {
        'unimplemented': '<span style="color: #C00">unimplemented</span>',
        'undefined': '<span style="color: #CC0">undefined</span>',
        'implemented': '<span style="color: #0C0">implemented</span>'
    }

    color_by_frontend_status = {
        'unimplemented': '<span style="color: #C00">unimplemented</span>',
        'implemented': '<span style="color: #0C0">implemented</span>'
    }

    def addMetricToTable(self, metric, html):
        if metric.url != '/' and metric.group != 'experimental':
            html += '<tr><td>{}</td><td>{}</td><td><a href="https://github.com/chaoss/wg-gmd/tree/master/{}"> {} </td><td>{}</td><td>{}</td></tr>'.format(self.color_by_backend_status[metric.backend_status], self.color_by_frontend_status[metric.frontend_status], metric.url, metric.name, metric.escaped_endpoint, metric.source)
        else:
            html += '<tr><td>{}</td><td>{}</td><td> {} </td><td>{}</td><td>{}</td></tr>'.format(self.color_by_backend_status[metric.backend_status], self.color_by_frontend_status[metric.frontend_status], metric.name, metric.escaped_endpoint, metric.source)
        return html

    def addTableWithHeader(self, header, metrics):
        html_to_add = "<h2>{}</h2><table><tr><td>backend_status</td><td>frontend_status</td><td>metric</td><td>endpoint</td><td>source</td></tr>".format(header)
        for metric in metrics:
            html_to_add = self.addMetricToTable(metric, html_to_add)
        html_to_add += '</table>'
        self.html += html_to_add

HTMLBuilder = HTMLBuilder()

HTMLBuilder.html = """
<html>
<head>
    <title>Augur Metrics Status</title>
    <style>
        td { padding: 5px }
    </style>
</head>
<body>
    <h1>Augur Metrics Status</h1>
"""

HTMLBuilder.addTableWithHeader("Diversity and Inclusion", diversity_inclusion_metrics)
HTMLBuilder.addTableWithHeader('Growth, Maturity, and Decline', growth_maturity_decline_metrics)
HTMLBuilder.addTableWithHeader("Risk", risk_metrics)
HTMLBuilder.addTableWithHeader("Value", value_metrics)
HTMLBuilder.addTableWithHeader("Activity", activity_metrics)
HTMLBuilder.addTableWithHeader("Experimental", experimental_metrics)

HTMLBuilder.html += """
    </table>
</body>
</html>
"""

app = Flask(__name__)

@app.route("/")
def root():
    return HTMLBuilder.html

def run():
    webbrowser.open_new_tab('http://localhost:5001/')
    app.run(port=5001)

if __name__ == "__main__":
     run()

