import json
import os, re
import requests

def get_NPM_data(package):
    url = "https://registry.npmjs.org/%s" % package
    r = requests.get(url)
    if r.status_code < 400:
        return r.json()
    return {}


