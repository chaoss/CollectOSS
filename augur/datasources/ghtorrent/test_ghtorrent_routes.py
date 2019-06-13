import os
import subprocess
import time
from subprocess import Popen
import pytest
import requests

@pytest.fixture(scope="session")
def ghtorrent_routes():
    process = subprocess.Popen(['make', 'backend-restart'])
    time.sleep(5)
    return process

def test_commits_route(ghtorrent_routes):
    response = requests.get('http://localhost:5000/api/unstable/rails/rails/timeseries/commits')
    assert response.status_code == 200