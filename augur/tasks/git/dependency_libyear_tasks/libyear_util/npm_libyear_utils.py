import requests
import logging
import traceback

""" _summary_

    This module provides utility functions to interact with the NPM registry.
    It includes functions to fetch package data, clean and split version strings,
    and determine the latest versions of packages based on semantic versioning.
    The functions handle errors and log warnings or errors as appropriate.
    Functions:
        - get_NPM_data: Fetches package data from the NPM registry.     
        - clean_version: Cleans a version string by removing non-numeric characters.
        - split_version: Splits a version string into major, minor, and patch components.
        - get_latest_patch: Gets the latest patch version for a given version.
        - get_lastest_minor: Gets the latest minor version for a given version.
        - get_npm_release_date: Gets the release date for a specific version.
        - get_npm_latest_version: Gets the latest version from the package data.
        - get_npm_current_version: Determines the current version based on a requirement.
    Specific improvements in May, 2025 update: 
    	•	Gracefully handles:
            •	Missing versions key
            •	Malformed or missing version strings
            •	Network errors and malformed responses
        •	Provides safe fallbacks like 'unspecified' instead of crashing
        •	Adds thorough logging (warnings and errors) for debug tracing
        •	Prevents crash loops caused by invalid/missing data from NPM
    """

logger = logging.getLogger(__name__)


def get_NPM_data(package):
    url = f"https://registry.npmjs.org/{package}"
    try:
        r = requests.get(url)
        if r.status_code < 400:
            data = r.json()
            if 'versions' not in data:
                logger.warning(f"[NPM] Package '{package}' fetched but missing 'versions'. Possibly deprecated or unpublished.")
            return data
        else:
            logger.warning(f"[NPM] Failed to fetch data for package '{package}'. HTTP Status: {r.status_code}")
            return {}
    except Exception as e:
        logger.error(f"[NPM] Exception while fetching data for '{package}': {e}")
        return {}


def clean_version(version):
    version = [v for v in version if v.isdigit() or v == '.']
    return ''.join(version)


def split_version(version):
    try:
        version_list = version.split('.')
        patch = version_list.pop(-1)
        minor = version_list.pop(-1)
        major = version_list[0]
        return major, minor, patch
    except Exception as e:
        logger.error(f"[NPM] Failed to split version '{version}': {e}")
        return "0", "0", "0"


def get_latest_patch(version, data):
    if 'versions' not in data:
        logger.error(f"[NPM] 'versions' key not found in the data. Cannot get latest patch for version {version}")
        raise KeyError("'versions' key not found")

    versions = data['versions']
    if version not in versions:
        logger.warning(f"[NPM] Base version '{version}' not found in versions list for latest patch resolution")
        return version

    major, minor, patch = split_version(version)
    consider_version = version
    for v in versions.keys():
        parts = v.split('.')
        if len(parts) >= 3 and parts[0] == major and parts[1] == minor and parts[2] > patch:
            consider_version = v
    return consider_version


def get_lastest_minor(version, data):
    if 'versions' not in data:
        logger.error(f"[NPM] 'versions' key not found in the data. Cannot get latest minor version")
        raise KeyError("'versions' key not found")

    versions = data['versions']
    if version not in versions:
        logger.warning(f"[NPM] Base version '{version}' not found in versions list for latest minor resolution")
        return version

    major, minor, patch = split_version(version)
    consider_version = get_latest_patch(version, data)

    for v in versions.keys():
        parts = v.split('.')
        if len(parts) >= 2 and parts[0] == major and parts[1] > minor:
            consider_version = v
    return consider_version


def get_npm_release_date(data, version):
    try:
        release_time = data.get('time', {}).get(version)
        if release_time:
            return release_time
        else:
            logger.warning(f"[NPM] Release time not found for version '{version}'")
            return None
    except Exception as e:
        logger.error(f"[NPM] Error retrieving release date for version '{version}': {e}")
        return None


def get_npm_latest_version(data):
    try:
        return data.get('dist-tags', {}).get('latest', 'unspecified')
    except Exception as e:
        logger.warning(f"[NPM] Error getting latest version from dist-tags: {e}")
        return 'unspecified'


def get_npm_current_version(data, requirement):
    if not requirement:
        logger.warning(f"[NPM] No version requirement provided; defaulting to 'unspecified'")
        return 'unspecified'

    if 'versions' not in data:
        logger.error(f"[NPM] Cannot determine current version; 'versions' key missing. Requirement: {requirement}, Data keys: {list(data.keys())}")
        return 'unspecified'

    try:
        if requirement.startswith('~'):
            return get_latest_patch(clean_version(requirement), data)
        elif requirement.startswith('^'):
            return get_lastest_minor(clean_version(requirement), data)
        else:
            return requirement
    except Exception as e:
        logger.warning(f"[NPM] Failed to parse version requirement '{requirement}' in data. Error: {e}")
        return 'unspecified'