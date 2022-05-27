import json

def map_dependencies(dict, key, type):
    deps = list()
    if not dict:
        return []
    for name, info in dict[key].items():
        Dict = {'name': name, 'requirement': info, 'type': type, 'package': 'NPM'}
        deps.append(Dict)
    return deps


def parse_package_json(file_handle):
    manifest = json.load(file_handle)
    return map_dependencies(manifest, 'dependencies', 'runtime') + map_dependencies(manifest, 'devDependencies', 'development')


# def parse_package_lock(file_handle):

