import requests
import os
import json

token = os.getenv('AUTH_TOKEN')  # the auth token of the account
project_id = '17206683'  # the project id

headers = {
    'PRIVATE-TOKEN': token
}
commits = requests.get(
    f'https://gitlab.com/api/v4/projects/{project_id}/repository/commits', headers=headers
).json()

with open('data_rest.json', 'w', encoding='utf-8') as f:
    json.dump(commits, f)
