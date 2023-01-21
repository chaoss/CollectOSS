import sys
import re
from pathlib import Path

def get_files(path):
	#copied from example on https://docs.python.org/3/library/pathlib.html
	dir = path
	p = Path(dir)
	files = list(p.glob('**/*.cs'))
	return files
	
def get_deps_for_file(path):
	f = open(path, 'r')
	matches = re.findall("using\s*(\w*)\s*;", f.read())
	f.close()
	return matches
