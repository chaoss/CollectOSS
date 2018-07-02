import os
import re
import json
import glob
import webbrowser
import augur
from flask import Flask, request, Response
from augur.server import metrics as implemented_metric_metadata
from augur.server import Server

class Metric(object):
    def __init__(self, tag='', name='', group='', status='unimplemented', raw_endpoint="", endpoint='', source='', metric_type='', url='/', is_defined=False):
        self.tag = tag
        self.name = name
        self.group = group
        self.status = status
        self.raw_endpoint = raw_endpoint
        self.endpoint = endpoint
        self.source = source
        self.metric_type = metric_type
        self.url = url
        self.is_defined = is_defined

defined_metric_tags = []

def getFileID(path):
    return os.path.splitext(os.path.basename(path))[0]

for filename in glob.iglob('upstream/activity-metrics/*.md'):
    defined_metric_tags.append(getFileID(filename))

def extractGroupedMetricsFromFile(filename):
    file = open(filename, 'r')
    regEx = r'^(?!Name)(.*[^-])(?:\ \|)'
    if filename == 'upstream/2_Growth-Maturity-Decline.md':
        regEx = r'\[(.*?)\]\((?:.*?\.md)\)'
    metric_names = re.findall(regEx, file.read(), re.M)
    metrics = []
    for raw_name in metric_names:
        name = re.sub(r'-$|\*', '', raw_name)
        is_defined = False
        status = 'undefined'
        url = '/'
        tag = re.sub(' ', '-', name).lower()

        if tag in defined_metric_tags:
            is_defined = True
            url = 'activity-metrics/' + tag + '.md'
            status = "unimplemented"

        metrics.append(Metric(tag=tag, name=name, url=url, status=status, group=metric_type_by_file[filename], is_defined=is_defined))

    return metrics

def extractImplementedMetric(metric):
    tag = metric['metric_name']
    name = re.sub('-', ' ', tag).title()
    source_of_metric = ''
    url='/'
    endpoint_of_metric = ''
    raw_endpoint = ''
    type_of_metric = 'metric'

    if 'source' in metric:
        source_of_metric = metric['source']

    if 'endpoint' in metric:
        raw_endpoint = metric['endpoint']
        endpoint_of_metric = re.sub(">", "&gt;", re.sub("<", "&lt;", raw_endpoint))

    if 'metric_type' in metric:
        type_of_metric = metric['metric_type']

    if tag in defined_metric_tags:
        url = 'activity-metrics/' + tag + '.md'

    return Metric(name=name, tag=metric['metric_name'], url=url, status='implemented', raw_endpoint=raw_endpoint, endpoint=endpoint_of_metric, source=source_of_metric, group=metric['group'], metric_type=type_of_metric, is_defined=True)

def extractActivityMetrics(metric_groups):
    activity_file = open('upstream/activity-metrics-list.md', 'r')
    raw_activity_names = re.findall(r'\|(?:\[|)(.*)\|(?:\]|)(?:\S| )', activity_file.read())
    activity_names = [re.sub(r'(?:\]\(.*\))', '', name) for name in raw_activity_names if '---' not in name and 'Name' not in name]
    activity_metrics = []

    for name in activity_names:
        raw_tag = re.sub(' ', '-', name).lower()
        tag = re.sub(r'-$|\*', '', raw_tag, re.M)
        is_defined = False
        status = 'undefined'

        if tag in defined_metric_tags:
            is_defined = True
            status = "unimplemented"

        found = False
        for group in metric_groups:
            if tag in [metric.tag for metric in group]:
                found = True

        if found == False:
            activity_metrics.append(Metric(tag=tag, name=name, status=status, is_defined=is_defined))

    return activity_metrics

metric_files = ['upstream/1_Diversity-Inclusion.md', 'upstream/2_Growth-Maturity-Decline.md', 'upstream/3_Risk.md', 'upstream/4_Value.md']

metric_type_by_file = {
    'upstream/1_Diversity-Inclusion.md': 'diversity-inclusion',
    'upstream/2_Growth-Maturity-Decline.md': 'growth-maturity-decline',
    'upstream/3_Risk.md': 'risk',
    'upstream/4_Value.md': 'value',
}

app = augur.Application()
sources = augur.data_sources()
sv = Server()
implemented_metrics = []

for metric in implemented_metric_metadata:
    implemented_metrics.append(extractImplementedMetric(metric))

diversity_inclusion_metrics = extractGroupedMetricsFromFile('upstream/1_Diversity-Inclusion.md')
growth_maturity_decline_metrics = extractGroupedMetricsFromFile('upstream/2_Growth-Maturity-Decline.md')
risk_metrics = extractGroupedMetricsFromFile('upstream/3_Risk.md')
value_metrics = extractGroupedMetricsFromFile('upstream/4_Value.md')
metric_groups = [diversity_inclusion_metrics, growth_maturity_decline_metrics, risk_metrics, value_metrics]
experimental_metrics = [metric for metric in implemented_metrics if metric.group == "experimental"]

activity_metrics = extractActivityMetrics(metric_groups)
metric_groups.append(activity_metrics)

# takes implemented metrics and copies their data to the appropriate metric object
implemented_metric_tags = [metric.tag for metric in implemented_metrics]
for group in metric_groups:
    for grouped_metric in group:
        if grouped_metric.tag in implemented_metric_tags:
            metric_to_copy = (next((metric for metric in implemented_metrics if metric.tag == grouped_metric.tag)))
            grouped_metric.__dict__ =  metric_to_copy.__dict__.copy()

class HTMLBuilder(object):

    color_by_status = {
        'unimplemented': '<span style="color: #C00">unimplemented</span>',
        'undefined': '<span style="color: #CC0">undefined</span>',
        'implemented': '<span style="color: #0C0">implemented</span>'
    }

    def printMetric(self, metric, html):
        if metric.url != '/':
            html += '<tr><td>{}</td><td><a href="https://github.com/chaoss/wg-gmd/tree/master/{}"> {} </td><td>{}</td><td>{}</td></tr>'.format(self.color_by_status[metric.status], metric.url, metric.name, metric.endpoint, metric.source)
        else:
            html += '<tr><td>{}</td><td> {} </td><td>{}</td><td>{}</td></tr>'.format(self.color_by_status[metric.status], metric.name, metric.endpoint, metric.source)
        return html

    def addToStatusHTML(self, header, metrics):
        html = "<h2>{}</h2><table><tr><td>status</td><td>metric</td><td>endpoint</td><td>source</td></tr>".format(header)
        for metric in metrics:
            html = self.printMetric(metric, html)
        html += '</table>'
        return html

HTMLBuilder = HTMLBuilder()

statusHTML = """
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

statusHTML += HTMLBuilder.addToStatusHTML("Diversity and Inclusion", diversity_inclusion_metrics)
statusHTML += HTMLBuilder.addToStatusHTML('Growth, Maturity, and Decline', growth_maturity_decline_metrics)
statusHTML += HTMLBuilder.addToStatusHTML("Risk", risk_metrics)
statusHTML += HTMLBuilder.addToStatusHTML("Value", value_metrics)
statusHTML += HTMLBuilder.addToStatusHTML("Activity", activity_metrics)
statusHTML += HTMLBuilder.addToStatusHTML("Experimental", experimental_metrics)

statusHTML += """
    </table>
</body>
</html>
"""

app = Flask(__name__)

@app.route("/")
def root():
    return statusHTML

def run():
    webbrowser.open_new_tab('http://localhost:5001/')
    app.run(port=5001)

if __name__ == "__main__":
     run()


