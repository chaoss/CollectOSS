import pytest
import augur

@pytest.fixture(scope="session")
def metrics():
    augur_app = augur.Application()
    return augur_app.metrics
