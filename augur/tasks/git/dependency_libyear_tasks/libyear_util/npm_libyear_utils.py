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

def split_version(version):
    #Split version string into list seperated by .
    #assign elements of list to respective variables.
    version_list = list(version.split('.'))
    patch = version_list.pop(-1)
    minor = version_list.pop(-1)
    major = version_list[0]

    return major,minor,patch



def get_latest_patch(version, data):
    versions = data['versions']
    try:
        index = list(versions.keys()).index(version)
    except ValueError as e:
        raise e
    
    major,minor,patch = split_version(version)
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
    except ValueError as e:
        raise e

    major,minor,patch = split_version(version)
    
    consider_version = get_latest_patch(version, data)
    for v in list(versions.keys())[index:]:
        if v.split('.')[0]==major:
            if v.split('.')[1]>minor:
                    consider_version = v
    return consider_version 


def get_npm_release_date(data, version):
    release_time = data['time'][version]
    if release_time:
        return release_time
    return None


def get_npm_latest_version(data):
    return data['dist-tags']['latest']

#add code here
def get_npm_current_version(data, requirement):
    if requirement[0]=='~':
        try:
            return get_latest_patch(clean_version(requirement), data)
        except ValueError:
            return None
    elif requirement[0]=='^':
        try:
            return get_lastest_minor(clean_version(requirement), data)
        except ValueError:
            return None
    else:
        return requirement
