import importlib

route_files = ['downloads', 'facade', 'ghtorrent', 'ghtorrentplus', 'git', 'githubapi', 'librariesio', 'publicwww']

def create_all_routes(server):
    for route_file in route_files:
        try:
            module = importlib.import_module('.' + route_file, 'augur.routes')
            module.create_routes(server)
        except Exception as e:
            pass