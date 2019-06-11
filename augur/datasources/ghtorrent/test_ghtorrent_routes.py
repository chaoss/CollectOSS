import os
import pytest
import requests
import augur.server

def teardown_module(module):
    os.system('make dev-stop')

@pytest.fixture(scope="session")
def ghtorrent_routes():
    os.system('make dev-stop')
    os.system('make dev-start &')

def test_commits_route(ghtorrent_routes):
    response = requests.get('http://localhost:5000/api/unstable/rails/rails/timeseries/commits')
    assert response.status_code == 200