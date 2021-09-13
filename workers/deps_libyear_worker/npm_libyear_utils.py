import json
import os, re
import requests

def get_NPM_data(package):
    url = "https://registry.npmjs.org/%s" % package
    r = requests.get(url)
    if r.status_code < 400:
        return r.json()
    return {}


def clean_version(version):
    version = [v for v in version if v.isdigit() or v == '.']
    return ''.join(version)


def get_latest_patch(version, data):
    versions = data['versions']
    try:
        index = list(versions.keys()).index(version)
    except:
        #NOTE: Add error logging here
        pass
    major,minor,patch = version.split('.')
    consider_version = version
    for v in list(versions.keys())[index:]:
        if v.split('.')[0]==major:
            if v.split('.')[1]== minor:
                if v.split('.')[2]>patch:
                    consider_version = v
    return consider_version


def get_lastest_minor(version, data):
    versions = data['versions']
    try:
        index = list(versions.keys()).index(version)
    except:
        #NOTE: Add error logging here
        pass
    major,minor,patch = version.split('.')
    consider_version = version
    for v in list(versions.keys())[index:]:
        if v.split('.')[0]==major:
            if v.split('.')[1]>minor:
                    consider_version = v
    return consider_version 


def get_npm_release_date(data, version):
    release_time = data['time']['version']
    if release_time:
        return release_time
    return None


def get_npm_latest_version(data):
    return data['dist-tags']['latest']

#add code here
def get_npm_current_version(requirement):
    pass