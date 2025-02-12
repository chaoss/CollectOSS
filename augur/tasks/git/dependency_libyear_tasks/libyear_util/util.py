import dateutil.parser
import os
from augur.tasks.git.dependency_libyear_tasks.libyear_util.pypi_parser import parse_conda, parse_pipfile,parse_pipfile_lock,parse_poetry,parse_poetry_lock,parse_requirement_txt,parse_setup_py
from augur.tasks.git.dependency_libyear_tasks.libyear_util.npm_parser import parse_package_json
from augur.tasks.git.dependency_libyear_tasks.libyear_util.pypi_libyear_util import sort_dependency_requirement,get_pypi_data,get_latest_version,get_release_date
from augur.tasks.git.dependency_libyear_tasks.libyear_util.npm_libyear_utils import get_NPM_data, get_npm_release_date, get_npm_latest_version,get_npm_current_version

#Files That would be parsed should be added here
file_list = [
    'Requirement.txt',
    'requirements.txt',
    'setup.py',
    'Pipfile',
    'Pipfile.lock',
    'pyproject.toml',
    'poetry.lock',
    'environment.yml',
    'environment.yaml',
    'environment.yml.lock',
    'environment.yaml.lock',
    'package.json'
]


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def get_parsed_deps(path,logger):

    deps_file = None
    dependency_list = list()
    for f in file_list:
        deps_file = find(f, path)

        if not deps_file or not f:
            continue
        file_handle= open(deps_file)

        short_file_name = os.path.split(deps_file)[-1]

        if short_file_name == 'Requirement.txt':
            dependency_list.extend(parse_requirement_txt(file_handle))
        
        if short_file_name == 'requirements.txt':
            dependency_list.extend(parse_requirement_txt(file_handle))

        if short_file_name == 'setup.py':
            dependency_list.extend(parse_setup_py(file_handle))

        if short_file_name == 'Pipfile':
            dependency_list.extend(parse_pipfile(file_handle))

        if short_file_name == 'Pipfile.lock':
            dependency_list.extend(parse_pipfile_lock(file_handle))

        if short_file_name == 'pyproject.toml':
            dependency_list.extend(parse_poetry(file_handle))

        if short_file_name == 'poetry.lock':
            dependency_list.extend(parse_poetry_lock(file_handle))

        if short_file_name == 'environment.yml':
            dependency_list.extend(parse_conda(file_handle))

        if short_file_name == 'environment.yaml':
            dependency_list.extend(parse_conda(file_handle))

        if f == 'environment.yml.lock':
            dependency_list.extend(parse_conda(file_handle))

        if short_file_name == 'environment.yaml.lock':
            dependency_list.extend(parse_conda(file_handle)) 
            
        if short_file_name == 'package.json':
            try:
                dependency_list.extend(parse_package_json(file_handle))
            except KeyError as e:
                logger.error(f"package.json for repo at path {path} is missing required key: {e}\n Skipping file...")

        
    return dependency_list


def get_libyear(current_version, current_release_date, latest_version, latest_release_date):

    if not latest_version:
        return -1
    
    if not latest_release_date:
        return -1

    if not current_version or not current_release_date or not isinstance(current_release_date, str):
        return 0

    current_release_date= dateutil.parser.parse(current_release_date)
    latest_release_date = dateutil.parser.parse(latest_release_date)    

    libdays = (latest_release_date - current_release_date).days
    print(libdays)
    libyear = libdays/365
    return libyear


def get_deps_libyear_data(path, logger):
    current_release_date = None
    libyear = None

    dependencies = get_parsed_deps(path,logger)
    if dependencies:
        for dependency in dependencies:

            #NOTE: Add new if for new package parser
            if dependency['package'] == 'PYPI':
                data = get_pypi_data(dependency['name'])
                try:
                    current_version = sort_dependency_requirement(dependency,data)
                except (KeyError, TypeError) as e:
                    logger.error(f"Could not get current version of dependency for path {path}.\n  Dependency: {dependency}")
                    current_version = None
                try:
                    latest_version = get_latest_version(data)
                    
                except KeyError:
                    logger.error(f"Could not get current version of dependency for path {path}.\n  Dependency: {dependency}")
                    latest_version = None
                
                try:
                    if latest_version:
                        latest_release_date = get_release_date(data, latest_version,logger)
                    else:
                        latest_release_date = None
                except KeyError:
                    logger.error(f"Could not get current date of dependency for path {path} with version {latest_version}.\n  Dependency: {dependency}")
                    latest_release_date = None
                
                if current_version:
                    current_release_date = get_release_date(data, current_version,logger)

            elif dependency['package'] == 'NPM':
                data = get_NPM_data(dependency['name'])
                current_version = get_npm_current_version(data, dependency['requirement'])
                try:
                    latest_version = get_npm_latest_version(data)
                except KeyError:
                    logger.error(f"Could not get latest version of dependency for path {path}.\n  Dependency: {dependency}")
                    latest_version = None

                try:
                    if latest_version:
                        latest_release_date = get_npm_release_date(data, latest_version)
                    else:
                        latest_release_date = None
                except KeyError:
                    logger.error(f"Could not get latest version of dependency for path {path}.\n  Dependency: {dependency}")
                    latest_release_date = None

                if current_version:
                    try:
                        current_release_date = get_npm_release_date(data, current_version)
                    except KeyError:
                        logger.error(f"Could not get latest version of dependency for path {path}.\n  Dependency: {dependency}")
                        current_release_date = dateutil.parser.parse('1970-01-01 00:00:00')

            
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

        return [d for d in dependencies if d] 