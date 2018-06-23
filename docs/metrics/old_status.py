import os
import re
import json
import glob
import webbrowser
import pprint
from flask import Flask, request, Response

pp = pprint.PrettyPrinter()

metric_files = ['upstream/1_Diversity-Inclusion.md', 'upstream/2_Growth-Maturity-Decline.md', 'upstream/3_Risk.md', 'upstream/4_Value.md']

metric_type_by_file = {
    'upstream/1_Diversity-Inclusion.md': 'Diversity and Inclusion',
    'upstream/2_Growth-Maturity-Decline.md': 'Growth, Maturity, and Decline',
    'upstream/3_Risk.md': 'Risk',
    'upstream/4_Value.md': 'Value',
}

color_by_status = {
    'unimplemented': '<span style="color: #C00">unimplemented</span>',
    'in_progress': '<span style="color: #CC0">in progress</span>',
    'implemented': '<span style="color: #0C0">implemented</span>'
}

statusMap = json.loads(open('status.json', 'r').read())
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

def getFileID(path):
    return os.path.splitext(os.path.basename(path))[0]

def printMetric(title, path):
    global statusHTML
    status = 'unimplemented'
    fileID = getFileID(path)
    if fileID in statusMap:
        status = statusMap[fileID]
    if status != 'printed':
        statusHTML += '<tr><td>{}</td><td><a href="https://github.com/chaoss/wg-gmd/tree/master/{}"> {} ({})</td></tr>'.format(color_by_status[status], path, title, fileID)
    statusMap[fileID] = 'printed'
    return fileID

# Iterate through the category Markdown files to categorize links
for filename in metric_files:
    file = open(filename, 'r')
    matches = re.findall(r'\[(.*?)\]\((.*?\.md)\)', file.read())
    if len(matches) > 0:
        statusHTML +=  '<h2>' + metric_type_by_file[filename] + '</h2><table><tr><td>status</td><td>metric</td></tr>'
    for match in matches:
        printMetric(match[0], match[1])
    statusHTML +=  '</table>'
    

# Iterate through the files in activity-metrics to find uncategorized metrics
statusHTML +=  '<h2>Experimental</h2><table><tr><td>status</td><td>metric</td></tr>'
for filename in glob.iglob('upstream/activity-metrics/*.md'):
    print(getFileID(filename).replace('-', ' ').title())
    printMetric(getFileID(filename).replace('-', ' ').title(), 'activity-metrics/' + getFileID(filename) + '.md')


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
