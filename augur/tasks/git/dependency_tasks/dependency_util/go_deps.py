import re
from pathlib import Path

def get_files(path):
    dir = path
    p = Path(dir)
    files = list(p.glob('**/*.go'))
    return files

def get_deps_for_file(path):
    with open(path, 'r') as f:
        matches = re.findall('import\s+\(([\s\S]*?)\)', f.read())
        if matches:
            imports = []
            for m in matches:
                imports += re.findall('(\w+)', m)
            return imports
        else:
            matches = re.findall('import\s+"(\w+)"', f.read())
            if matches:
                return matches
            else:
                return []

