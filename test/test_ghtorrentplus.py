import os
import pytest
import pandas

@pytest.fixture
def ghtorrentplus():
    import augur
    augurApp = augur.Application()
    return augurApp.ghtorrentplus()

# *** DIVERSITY AND INCLUSION *** #

# *** GROWTH, MATURITY, AND DECLINE *** #
def test_closed_issue_resolution_duration(ghtorrentplus):
    assert ghtorrentplus.closed_issue_resolution_duration('TEST', 'TEST').isin(["DATE"]).any

# *** RISK *** #

# *** VALUE *** #

# *** ACTIVITY *** #

# *** EXPERIMENTAL *** #
