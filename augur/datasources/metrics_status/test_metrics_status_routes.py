import os
import pytest
import requests
import augur.server

def teardown_module(module):
    os.system('make dev-stop')

@pytest.fixture(scope="session")
def metrics_status():
    os.system('make dev-stop')
    os.system('make dev-start &')

def test_metrics_statu(metrics_status):
    result = requests.get('http://localhost:5000/api/unstable').json()
    assert result['status'] == 'OK'
