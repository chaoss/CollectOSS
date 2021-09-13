from distutils.version import LooseVersion
import dateutil.parser
from distutils import version
import os
from pypi_parser import parse_conda, parse_pipfile,parse_pipfile_lock,parse_poetry,parse_poetry_lock,parse_requirement_txt,parse_setup_py
from npm_parser import parse_package_json
from pypi_libyear_util import sort_dependency_requirement,get_pypi_data,get_latest_version,get_release_date
from npm_libyear_utils import get_NPM_data, get_npm_release_date, get_npm_latest_version,get_npm_current_version

#Files That would be parsed should be added here
file_list = [
    'Requirement.txt',
    'setup.py',
    'Pipfile',
    'Pipfile.lock',
    'pyproject.toml',
    'poetry.lock',
    'environment.yml',
    'environment.yaml',
    'environment.yml.lock',
    'environment.yaml.lock'
]


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def get_parsed_deps(path):

    deps_file = None
    dependency_list = list()

    for f in file_list:
        deps_file = find(f, path)
        if not deps_file:
            continue
        file_handle= open(deps_file)

        if f == 'Requirement.txt':
            dependency_list = parse_requirement_txt(file_handle)

        elif f == 'setup.py':
            dependency_list = parse_setup_py(file_handle)

        elif f == 'Pipfile':
            dependency_list = parse_pipfile(file_handle)

        elif f == 'Pipfile.lock':
            dependency_list = parse_pipfile_lock(file_handle)

        elif f == 'pyproject.toml':
            dependency_list = parse_poetry(file_handle)

        elif f == 'poetry.lock':
            dependency_list = parse_poetry_lock(file_handle)

        elif f == 'environment.yml':
            dependency_list = parse_conda(file_handle)

        elif f == 'environment.yaml':
            dependency_list = parse_conda(file_handle)

        elif f == 'environment.yml.lock':
            dependency_list = parse_conda(file_handle)

        elif f == 'environment.yaml.lock':
            dependency_list = parse_conda(file_handle)                
        return dependency_list


def get_libyear(current_version, current_release_date, latest_version, latest_release_date):

    if not latest_version:
        return -1
    
    if not latest_release_date:
        return -1

    if not current_version:
        return 0

    current_release_date= dateutil.parser.parse(current_release_date)
    latest_release_date = dateutil.parser.parse(latest_release_date)    

    libdays = (latest_release_date - current_release_date).days
    print(libdays)
    libyear = libdays/365
    return libyear


def get_deps_libyear_data(path):
    current_release_date = None
    libyear = None

    dependencies = get_parsed_deps(path)
    if dependencies:
        for dependency in dependencies:
            #NOTE: Add new if for new package parser
            if dependency['package'] == 'PYPI':
                data = get_pypi_data(dependency['name'])
                current_version = sort_dependency_requirement(dependency,data)
                latest_version = get_latest_version(data)
                latest_release_date = get_release_date(data, latest_version)
                if current_version:
                    current_release_date = get_release_date(data, current_version)
            elif dependency['package'] == 'NPM':
                data = get_NPM_data(dependency['name'])
                current_version = get_npm_current_version(dependency['requirement'])
                latest_version = get_npm_latest_version(data)
                latest_release_date = get_npm_release_date(data, latest_version)
                if current_version:
                    current_release_date = get_npm_release_date(data, current_version)

            libyear = get_libyear(current_version, current_release_date, latest_version, latest_release_date)
            if not latest_release_date:
                latest_release_date = dateutil.parser.parse('1970-01-01 00:00:00')
                libyear = -1

            if not latest_version:
                latest_version = 'unspecified'     

            if not current_version:
                current_version = latest_version
                current_release_date = latest_release_date

            if not dependency['requirement']:
                dependency['requirement'] = 'unspecified'    

            dependency['current_version'] = current_version    
            dependency['latest_version'] = latest_version
            dependency['current_release_date'] = current_release_date
            dependency['latest_release_date'] = latest_release_date
            dependency['libyear'] = libyear

        return dependencies 