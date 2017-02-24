import os
import pytest

@pytest.fixture
def gh():
    import ghdata
    return ghdata.GHData(os.getenv("DB_TEST_URL"))

def test_repoid(gh):
    assert gh.repoid('rails', 'rails') == 78852

def test_userid(gh):
    assert gh.userid('howderek') == 417486