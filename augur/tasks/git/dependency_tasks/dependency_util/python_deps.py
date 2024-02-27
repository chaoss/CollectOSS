import re
from pathlib import Path
import ast


def get_files(path):
    # copied from example on https://docs.python.org/3/library/pathlib.html
    dir = path
    p = Path(dir)
    files = list(p.glob("**/*.py"))
    return files


def get_deps_for_file(path):
    try:
        return get_deps_for_file_ast(path)
    except Exception:
        return get_deps_for_file_simple_regex(path)

def get_deps_for_file_simple_regex(path):
    f = open(path, 'r',encoding="utf-8")

    matches = re.findall("import\s*(\w*)", f.read())
    f.close()
    return matches


def get_deps_for_file_ast(path):
    with open(path, "r", encoding="utf-8") as f:

        imports = set()

        # parse abstract syntax tree (ast)
        tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module
                if module_name:
                    imports.add(module_name)
    return imports
