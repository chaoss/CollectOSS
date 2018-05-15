import os
import pytest
import pandas

@pytest.fixture
def publicwww():
    import augur
    augurApp = augur.Application()
    return augurApp.publicwww()

def test_linking_websites(publicwww):
    assert publicwww.linking_websites(owner='yihui', repo='knitr').isin(["sohu.com"]).any