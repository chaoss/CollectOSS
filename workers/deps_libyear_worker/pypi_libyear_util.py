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