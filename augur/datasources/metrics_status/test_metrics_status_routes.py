import pytest
import requests

@pytest.fixture(scope="module")
def metrics_status():
    pass

def test_api_status(metrics_status):
    result = requests.get('http://localhost:5000/api/unstable').json()
    assert result['status'] == 'OK'
