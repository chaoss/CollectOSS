import re, os
import json
from typing import Dict
import toml 
import dateutil.parser
from pypi_libyear_util import sort_dependency_requirement,get_pypi_data,get_latest_version,get_release_date
from pypi_libyear_util import get_libyear


INSTALL_REGEXP = r'install_requires\s*=\s*\[([\s\S]*?)\]'
REQUIRE_REGEXP = r'([a-zA-Z0-9]+[a-zA-Z0-9\-_\.]+)([><=\w\.,]+)?'
REQUIREMENTS_REGEXP = '^#{REQUIRE_REGEXP}'
MANIFEST_REGEXP = r'.*require[^\/]*(\/)?[^\/]*\.(txt|pip)$'

install_regrex = re.compile(INSTALL_REGEXP)
require_regrex = re.compile(REQUIRE_REGEXP)
requirement_regrex = re.compile(REQUIREMENTS_REGEXP)