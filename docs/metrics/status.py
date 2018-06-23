import os
import re
import json
import glob
import webbrowser
import pprint
from flask import Flask, request, Response

pp = pprint.PrettyPrinter()

class Metric(object):
    def __init__(self, tag="", name="", group="", status="unimplemented", endpoint="", source="", metricType="", url="/"):
        self.tag = tag
        self.name = name
        self.group = group
        self.status = status
        self.endpoint = endpoint
        self.source = source
        self.metricType = metricType
        self.url = url

class Parser(object):

    def extractImplementedMetricData(self):
        server = open("../../augur/server.py", 'r')
        sourceRegEx = r'(Timeseries|Metric|Git)(?:Metric)?\((.*)\.(.*), \'(.*)\''
        metricDataTuples = re.findall(sourceRegEx, server.read()) 
        return metricDataTuples

    def extractImplementedMetricGroup(self, tag):
        mapping = json.loads(open('group-mapping.json', 'r').read())
        return mapping[tag]

class MetricsBuilder(object):

    parser = Parser()
    mapping = json.loads(open('group-mapping.json', 'r').read())

    def buildImplementedMetricObjects(self):
        implementedMetricData = self.parser.extractImplementedMetricData()
        implementedMetricObjects = []
        for metric in implementedMetricData:
            implementedMetricObjects.append(self.buildImplementedMetricObject(metric))
        return implementedMetricObjects

    def buildUnimplementedMetricObject(self, mapping, tag):
        name = re.sub("-", " ", tag.title())
        group = self.parser.extractImplementedMetricGroup(tag)
        return Metric(name=name, tag=tag, group=group)

    def buildAllMetricObjects(self, mapping, implementedMetricData):
        metrics = []
        implementedMetricObjects = self.buildImplementedMetricObjects()
        implementedMetricTags = [metric.tag for metric in implementedMetricObjects]
        for tag in mapping:
            if tag in implementedMetricTags:
                metricToAppend = next(metric for metric in implementedMetricObjects if metric.tag == tag)
            else:
                metricToAppend = self.buildUnimplementedMetricObject(self.mapping, tag)
            metrics.append(metricToAppend)

        return metrics

    def buildImplementedMetricObject(self, metric):
        name = re.sub("_", " ", metric[2].title())
        tag = re.sub("_", '-', metric[2])
        group = self.parser.extractImplementedMetricGroup(tag)
        status = "implemented"
        endpoint = metric[3]
        source = metric[1]
        metricType = metric[0]
        url = "/"
        return Metric(tag, name, group, status, endpoint, source, metricType, url)

    def printMetricList(self, metrics):
        for metric in metrics:
            print("Name: {}, Tag: {}, Group: {} Status: {}, Endpoint: {}, Source: {}, Type: {}".format(metric.name, metric.tag, metric.group, metric.status, metric.endpoint, metric.source, metric.metricType))

    def extractMetricsWithGroup(self, group):
        implementedMetricObjects = self.buildAllMetricObjects(self.mapping, self.buildImplementedMetricObjects())
        return [metric for metric in implementedMetricObjects if metric.group == group]


sources = [
            "ghtorrent", 
            "github", 
            "git", 
            "downloads", 
            "ghtorrentplus",
            "publicwww",
            "librariesio"
        ]

bd = MetricsBuilder()
ps = Parser()
mapping = json.loads(open('group-mapping.json', 'r').read())

implementedMetricData = ps.extractImplementedMetricData()
metrics = bd.buildAllMetricObjects(mapping, implementedMetricData)

growth_maturity_decline_metrics = bd.extractMetricsWithGroup("growth-maturity-decline")
diversity_inclusion_metrics = bd.extractMetricsWithGroup("diversity-inclusion")
risk_metrics = bd.extractMetricsWithGroup("risk")
value_metrics = bd.extractMetricsWithGroup("value")
activity_metrics = bd.extractMetricsWithGroup("activity")
experimental_metrics = bd.extractMetricsWithGroup("experimental")

class HTMLBuilder(object):

    color_by_status = {
        'unimplemented': '<span style="color: #C00">unimplemented</span>',
        'in_progress': '<span style="color: #CC0">in progress</span>',
        'implemented': '<span style="color: #0C0">implemented</span>'
    }

    def printMetric(self, metric, html):
        html += '<tr><td>{}</td><td><a href="{}"> {} </td><td>{}</td><td>{}</td></tr>'.format(self.color_by_status[metric.status], metric.url, metric.name, metric.endpoint, metric.source)
        return html

    def addToStatusHTML(self, statusHTML, newHTML):
        statusHTML += newHTML
        return statusHTML

    def createTableOfMetricObjects(self, header, metrics):
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

diversity_inclusion_HTML = HTMLBuilder.createTableOfMetricObjects("Diversity and Inclusion", diversity_inclusion_metrics)
statusHTML = HTMLBuilder.addToStatusHTML(statusHTML, diversity_inclusion_HTML)

growth_maturity_decline_HTML = HTMLBuilder.createTableOfMetricObjects("Growth, Maturity, and Decline", growth_maturity_decline_metrics)
statusHTML = HTMLBuilder.addToStatusHTML(statusHTML, growth_maturity_decline_HTML)

risk_HTML = HTMLBuilder.createTableOfMetricObjects("Risk", risk_metrics)
statusHTML = HTMLBuilder.addToStatusHTML(statusHTML, risk_HTML)

value_HTML = HTMLBuilder.createTableOfMetricObjects("Value", value_metrics)
statusHTML = HTMLBuilder.addToStatusHTML(statusHTML, value_HTML)

activity_HTML = HTMLBuilder.createTableOfMetricObjects("Activity", activity_metrics)
statusHTML = HTMLBuilder.addToStatusHTML(statusHTML, activity_HTML)

experimental_HTML = HTMLBuilder.createTableOfMetricObjects("Experimental", experimental_metrics)
statusHTML = HTMLBuilder.addToStatusHTML(statusHTML, experimental_HTML)


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