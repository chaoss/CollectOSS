from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from flask import render_template, flash, url_for, Flask
from .init import *
from ..server import app, db_session
from augur.application.config import AugurConfig
import urllib.request, urllib.error, json, os, math, yaml, urllib3, time, logging, re, math

from augur.application.db.session import DatabaseSession
from augur.application.db.engine import DatabaseEngine
from augur.application.db.models import User, Repo, RepoGroup, UserGroup, UserRepo
from sqlalchemy import Column, Table, Integer, MetaData, or_, Label
from sqlalchemy.sql.operators import ilike_op, distinct_op
from sqlalchemy.sql.functions import coalesce
from augur.application.db.models.base import Base

init_logging()

from .init import logger

config = AugurConfig(logger, db_session)

def parse_url(url):
    from urllib.parse import urlparse

    # localhost is not a valid host
    if "localhost" in url:
        url = url.replace("localhost", "127.0.0.1")
    
        if not url.startswith("http"):
            url = f"http://{url}"

    parts = urlparse(url)
    directories = parts.path.strip('/').split('/')
    queries = parts.query.strip('&').split('&')

    elements = {
        'scheme': parts.scheme,
        'netloc': parts.netloc,
        'path': parts.path,
        'params': parts.params,
        'query': parts.query,
        'fragment': parts.fragment
    }

    return elements, directories, queries

def validate_api_url(url):
    from urllib.parse import urlunparse

    parts = parse_url(url)[0]

    if not parts["scheme"]:
        parts["scheme"] = "http"

    staged_url = urlunparse(parts.values())

    def is_status_ok():
        try:
            with urllib.request.urlopen(staged_url) as request:
                response = json.loads(request.read().decode())
                if "status" in response:
                    return request.url
        except Exception as e:
            logger.error(f"Error during serving URL verification: {str(e)}")

        return False

    status = is_status_ok()
    if not status:
        if "/api/unstable" not in parts["path"]:
            # The URL does not point directly to the API
            # try once more with a new suffix
            parts["path"] = str(Path(parts["path"]).joinpath("api/unstable"))
            staged_url = urlunparse(parts.values())

            status = is_status_ok()
            if not status:
                # The URL does not point to a valid augur instance
                return ""
            else:
                return status
        else:
            return ""

    return status


""" ----------------------------------------------------------------
loadSettings:
    This function attempts to load the application settings from the config file
    (defined in init.py). It is assumed that the filename or file path defined
    during initialization is sufficient to locate the config file, and that the
    current process has read access to that file.

    If loading the config file fails, default settings are loaded via
    init_settings() and an attempt is made to write default settings to the
    provided config file.
"""
def loadSettings():
    global settings
    configFilePath = Path(configFile)
    if not configFilePath.is_file():
        init_settings()
        with open(configFile, 'w') as file:
            logger.info(f"Generating default configuration file: {configFile}")
            yaml.dump(settings, file)
            logger.info("Default configuration file successfully generated.")
    else:
        with open(configFilePath) as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)
    
    # # Ensure that the cache directory exists and is valid
    # cachePath = Path(settings["caching"])

    cachePath = Path.cwd() / "augur" / "static" / "cache"

    if not cachePath.is_dir():
        if cachePath.is_file():
            raise Exception(f"Cannot initialize caching: cache path [{cachePath}] is a file")
        else:
            try:
                cachePath.mkdir(parents=True)
                logger.info("cache directory initialized")
            except Exception as err:
                raise Exception(f"Cannot initialize caching: could not create cache directory [{cachePath}]")

    # Use the resolved path for cache directory access
    settings["caching"] = cachePath

    staged_url = validate_api_url(settings["serving"])
    if staged_url:
        settings["serving"] = re.sub("/$", "", staged_url)
        settings["valid"] = True
    else:
        settings["valid"] = False
        raise ValueError(f"The provided serving URL is not valid: {settings['serving']}")

""" ----------------------------------------------------------------
"""
def getSetting(key, section = "View"):
    if section == "View":
        if key == "serving":
            return "http://127.0.0.1:5000/api/unstable"
        return settings[key]
    else:
        return config.get_value(section, key)

loadSettings()

version_check(settings)

""" ----------------------------------------------------------------
"""
def loadReports():
    global reports
    try:
        with open(getSetting("reports")) as file:
            reports = yaml.load(file, Loader=yaml.FullLoader)
            id = -1
            for report in reports:
                for image in reports[report]:
                    image['id'] = id = id + 1
        return True
    except Exception as err:
        logger.error(f"An exception occurred reading reports endpoints from [{getSetting('reports')}]:")
        logger.error(err)
        try:
            with open(getSetting("reports"), 'w') as file:
                logger.info("Attempting to generate default reports.yml")
                yaml.dump(reports, file)
                logger.info("Default reports file successfully generated.")
        except Exception as ioErr:
            logger.error("Error creating default report configuration:")
            logger.error(ioErr)
        return False

if not loadReports():
    loadReports()
    
cache_files_requested = []

""" ----------------------------------------------------------------
"""
def cacheFileExists(filename):
    cache_file = Path(filename)
    if cache_file.is_file():
        if(getSetting('cache_expiry') > 0):
            cache_file_age = time.time() - cache_file.stat().st_mtime
            if(cache_file_age > getSetting('cache_expiry')):
                try:
                    cache_file.unlink()
                    logger.info(f"Cache file {filename} removed due to expiry")
                    return False
                except Exception as e:
                    logger.error("Error: cache file age exceeds expiry limit, but an exception occurred while attempting to remove")
                    logger.error(e)
        return True
    else:
        return False

def stripStatic(url):
    return url.replace("static/", "")

""" ----------------------------------------------------------------
"""
def toCacheFilename(endpoint, append = True):
    return endpoint.replace("/", ".").replace("?", "_").replace("=", "_") + ('.agcache' if append else "")

def toCacheFilepath(endpoint, append = True):
    return getSetting('caching').joinpath(toCacheFilename(endpoint, append))

def toCacheURL(endpoint):
    return getSetting('approot') + str(toCacheFilepath(endpoint))

""" ----------------------------------------------------------------
requestJson:
    Attempts to load JSON data from cache for the given endpoint.
    If no cache file is found, a request is made to the URL for
    the given endpoint and, if successful, the resulting JSON is
    cached for future use. Cached files will be stored with all
    '/' characters replaced with '.' for filesystem compatibility.

@PARAM:     endpoint: String
        A String representation of the requested
        json endpoint (relative to the api root).

@RETURN:    data: JSON
        An object representing the JSON data read
        from either the cache file or the enpoint
        URL. Will return None if an error isreturn None
        encountered.
"""
def requestJson(endpoint, cached = True):
    filename = toCacheFilepath(endpoint)
    requestURL = getSetting('serving') + "/" + endpoint
    logger.info(f'requesting json from: {endpoint}')
    try:
        if cached and cacheFileExists(filename):
            with open(filename) as f:
                data = json.load(f)
        else:
            with urllib.request.urlopen(requestURL) as url:
                if url.getcode() != 200:
                    raise urllib.error.HTTPError(code = url.getcode())

                data = json.loads(url.read().decode())

                if cached:
                    with open(filename, 'w') as f:
                        json.dump(data, f)
        if filename in cache_files_requested:
            cache_files_requested.remove(filename)
        return data
    except Exception as err:
        logger.error("An exception occurred while fulfilling a json request")
        logger.error(err)
        return False, str(err)

""" ----------------------------------------------------------------
"""
def requestPNG(endpoint):
    filename = toCacheFilepath(endpoint)
    requestURL = getSetting('serving') + "/" + endpoint
    try:
        if cacheFileExists(filename):
            return toCacheURL(endpoint)
        else:
            urllib.request.urlretrieve(requestURL, filename)
        if filename in cache_files_requested:
            cache_files_requested.remove(filename)
        return toCacheURL(endpoint)
    except Exception as err:
        logger.error("An exception occurred while fulfilling a png request")
        logger.error(err)

""" ----------------------------------------------------------------
"""
def download(url, cmanager, filename, image_cache, image_id, repo_id = None):
    image_cache[image_id] = {}
    image_cache[image_id]['filename'] = filename
    filename = toCacheFilepath(filename, False)
    if cacheFileExists(filename):
        image_cache[image_id]['exists'] = True
        return
    try:
        response = cmanager.request('GET', url)
    except Exception as e:
        logger.error("Could not make request: " + str(e))
        raise e
    
    if "json" in response.headers['Content-Type']:
        logger.warn(f"repo {repo_id}: unexpected json response in image request")
        logger.warn(f"  response: {response.data.decode('utf-8')}")
        image_cache[image_id]['exists'] = False
        return
    if response and response.status == 200:
        image_cache[image_id]['exists'] = True
        try:
            with open(filename, 'wb') as f:
                logger.info("Writing image: " + str(filename))
                f.write(response.data)
        except Exception as err:
            logger.error("An exception occurred writing a cache file to disk")
            logger.error(err)

""" ----------------------------------------------------------------
"""
def requestReports(repo_id):
    # If this request has already been fulfilled, no need to process it again
    if(repo_id in report_requests.keys()):
        return

    # initialize a new request entry to hold the resulting data
    report_requests[repo_id] = {}
    report_requests[repo_id]['complete'] = False

    host = getSetting("host", "Server")
    port = getSetting("port", "Server")

    """ ----------
        If the report definition could not be loaded, we cannot determine what
        files to request from the backend to compose the report. Returning here
        causes the completion status of the request to be False, which will
        display an error message when sent to the frontend.
    """
    if reports is None:
        return

    threadPools = []
    reportImages = {}
    for report in reports:
        # Reports is a dictionary of lists, so we get the size of each list
        size = len(reports[report])

        # Set up various threading components to manage image downloading
        connection_mgr = urllib3.PoolManager(maxsize=size)
        thread_pool = ThreadPoolExecutor(size)
        threadPools.append(thread_pool)

        for image in reports[report]:
            # Where should the downloaded image be stored (in cache)
            filename = toCacheFilename(f"{image['url']}?repo_id={repo_id}")
            # Where are we downloading the image from
            image_url = f"{host}:{port}" + url_for(image['url'], repo_id = repo_id)
            # f"{getSetting('serving')}/{image['url']}?repo_id={repo_id}"
            
            # Add a request for this image to the thread pool using the download function
            thread_pool.submit(download, image_url, connection_mgr, filename, reportImages, image['id'], repo_id)

    # Wait for all connections to resolve, then clean up
    for thread_pool in threadPools:
        thread_pool.shutdown()

    report_requests[repo_id]['images'] = reportImages

    # Remove the request from the queue when completed
    report_requests[repo_id]['complete'] = True

""" ----------------------------------------------------------------
renderRepos:
    This function renders a list of repos using a given view, while passing query
    data along. This function also processes pagination automatically for the
    range of data provided. If a query is provided and filtering is enabled, the
    data will be filtered using the 'repo_name', 'repo_group_id' or 'rg_name'.
@PARAM:     view: String
        A string representing the template to use for displaying the repos.
@PARAM:     query: String
        The query argument from the previous page.
@PARAM:     data: Dictionary
        The repo data to display on the page
@PARAM:     sorting: String = None
        The key in the data to sort by
@PARAM:     rev: Boolean = False
        Determines if the sorted data should be displayed in descending order
@PARAM:     page: String = None
        The current page to use within pagination
@PARAM:     filter: Boolean = False
        Filter data using query
@PARAM:     pageSource: String = "repos/views/table"
        The base url to use for the page links
"""
def renderRepos(view, query, data, sorting = None, rev = False, page = None, filter = False, pageSource = "repo_table_view", sortBasis = None):
    pagination_offset = getSetting('pagination_offset')
    
    """ ----------
        If the data does not exist, we cannot construct the table to display on
        site. Rendering the table module without data displays an error message
    """
    if(data is None):
        return render_template('index.j2', body="repos-" + view, title="Repos")

    # If a query exists and filtering is set to true, attempt to filter the data
    if((query is not None) and filter):
        results = []
        for repo in data:
            if (query in repo["repo_name"]) or (query == str(repo["repo_group_id"])) or (query in repo["rg_name"]):
                results.append(repo)
        data = results

    # Determine the maximum number of pages which can be displayed from the data
    pages = math.ceil(len(data) / pagination_offset)

    if page is not None:
        page = int(page)
    else:
        page = 1

    """ ----------
        Caller requested sorting of the data. The data is a list of dictionaries
        with numerous sortable elements, and the "sorting" parameter is assumed
        to be the key of the desired element in the dictionary by which to sort.

        We need the "or 0" here to ensure the comparison is valid for rows which
        do not have data for the requested column (we're making the assumption
        that the data type is comparable to integer 0).
    """
    if sorting is not None:
        try:
            data = sorted(data, key = lambda i: i[sorting] or 0, reverse = rev)
        except Exception as e:
            flash("An error occurred during sorting")
            logger.error(str(e))

    """ ----------
        Here we extract a subset of the data for display on the site. First we
        calculate the start index within the data of our current "page" (x),
        then we index to that position plus the pagination offset (or page size)
        defined above. The result is a list which contains *at most* a number of
        entries equal to the pagination offset
    """
    x = pagination_offset * (page - 1)
    data = data[x: x + pagination_offset]

    return render_module("repos-" + view, title="Repos", repos=data, query_key=query, activePage=page, pages=pages, offset=pagination_offset, PS=pageSource, reverse = rev, sorting = sorting)

""" ----------------------------------------------------------------
    Renders a simple page with the given message information, and optional page
    title and redirect
"""
def render_message(messageTitle, messageBody = None, title = None, redirect = None, pause = None, **kwargs):
    return render_module("notice", messageTitle=messageTitle, messageBody=messageBody, title=title, redirect=redirect, pause=pause, **kwargs)

""" ----------------------------------------------------------------
"""
def render_module(module, **args):
    # args.setdefault("title", "Augur View")
    args.setdefault("api_url", getSetting("serving"))
    args.setdefault("body", module)

    if not getSetting("valid"):
        args.setdefault("invalid", True)

    return render_template('index.j2', **args)

""" ----------------------------------------------------------------
    No longer used
"""
# My attempt at a loading page
def renderLoading(dest, query, request):
    cache_files_requested.append(request)
    return render_template('index.j2', body="loading", title="Loading", d=dest, query_key=query, api_url=getSetting('serving'))

with DatabaseEngine() as engine:
    augur_data_schema = MetaData(schema = "augur_data")
    augur_data_schema.reflect(bind = engine, views = True)
    
    commits_materialized_view: Table = augur_data_schema.tables["augur_data.api_get_all_repos_commits"]
    issues_materialized_view: Table = augur_data_schema.tables["augur_data.api_get_all_repos_issues"]

""" ----------------------------------------------------------------
"""
def load_repos_test(count = False, source = None, **kwargs):
    columns: list[Label] = [
        Repo.repo_id.distinct().label("repo_id"),
        Repo.description.label("description"),
        Repo.repo_git.label("url"),
        coalesce(commits_materialized_view.columns.commits_all_time, 0).label("commits_all_time"),
        coalesce(issues_materialized_view.columns.issues_all_time, 0).label("issues_all_time"),
        RepoGroup.rg_name.label("rg_name"),
        Repo.repo_git.regexp_replace('.*github\.com\/[A-Za-z0-9 \- _]+\/([A-Za-z0-9 \- _ .]+)$', "\\1").label("repo_name"),
        Repo.repo_git.regexp_replace('.*github\.com\/([A-Za-z0-9 \- _]+)\/[A-Za-z0-9 \- _ .]+$', "\\1").label("repo_owner"),
        RepoGroup.repo_group_id.label("repo_group_id")
    ]
    
    def get_colum_by_label(label: str)-> Label:
        for column in columns:
            if column.name == label:
                return column
    
    repos = db_session.query(*columns)\
        .outerjoin(commits_materialized_view, Repo.repo_id == commits_materialized_view.columns.repo_id)\
        .outerjoin(issues_materialized_view, Repo.repo_id == issues_materialized_view.columns.repo_id)\
        .join(RepoGroup, Repo.repo_group_id == RepoGroup.repo_group_id)
    
    user: User = kwargs.get("user")
    if user:
        repos = repos.join(UserRepo, Repo.repo_id == UserRepo.repo_id)\
            .join(UserGroup, UserGroup.group_id == UserRepo.group_id)\
            .filter(UserGroup.user_id == user.user_id)
    
    search = kwargs.get("search")
    qkey = kwargs.get("query_key") or ["repo_name", "repo_owner"]
    if search:
        if isinstance(qkey, list) and len(qkey) > 0:
            repos = repos.filter(or_(ilike_op(get_colum_by_label(filter_column), f"%{search}%") for filter_column in qkey))
        else:
            repos = repos.filter(ilike_op(get_colum_by_label(qkey), f"%{search}%"))
    
    page_size: int = kwargs.get("page_size") or 25
    if count:
        c = repos.count()
        return math.ceil(c / page_size) - 1
            
    page: int = kwargs.get("page") or 0
    offset = page * page_size
    
    return repos.slice(offset, offset + page_size)