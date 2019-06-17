import os
import subprocess
import time
from subprocess import Popen
import pytest
import requests

@pytest.fixture(scope="module")
def ghtorrent_routes():
    pass

def test_commits_route(ghtorrent_routes):
    response = requests.get('http://localhost:5000/api/unstable/rails/rails/timeseries/commits')
    assert response.status_code == 200