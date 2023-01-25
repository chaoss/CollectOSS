import sys
import re
from pathlib import Path
import codecs

def get_files(path):
	#copied from example on https://docs.python.org/3/library/pathlib.html
	dir = path
	p = Path(dir)
	files = list(p.glob('**/*.py'))
	return files
	
def get_deps_for_file(path):
	f = open(path, 'r',encoding="utf-8")

	matches = re.findall("import\s*(\w*)", f.read())
	f.close()
	return matches
