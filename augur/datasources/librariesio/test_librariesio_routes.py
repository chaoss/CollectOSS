import os
import pytest
import requests
import augur.server

def teardown_module(module):
    os.system('make dev-stop')

@pytest.fixture(scope="session")
def librariesio_routes():
    os.system('make dev-stop')
    os.system('make dev-start &')