import os
import subprocess
import time
from subprocess import Popen
import pytest
import requests

@pytest.fixture(scope="session")
def librariesio_routes():
    process = subprocess.Popen(['make', 'backend-restart'])
    time.sleep(5)
    return process
