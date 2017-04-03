import os
import pytest
import pandas

@pytest.fixture
def publicwww():
    import ghdata
    key = os.getenv("PUBLIC_WWW_TEST_API_KEY")
    assert key is not None and len(key) >= 1
    return ghdata.PublicWWW(public_www_api_key=key)

def test_linking_websites(publicwww):
    assert publicwww.linking_websites(owner='yihui', repo='knitr').isin(["sohu.com"]).any