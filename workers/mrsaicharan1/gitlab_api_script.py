import requests
import pprint
import os
import json

pp = pprint.PrettyPrinter(indent=4)
proxies = {
    'http': os.environ.get('HTTP_PROXY'),
    'https': os.environ.get('HTTPS_PROXY'),
}
commit_info = requests.get(
    'https://gitlab.com/api/v4/projects/13876455/repository/commits', proxies=proxies
).json()
pp.pprint(commit_info)
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(commit_info, f, ensure_ascii=False, indent=4)
