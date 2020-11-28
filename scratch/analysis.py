import csv
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

results = []
with open('out.csv') as File:
    reader = csv.DictReader(File)
    for row in reader:
        results.append(row)

np_toss_pr_rate = np.array([float(record['toss-pull-request-acceptance-rate']) for record in results if record['toss-pull-request-acceptance-rate'] != 'None'])
df = pd.DataFrame({'rate': np_toss_pr_rate})
df.hist(bins=20)
plt.show()

def find_min_for_field(data, field):
    repo_id = 0
    minimum = sys.float_info.max
    for record in data:
        if record[field] != "None":
            if float(record[field]) < minimum:
                minimum = float(record[field])
                repo_id = record['id']
    return repo_id, minimum

def find_max_for_field(data, field):
    repo_id = 0
    minimum = 0.0
    for record in data:
        if record[field] != "None":
            if float(record[field]) > minimum:
                minimum = float(record[field])
                repo_id = record['id']
    return repo_id, minimum

# print(find_max_for_field(results, "toss-pull-request-acceptance-rate"))
# print(find_min_for_field(results, "toss-pull-request-acceptance-rate"))

# print(find_max_for_field(results, "issues-maintainer-response-duration"))
# print(find_min_for_field(results, "issues-maintainer-response-duration"))

# print(find_max_for_field(results, "toss-review-duration"))
# print(find_min_for_field(results, "toss-review-duration"))

