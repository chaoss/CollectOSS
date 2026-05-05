import re
from pathlib import Path

def get_files(path):
    p = Path(path)
    files = list(p.glob('**/*.kt'))
    return files

def get_deps_for_file(path):
    with open(path, 'r') as f:
        content = f.read()
        matches = re.findall('import\s+(.*?)(?:;|\n)', content, re.DOTALL)
        imports = []
        for m in matches:
            m = m.strip().replace('\n', ' ')
            if m.startswith('import '):
                m = m[len('import '):]
            if 'as ' in m:
                m = m.split('as ')[0]
            imports += re.findall(r'[\w\.]+', m)
        return imports

