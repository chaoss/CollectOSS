import pytest

@pytest.fixture(scope="session")
def metrics():
    import augur
    augur_app = augur.Application()
    return augur_app.metrics
