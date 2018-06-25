# Metadata
from .metadata import __version__

# Functions
from .util import logger

# Classes
from .application import Application

def data_sources():
    from .downloads import Downloads
    from .ghtorrent import GHTorrent
    from .ghtorrentplus import GHTorrentPlus
    from .git import Git
    from .githubapi import GitHubAPI
    from .librariesio import LibrariesIO
    from .localcsv import LocalCSV
    from .publicwww import PublicWWW
    from .server import Server
    return [Downloads, GHTorrent, GHTorrentPlus, Git, GitHubAPI, LibrariesIO, LocalCSV, PublicWWW, Server]
