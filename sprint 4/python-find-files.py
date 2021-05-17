#protoype for getting source files for a language
import sys
from pathlib import Path

#copied from example on https://docs.python.org/3/library/pathlib.html
dir = sys.argv[1]
p = Path(dir)
files = list(p.glob('**/*.py'))
print(files)
