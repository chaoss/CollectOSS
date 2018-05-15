import os
import re
import json
import glob

metric_files = ['upstream/1_Diversity-Inclusion.md', 'upstream/2_Growth-Maturity-Decline.md', 'upstream/3_Risk.md', 'upstream/4_Value.md']

metric_type_by_file = {
    'upstream/1_Diversity-Inclusion.md': 'Diversity and Inclusion',
    'upstream/2_Growth-Maturity-Decline.md': 'Growth, Maturity, and Decline',
    'upstream/3_Risk.md': 'Risk',
    'upstream/4_Value.md': 'Value',
}

color_by_status = {
    'unimplemented': '\033[31mu',
    'in_progress': '\033[33mp',
    'implemented': '\033[32mi'
}


print('+----- STATUS ------+')
print('| \033[31mu\033[0m - unimplemented |')
print('| \033[33mp\033[0m - in_progress   |')
print('| \033[32mi\033[0m - implemented   |')
print('+-------------------+\n\n')
statusMap = json.loads(open('status.json', 'r').read())

def getFileID(path):
    return os.path.splitext(os.path.basename(path))[0]

def printMetric(title, path):
    status = 'unimplemented'
    fileID = getFileID(path)
    if fileID in statusMap:
        status = statusMap[fileID]
    if status != 'printed':
        print('{} {} ({})\033[0m'.format(color_by_status[status], title, fileID))
        print('  https://github.com/chaoss/metrics/tree/master/{}\n'.format(path))
    statusMap[fileID] = 'printed'
    return fileID

# Iterate through the category Markdown files to categorize links
for filename in metric_files:
    file = open(filename, 'r')
    matches = re.findall(r'\[(.*?)\]\((.*?\.md)\)', file.read())
    if len(matches) > 0:
        print('\033[4m' + metric_type_by_file[filename] + '\033[0m\n')
    for match in matches:
        printMetric(match[0], match[1])
    

# Iterate through the files in activity-metrics to find uncategorized metrics
print('\033[4mUncategorized\033[0m\n')
for filename in glob.iglob('upstream/activity-metrics/*.md'):
    printMetric(getFileID(filename).replace('-', ' ').title(), 'activity-metrics/' + getFileID(filename) + '.md')