from distutils import version
import requests
import dateutil.parser
# from packaging import version
from distutils.version import LooseVersion
import re 


def get_pypi_data(name, version=None):
    """return a dictionary with pypi project data"""
    url = "https://pypi.org/pypi/%s/json" % name
    if version:
        url = "https://pypi.org/pypi/%s/%s/json" % (name, version)
    r = requests.get(url)
    if r.status_code < 400:
        return r.json()
    return {}


def clean_version(version):
    version = [v for v in version if v.isdigit() or v == '.']
    return ''.join(version)


def get_version(pypi_data, version, lt=False):
    if not version:
        return None

    orig_ver = version
    releases = pypi_data['releases']
    if version not in releases:
        version_data = get_pypi_data(pypi_data['info']['name'], version=version)
        version = version_data.get('info', {}).get('version')
    if lt:
        releases = [(r, rd[-1]['upload_time_iso_8601']) for r, rd in releases.items() if rd]
        releases = sorted(releases, key=lambda x: x[1], reverse=True)
        releases = [r for r, rd in releases]
        if version is None:
            curr_ver = LooseVersion(clean_version(orig_ver))
            releases_float = [clean_version(r) for r in releases]
            releases_float = [r for r in releases_float if LooseVersion(r) >= curr_ver]
            return releases[len(releases_float)]

        idx = releases.index(version)
        if idx < len(releases) - 1:
            return releases[idx + 1]
    return version


def handle_upper_limit_dependency(dependency, data):
    versions = dependency['requirement'].split(',')
    upper_limit = clean_version(versions[0])
    lower_limit = clean_version(versions[1])
    release_list = list(data['releases'])

    if upper_limit not in release_list:
        upper_limit += '.0'
    # print('the upper limit and lower limit is %s and %s' %(upper_limit,lower_limit))
    upper_index = release_list.index(upper_limit)
    return release_list[upper_index -1]
    # return get_version(data, upper_limit, lt= True)


def get_latest_version(data):
    # dict_list = list(data['releases'])
    # return dict_list[-1]
    return data['info']['version']


def get_release_date(data, version):
    if not data:
        print('invalid data')
        return None
    releases = data['releases']
    name = data['info']['name']
    try:
        version_date = releases[version][-1]['upload_time_iso_8601']
    except IndexError:
        print(f'Used release of {name}=={version} has no upload time.')
        return None    
    # version_date = dateutil.parser.parse(version_date)
    return version_date


def sort_dependency_requirement(dependency,data):
    if dependency['requirement'] == '' or dependency['requirement'] is None or dependency['requirement'] == '*':
        return None

    elif re.search(r'<', dependency['requirement']):
        return handle_upper_limit_dependency(dependency, data)

    elif re.search(r'>=', dependency['requirement']):
        return None

    else:
        # return get_version(data, clean_version(dependency['requirement']))
        return clean_version(dependency['requirement'])