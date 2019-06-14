import os
import subprocess
import time
from subprocess import Popen
import pytest
import requests

@pytest.fixture(scope="session")
def metrics_status():
    process = subprocess.Popen(['make', 'backend-restart'])
    time.sleep(5)
    return process

def test_api_status(metrics_status):
    result = requests.get('http://localhost:5000/api/unstable').json()
    assert result['status'] == 'OK'
