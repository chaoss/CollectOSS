import re
from pathlib import Path

def get_files(path):
    #copied from example on https://docs.python.org/3/library/pathlib.html
    dir = path
    p = Path(dir)
    files = list(p.glob('**/*.rs'))
    return files

def get_deps_for_file(path):
    #gets imports in specified file path.
    with open(path, 'r') as f:
        content = f.read()
        matches = re.findall(r'use\s+([\w:]+)(\s+as\s+([\w:]+))?(\s*\*\s*)?(;|\n)', content)
        imports = []
        for m in matches:
            import_path = m[0]
            imports.append(import_path)
        return imports