import sys
import re
from pathlib import Path

def get_files(path):
	#copied from example on https://docs.python.org/3/library/pathlib.html
	dir = path
	p = Path(dir)
	files = list(p.glob('**/*.rb'))
	return files
	
def get_deps_for_file(path):
	f = open(path, 'r')
	matches = re.findall('require\s*"(.*)"', f.read())
	f.seek(0)
	matches = re.findall('require_relative\s*"(.*)"', f.read())
	f.close()
	return matches
